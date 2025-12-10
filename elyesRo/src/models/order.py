"""
Modèle pour les commandes
"""

from enum import Enum
from dataclasses import dataclass


class OrderType(Enum):
    """Types de commandes"""
    STANDARD = "Standard"
    FRAGILE = "Fragile"
    ALIMENTAIRE = "Alimentaire"
    REFRIGERE = "Réfrigéré"
    LIQUIDE = "Liquide"
    DANGEREUX = "Dangereux"


@dataclass
class Order:
    """
    Représente une commande à livrer
    
    Attributes:
        id: Identifiant unique de la commande
        origin: Ville d'origine
        destination: Ville de destination
        weight: Poids en tonnes
        order_type: Type de commande
        distance: Distance en km
        priority: Priorité (1=haute, 5=basse)
        time_window_start: Heure de début de fenêtre (optionnel)
        time_window_end: Heure de fin de fenêtre (optionnel)
    """
    
    id: str
    origin: str
    destination: str
    weight: float
    order_type: OrderType
    distance: float
    priority: int = 3
    time_window_start: float = 0.0  # Heures
    time_window_end: float = 24.0   # Heures
    
    def __post_init__(self):
        """Validation après initialisation"""
        if self.weight <= 0:
            raise ValueError("Le poids doit être positif")
        if self.distance <= 0:
            raise ValueError("La distance doit être positive")
        if not 1 <= self.priority <= 5:
            raise ValueError("La priorité doit être entre 1 et 5")
        if self.time_window_start >= self.time_window_end:
            raise ValueError("La fenêtre de temps est invalide")
    
    def __str__(self):
        return f"{self.origin} → {self.destination} ({self.weight}t, {self.order_type.value})"
    
    def to_dict(self):
        """Convertit en dictionnaire"""
        return {
            'id': self.id,
            'origin': self.origin,
            'destination': self.destination,
            'weight': self.weight,
            'order_type': self.order_type.value,
            'distance': self.distance,
            'priority': self.priority,
            'time_window_start': self.time_window_start,
            'time_window_end': self.time_window_end
        }
