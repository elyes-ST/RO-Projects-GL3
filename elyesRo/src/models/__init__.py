"""
Modèles de données pour le système de gestion de flotte
"""

from .truck import Truck, TruckType
from .driver import Driver
from .order import Order, OrderType
from .route import Route

__all__ = ['Truck', 'TruckType', 'Driver', 'Order', 'OrderType', 'Route']
