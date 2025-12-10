"""
Modèle pour les camions
"""

from enum import Enum
from dataclasses import dataclass
from typing import List


class TruckType(Enum):
    """Types de camions disponibles"""
    STANDARD = "Standard"
    REFRIGERE = "Réfrigéré"
    CITERNE = "Citerne"
    BENNE = "Benne"
    PLATEAU = "Plateau"


@dataclass
class Truck:
    """
    Représente un camion de la flotte
    
    Attributes:
        id: Identifiant unique du camion
        name: Nom du camion
        capacity: Capacité maximale en tonnes
        truck_type: Type de camion
        compatible_order_types: Types de commandes compatibles
        cost_per_km: Coût par kilomètre (TND)
        max_orders: Nombre maximum de commandes par tournée
    """
    
    id: str
    name: str
    capacity: float
    truck_type: TruckType
    compatible_order_types: List[str]
    cost_per_km: float = 0.5
    max_orders: int = 5
    
    def __post_init__(self):
        """Validation après initialisation"""
        if self.capacity <= 0:
            raise ValueError("La capacité doit être positive")
        if self.cost_per_km < 0:
            raise ValueError("Le coût par km doit être positif")
        if self.max_orders < 1:
            raise ValueError("Le nombre maximum de commandes doit être au moins 1")
    
    def can_handle_order(self, order_type: str) -> bool:
        """
        Vérifie si le camion peut transporter ce type de commande
        
        Args:
            order_type: Type de la commande
            
        Returns:
            True si compatible, False sinon
        """
        return order_type in self.compatible_order_types
    
    def __str__(self):
        return f"{self.name} ({self.truck_type.value}) - {self.capacity}t"
    
    def to_dict(self):
        """Convertit en dictionnaire"""
        return {
            'id': self.id,
            'name': self.name,
            'capacity': self.capacity,
            'truck_type': self.truck_type.value,
            'compatible_order_types': self.compatible_order_types,
            'cost_per_km': self.cost_per_km,
            'max_orders': self.max_orders
        }
