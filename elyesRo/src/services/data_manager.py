"""
Gestionnaire de données pour charger et sauvegarder les données
"""

import json
import sys
import os
from typing import List, Dict

# Ajouter le chemin parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Truck, TruckType, Driver, Order, OrderType


class DataManager:
    """Gestionnaire de données"""
    
    @staticmethod
    def load_default_data() -> Dict:
        """
        Charge des données par défaut pour la démonstration
        
        Returns:
            Dictionnaire avec trucks, drivers, orders
        """
        # Camions par défaut
        trucks = [
            Truck(
                id="T001",
                name="Camion Standard 1",
                capacity=15.0,
                truck_type=TruckType.STANDARD,
                compatible_order_types=["Standard", "Fragile"],
                cost_per_km=0.5,
                max_orders=5
            ),
            Truck(
                id="T002",
                name="Camion Réfrigéré 1",
                capacity=20.0,
                truck_type=TruckType.REFRIGERE,
                compatible_order_types=["Alimentaire", "Réfrigéré"],
                cost_per_km=0.7,
                max_orders=4
            ),
            Truck(
                id="T003",
                name="Camion Standard 2",
                capacity=12.0,
                truck_type=TruckType.STANDARD,
                compatible_order_types=["Standard", "Fragile"],
                cost_per_km=0.5,
                max_orders=5
            ),
            Truck(
                id="T004",
                name="Camion Citerne",
                capacity=18.0,
                truck_type=TruckType.CITERNE,
                compatible_order_types=["Liquide"],
                cost_per_km=0.6,
                max_orders=3
            ),
            Truck(
                id="T005",
                name="Camion Plateau",
                capacity=15.0,
                truck_type=TruckType.PLATEAU,
                compatible_order_types=["Standard", "Fragile"],
                cost_per_km=0.5,
                max_orders=6
            )
        ]
        
        # Chauffeurs par défaut
        drivers = [
            Driver(
                id="D001",
                name="Ahmed Ben Ali",
                license_types=["B", "C"],
                max_hours=8.0,
                hourly_rate=15.0,
                available=True
            ),
            Driver(
                id="D002",
                name="Fatma Trabelsi",
                license_types=["B", "C", "CE"],
                max_hours=10.0,
                hourly_rate=18.0,
                available=True
            ),
            Driver(
                id="D003",
                name="Mohamed Gharbi",
                license_types=["B", "C"],
                max_hours=8.0,
                hourly_rate=15.0,
                available=True
            ),
            Driver(
                id="D004",
                name="Salma Karoui",
                license_types=["B", "C", "CE"],
                max_hours=9.0,
                hourly_rate=17.0,
                available=True
            ),
            Driver(
                id="D005",
                name="Karim Mansour",
                license_types=["B", "C"],
                max_hours=8.0,
                hourly_rate=16.0,
                available=True
            )
        ]
        
        # Commandes par défaut
        orders = [
            Order(
                id="O001",
                origin="Tunis",
                destination="Sfax",
                weight=8.0,
                order_type=OrderType.STANDARD,
                distance=270,
                priority=2
            ),
            Order(
                id="O002",
                origin="Tunis",
                destination="Sousse",
                weight=6.0,
                order_type=OrderType.FRAGILE,
                distance=140,
                priority=1
            ),
            Order(
                id="O003",
                origin="Sfax",
                destination="Gabès",
                weight=10.0,
                order_type=OrderType.ALIMENTAIRE,
                distance=150,
                priority=2
            ),
            Order(
                id="O004",
                origin="Sousse",
                destination="Monastir",
                weight=5.0,
                order_type=OrderType.STANDARD,
                distance=20,
                priority=3
            ),
            Order(
                id="O005",
                origin="Tunis",
                destination="Bizerte",
                weight=12.0,
                order_type=OrderType.STANDARD,
                distance=65,
                priority=1
            ),
            Order(
                id="O006",
                origin="Tunis",
                destination="Kairouan",
                weight=7.0,
                order_type=OrderType.REFRIGERE,
                distance=160,
                priority=2
            ),
            Order(
                id="O007",
                origin="Sfax",
                destination="Gafsa",
                weight=9.0,
                order_type=OrderType.LIQUIDE,
                distance=120,
                priority=3
            ),
            Order(
                id="O008",
                origin="Sousse",
                destination="Mahdia",
                weight=4.0,
                order_type=OrderType.FRAGILE,
                distance=50,
                priority=2
            )
        ]
        
        return {
            'trucks': trucks,
            'drivers': drivers,
            'orders': orders
        }
    
    @staticmethod
    def save_to_json(data: Dict, filename: str):
        """
        Sauvegarde les données en JSON
        
        Args:
            data: Dictionnaire de données
            filename: Nom du fichier
        """
        # Convertir les objets en dictionnaires
        json_data = {
            'trucks': [truck.to_dict() for truck in data.get('trucks', [])],
            'drivers': [driver.to_dict() for driver in data.get('drivers', [])],
            'orders': [order.to_dict() for order in data.get('orders', [])]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def load_from_json(filename: str) -> Dict:
        """
        Charge les données depuis un fichier JSON
        
        Args:
            filename: Nom du fichier
            
        Returns:
            Dictionnaire avec trucks, drivers, orders
        """
        with open(filename, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Convertir les dictionnaires en objets
        trucks = []
        for truck_data in json_data.get('trucks', []):
            truck = Truck(
                id=truck_data['id'],
                name=truck_data['name'],
                capacity=truck_data['capacity'],
                truck_type=TruckType(truck_data['truck_type']),
                compatible_order_types=truck_data['compatible_order_types'],
                cost_per_km=truck_data.get('cost_per_km', 0.5),
                max_orders=truck_data.get('max_orders', 5)
            )
            trucks.append(truck)
        
        drivers = []
        for driver_data in json_data.get('drivers', []):
            driver = Driver(
                id=driver_data['id'],
                name=driver_data['name'],
                license_types=driver_data['license_types'],
                max_hours=driver_data.get('max_hours', 8.0),
                hourly_rate=driver_data.get('hourly_rate', 15.0),
                available=driver_data.get('available', True)
            )
            drivers.append(driver)
        
        orders = []
        for order_data in json_data.get('orders', []):
            order = Order(
                id=order_data['id'],
                origin=order_data['origin'],
                destination=order_data['destination'],
                weight=order_data['weight'],
                order_type=OrderType(order_data['order_type']),
                distance=order_data['distance'],
                priority=order_data.get('priority', 3),
                time_window_start=order_data.get('time_window_start', 0.0),
                time_window_end=order_data.get('time_window_end', 24.0)
            )
            orders.append(order)
        
        return {
            'trucks': trucks,
            'drivers': drivers,
            'orders': orders
        }
