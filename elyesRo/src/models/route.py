"""
Modèle pour les tournées
"""

from dataclasses import dataclass, field
from typing import List
from .order import Order


@dataclass
class Route:
    """
    Représente une tournée (ensemble de commandes pour un camion)
    
    Attributes:
        truck_id: ID du camion assigné
        driver_id: ID du chauffeur assigné
        orders: Liste des commandes dans l'ordre de livraison
        total_distance: Distance totale de la tournée
        total_weight: Poids total transporté
        total_cost: Coût total de la tournée
    """
    
    truck_id: str
    driver_id: str
    orders: List[Order] = field(default_factory=list)
    total_distance: float = 0.0
    total_weight: float = 0.0
    total_cost: float = 0.0
    
    def add_order(self, order: Order):
        """Ajoute une commande à la tournée"""
        self.orders.append(order)
        self.total_distance += order.distance
        self.total_weight += order.weight
    
    def calculate_cost(self, cost_per_km: float, hourly_rate: float, avg_speed: float = 60.0):
        """
        Calcule le coût total de la tournée
        
        Args:
            cost_per_km: Coût par kilomètre
            hourly_rate: Tarif horaire du chauffeur
            avg_speed: Vitesse moyenne en km/h
        """
        # Coût du carburant/usure
        fuel_cost = self.total_distance * cost_per_km
        
        # Coût du chauffeur
        hours = self.total_distance / avg_speed
        driver_cost = hours * hourly_rate
        
        self.total_cost = fuel_cost + driver_cost
    
    def get_stops(self):
        """Retourne la liste des arrêts de la tournée dans l'ordre optimal"""
        if not self.orders:
            return []
        
        # Grouper les commandes par origine commune
        origins = {}
        for order in self.orders:
            if order.origin not in origins:
                origins[order.origin] = []
            origins[order.origin].append(order)
        
        # Construire l'itinéraire optimal
        stops = []
        visited_destinations = set()
        
        # Commencer par l'origine la plus fréquente (généralement le dépôt)
        start_origin = max(origins.keys(), key=lambda x: len(origins[x]))
        
        # Ajouter l'origine de départ
        stops.append(start_origin)
        
        # Traiter toutes les commandes de cette origine
        for order in origins[start_origin]:
            if order.destination not in visited_destinations:
                stops.append(order.destination)
                visited_destinations.add(order.destination)
        
        # Traiter les autres origines (si différentes du point de départ)
        for origin in origins:
            if origin != start_origin and origin not in stops:
                stops.append(origin)
                for order in origins[origin]:
                    if order.destination not in visited_destinations:
                        stops.append(order.destination)
                        visited_destinations.add(order.destination)
        
        return stops
    
    def __str__(self):
        stops = " → ".join(self.get_stops())
        return f"Tournée: {stops} ({len(self.orders)} commandes, {self.total_distance:.1f}km)"
    
    def to_dict(self):
        """Convertit en dictionnaire"""
        return {
            'truck_id': self.truck_id,
            'driver_id': self.driver_id,
            'orders': [order.to_dict() for order in self.orders],
            'total_distance': self.total_distance,
            'total_weight': self.total_weight,
            'total_cost': self.total_cost,
            'stops': self.get_stops()
        }
