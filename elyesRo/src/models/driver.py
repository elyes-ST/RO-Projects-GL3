"""
Modèle pour les chauffeurs
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Driver:
    """
    Représente un chauffeur
    
    Attributes:
        id: Identifiant unique du chauffeur
        name: Nom complet du chauffeur
        license_types: Types de permis (B, C, CE, etc.)
        max_hours: Nombre maximum d'heures de conduite par jour
        hourly_rate: Tarif horaire (TND)
        available: Disponibilité du chauffeur
    """
    
    id: str
    name: str
    license_types: List[str]
    max_hours: float = 8.0
    hourly_rate: float = 15.0
    available: bool = True
    
    def __post_init__(self):
        """Validation après initialisation"""
        if self.max_hours <= 0:
            raise ValueError("Le nombre d'heures doit être positif")
        if self.hourly_rate < 0:
            raise ValueError("Le tarif horaire doit être positif")
    
    def can_drive_truck(self, truck_type: str) -> bool:
        """
        Vérifie si le chauffeur peut conduire ce type de camion
        
        Args:
            truck_type: Type de camion
            
        Returns:
            True si le chauffeur a le permis approprié
        """
        # Logique simplifiée : permis C pour tous les camions lourds
        return 'C' in self.license_types or 'CE' in self.license_types
    
    def __str__(self):
        return f"{self.name} (Permis: {', '.join(self.license_types)})"
    
    def to_dict(self):
        """Convertit en dictionnaire"""
        return {
            'id': self.id,
            'name': self.name,
            'license_types': self.license_types,
            'max_hours': self.max_hours,
            'hourly_rate': self.hourly_rate,
            'available': self.available
        }
