"""
Fonctions de validation des données
"""

import sys
import os

# Ajouter le chemin parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Truck, Driver, Order


def validate_truck(truck: Truck) -> tuple[bool, str]:
    """
    Valide un camion
    
    Returns:
        (is_valid, error_message)
    """
    if not truck.id or not truck.name:
        return False, "ID et nom requis"
    
    if truck.capacity <= 0:
        return False, "La capacité doit être positive"
    
    if truck.cost_per_km < 0:
        return False, "Le coût par km doit être positif"
    
    if truck.max_orders < 1:
        return False, "Le nombre maximum de commandes doit être au moins 1"
    
    if not truck.compatible_order_types:
        return False, "Au moins un type de commande compatible requis"
    
    return True, ""


def validate_driver(driver: Driver) -> tuple[bool, str]:
    """
    Valide un chauffeur
    
    Returns:
        (is_valid, error_message)
    """
    if not driver.id or not driver.name:
        return False, "ID et nom requis"
    
    if not driver.license_types:
        return False, "Au moins un type de permis requis"
    
    if driver.max_hours <= 0:
        return False, "Le nombre d'heures doit être positif"
    
    if driver.hourly_rate < 0:
        return False, "Le tarif horaire doit être positif"
    
    return True, ""


def validate_order(order: Order) -> tuple[bool, str]:
    """
    Valide une commande
    
    Returns:
        (is_valid, error_message)
    """
    if not order.id:
        return False, "ID requis"
    
    if not order.origin or not order.destination:
        return False, "Origine et destination requises"
    
    if order.weight <= 0:
        return False, "Le poids doit être positif"
    
    if order.distance <= 0:
        return False, "La distance doit être positive"
    
    if not 1 <= order.priority <= 5:
        return False, "La priorité doit être entre 1 et 5"
    
    if order.time_window_start >= order.time_window_end:
        return False, "La fenêtre de temps est invalide"
    
    return True, ""
