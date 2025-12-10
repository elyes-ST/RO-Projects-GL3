"""
Fonctions de formatage pour l'affichage
"""

from typing import List


def format_distance(distance: float) -> str:
    """Formate une distance en km"""
    return f"{distance:.1f} km"


def format_cost(cost: float) -> str:
    """Formate un coût en TND"""
    return f"{cost:.2f} TND"


def format_weight(weight: float) -> str:
    """Formate un poids en tonnes"""
    return f"{weight:.1f}t"


def format_route(stops: List[str]) -> str:
    """Formate une liste d'arrêts en chaîne"""
    return " → ".join(stops)


def format_percentage(value: float) -> str:
    """Formate un pourcentage"""
    return f"{value:.1f}%"


def format_hours(hours: float) -> str:
    """Formate des heures"""
    return f"{hours:.1f}h"
