"""
Service d'optimisation de la flotte avec Gurobi
Supporte les tournées multi-commandes et les contraintes de compatibilité
"""

import gurobipy as gp
from gurobipy import GRB
from typing import List, Dict, Tuple
import sys
import os

# Ajouter le chemin parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Truck, Driver, Order, Route


class FleetOptimizer:
    """
    Optimiseur de flotte avec support des tournées multi-commandes
    """
    
    def __init__(self, trucks: List[Truck], drivers: List[Driver], orders: List[Order]):
        """
        Initialise l'optimiseur
        
        Args:
            trucks: Liste des camions disponibles
            drivers: Liste des chauffeurs disponibles
            orders: Liste des commandes à livrer
        """
        self.trucks = trucks
        self.drivers = drivers
        self.orders = orders
        self.model = None
        self.solution = None
    
    def optimize(self, verbose: bool = False) -> Dict:
        """
        Résout le problème d'optimisation
        
        Args:
            verbose: Afficher les détails de résolution
            
        Returns:
            Dictionnaire avec les résultats
        """
        try:
            # Créer le modèle
            self.model = gp.Model("fleet_optimization_advanced")
            
            if not verbose:
                self.model.setParam('OutputFlag', 0)
            
            n_trucks = len(self.trucks)
            n_drivers = len(self.drivers)
            n_orders = len(self.orders)
            
            # Variables de décision
            # x[t,d,o] = 1 si le camion t avec le chauffeur d prend la commande o
            x = self.model.addVars(
                n_trucks, n_drivers, n_orders,
                vtype=GRB.BINARY,
                name="assignment"
            )
            
            # y[t,d] = 1 si le camion t est utilisé avec le chauffeur d
            y = self.model.addVars(
                n_trucks, n_drivers,
                vtype=GRB.BINARY,
                name="truck_used"
            )
            
            # Fonction objectif: minimiser le coût total
            # Coût = distance * coût_par_km + temps * tarif_horaire
            obj = gp.LinExpr()
            
            for t in range(n_trucks):
                for d in range(n_drivers):
                    for o in range(n_orders):
                        truck = self.trucks[t]
                        driver = self.drivers[d]
                        order = self.orders[o]
                        
                        # Coût du carburant
                        fuel_cost = order.distance * truck.cost_per_km
                        
                        # Coût du chauffeur (estimé à 60 km/h)
                        time_hours = order.distance / 60.0
                        driver_cost = time_hours * driver.hourly_rate
                        
                        total_cost = fuel_cost + driver_cost
                        
                        obj += total_cost * x[t, d, o]
            
            self.model.setObjective(obj, GRB.MINIMIZE)
            
            # CONTRAINTES
            
            # 1. Chaque commande doit être assignée exactement une fois
            for o in range(n_orders):
                self.model.addConstr(
                    gp.quicksum(x[t, d, o] 
                               for t in range(n_trucks) 
                               for d in range(n_drivers)) == 1,
                    name=f"order_assigned_{o}"
                )
            
            # 2. Capacité des camions (peut prendre plusieurs commandes)
            for t in range(n_trucks):
                for d in range(n_drivers):
                    self.model.addConstr(
                        gp.quicksum(self.orders[o].weight * x[t, d, o] 
                                   for o in range(n_orders)) <= self.trucks[t].capacity,
                        name=f"capacity_{t}_{d}"
                    )
            
            # 3. Nombre maximum de commandes par camion
            for t in range(n_trucks):
                for d in range(n_drivers):
                    self.model.addConstr(
                        gp.quicksum(x[t, d, o] for o in range(n_orders)) <= self.trucks[t].max_orders,
                        name=f"max_orders_{t}_{d}"
                    )
            
            # 4. Compatibilité camion-commande (type de marchandise)
            for t in range(n_trucks):
                for d in range(n_drivers):
                    for o in range(n_orders):
                        truck = self.trucks[t]
                        order = self.orders[o]
                        
                        if not truck.can_handle_order(order.order_type.value):
                            self.model.addConstr(
                                x[t, d, o] == 0,
                                name=f"compatibility_{t}_{d}_{o}"
                            )
            
            # 5. Un chauffeur ne peut conduire qu'un seul camion
            for d in range(n_drivers):
                self.model.addConstr(
                    gp.quicksum(y[t, d] for t in range(n_trucks)) <= 1,
                    name=f"driver_one_truck_{d}"
                )
            
            # 6. Lien entre x et y (si un camion prend une commande, il est utilisé)
            for t in range(n_trucks):
                for d in range(n_drivers):
                    self.model.addConstr(
                        gp.quicksum(x[t, d, o] for o in range(n_orders)) <= n_orders * y[t, d],
                        name=f"link_xy_{t}_{d}"
                    )
            
            # 7. Disponibilité des chauffeurs
            for d in range(n_drivers):
                if not self.drivers[d].available:
                    for t in range(n_trucks):
                        self.model.addConstr(
                            y[t, d] == 0,
                            name=f"driver_unavailable_{d}"
                        )
            
            # 8. Permis du chauffeur compatible avec le camion
            for t in range(n_trucks):
                for d in range(n_drivers):
                    driver = self.drivers[d]
                    truck = self.trucks[t]
                    
                    if not driver.can_drive_truck(truck.truck_type.value):
                        self.model.addConstr(
                            y[t, d] == 0,
                            name=f"license_{t}_{d}"
                        )
            
            # Résoudre
            self.model.optimize()
            
            # Extraire les résultats
            if self.model.status == GRB.OPTIMAL:
                return self._extract_solution(x, y, n_trucks, n_drivers, n_orders)
            else:
                return {
                    'status': 'infeasible' if self.model.status == GRB.INFEASIBLE else 'error',
                    'routes': [],
                    'total_cost': None,
                    'total_distance': None
                }
        
        except gp.GurobiError as e:
            return {
                'status': 'error',
                'error': str(e),
                'routes': [],
                'total_cost': None,
                'total_distance': None
            }
    
    def _extract_solution(self, x, y, n_trucks, n_drivers, n_orders) -> Dict:
        """Extrait la solution du modèle"""
        routes = []
        total_cost = 0
        total_distance = 0
        trucks_used = 0
        
        # Grouper les commandes par camion et chauffeur
        assignments = {}
        
        for t in range(n_trucks):
            for d in range(n_drivers):
                if y[t, d].X > 0.5:
                    trucks_used += 1
                    truck = self.trucks[t]
                    driver = self.drivers[d]
                    
                    # Trouver toutes les commandes pour ce camion/chauffeur
                    route_orders = []
                    for o in range(n_orders):
                        if x[t, d, o].X > 0.5:
                            route_orders.append(self.orders[o])
                    
                    if route_orders:
                        # Créer la tournée
                        route = Route(truck_id=truck.id, driver_id=driver.id)
                        
                        for order in route_orders:
                            route.add_order(order)
                        
                        route.calculate_cost(truck.cost_per_km, driver.hourly_rate)
                        
                        routes.append(route)
                        total_cost += route.total_cost
                        total_distance += route.total_distance
        
        return {
            'status': 'optimal',
            'routes': routes,
            'total_cost': total_cost,
            'total_distance': total_distance,
            'trucks_used': trucks_used,
            'objective_value': self.model.ObjVal
        }
    
    def get_statistics(self, solution: Dict) -> Dict:
        """
        Calcule des statistiques sur la solution
        
        Args:
            solution: Solution retournée par optimize()
            
        Returns:
            Dictionnaire de statistiques
        """
        if solution['status'] != 'optimal':
            return {}
        
        routes = solution['routes']
        
        total_orders = sum(len(route.orders) for route in routes)
        total_weight = sum(route.total_weight for route in routes)
        
        avg_orders_per_truck = total_orders / len(routes) if routes else 0
        avg_distance_per_truck = solution['total_distance'] / len(routes) if routes else 0
        
        # Utilisation de la capacité
        capacity_utilization = []
        for route in routes:
            truck = next(t for t in self.trucks if t.id == route.truck_id)
            utilization = (route.total_weight / truck.capacity) * 100
            capacity_utilization.append(utilization)
        
        avg_capacity_utilization = sum(capacity_utilization) / len(capacity_utilization) if capacity_utilization else 0
        
        return {
            'total_orders': total_orders,
            'total_weight': total_weight,
            'trucks_used': solution['trucks_used'],
            'total_trucks': len(self.trucks),
            'total_drivers': len(self.drivers),
            'avg_orders_per_truck': avg_orders_per_truck,
            'avg_distance_per_truck': avg_distance_per_truck,
            'avg_capacity_utilization': avg_capacity_utilization,
            'total_cost': solution['total_cost'],
            'total_distance': solution['total_distance']
        }
