"""
Composants de visualisation PyQt5
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QScrollArea, QGridLayout, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPainter, QColor, QPen
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import format_distance, format_cost, format_weight, format_percentage


class StatCard(QFrame):
    """Carte de statistique moderne avec effet de gradient"""
    
    def __init__(self, title, icon, color, parent=None):
        super().__init__(parent)
        self.color = color
        self.setMinimumHeight(140)
        self.setMinimumWidth(200)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        # En-tête avec icône
        header_layout = QHBoxLayout()
        
        # Icône
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        icon_label.setStyleSheet(f"color: {color};")
        header_layout.addWidget(icon_label)
        
        header_layout.addStretch()
        
        # Titre
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignRight)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title_label.setStyleSheet(f"color: #7f8c8d;")
        header_layout.addWidget(title_label)
        
        layout.addLayout(header_layout)
        
        # Valeur
        self.value_label = QLabel("--")
        self.value_label.setAlignment(Qt.AlignLeft)
        self.value_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(self.value_label)
        
        layout.addStretch()
        
        # Style avec ombre et gradient
        self.setStyleSheet(f"""
            StatCard {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 white, stop:1 {color}15);
                border: 2px solid {color}40;
                border-radius: 15px;
            }}
            StatCard:hover {{
                border: 2px solid {color};
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 white, stop:1 {color}25);
            }}
        """)
    
    def set_value(self, value):
        """Définit la valeur affichée"""
        self.value_label.setText(str(value))


class StatisticsPanel(QWidget):
    """Panneau de statistiques visuelles"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("📊 STATISTIQUES GLOBALES")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 20px; color: #2c3e50;")
        layout.addWidget(title)
        
        # Grille de cartes
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # Créer les cartes avec icônes
        self.cards = {}
        
        cards_config = [
            ('total_cost', 'Coût Total', '💰', '#e74c3c', 0, 0),
            ('total_distance', 'Distance Totale', '🛣️', '#3498db', 0, 1),
            ('trucks_used', 'Camions Utilisés', '🚛', '#27ae60', 0, 2),
            ('avg_capacity', 'Utilisation Moy.', '📊', '#f39c12', 1, 0),
            ('total_orders', 'Commandes', '📦', '#9b59b6', 1, 1),
            ('avg_orders', 'Moy. Commandes/Camion', '📈', '#1abc9c', 1, 2)
        ]
        
        for key, title, icon, color, row, col in cards_config:
            card = StatCard(title, icon, color)
            self.cards[key] = card
            grid.addWidget(card, row, col)
        
        layout.addLayout(grid)
        layout.addStretch()
    
    def update_statistics(self, stats):
        """Met à jour les statistiques"""
        if not stats:
            return
        
        self.cards['total_cost'].set_value(format_cost(stats.get('total_cost', 0)))
        self.cards['total_distance'].set_value(format_distance(stats.get('total_distance', 0)))
        self.cards['trucks_used'].set_value(f"{stats.get('trucks_used', 0)}/{stats.get('total_trucks', 0)}")
        self.cards['avg_capacity'].set_value(format_percentage(stats.get('avg_capacity_utilization', 0)))
        self.cards['total_orders'].set_value(str(stats.get('total_orders', 0)))
        self.cards['avg_orders'].set_value(f"{stats.get('avg_orders_per_truck', 0):.1f}")


class RouteCard(QFrame):
    """Carte moderne pour une tournée avec design amélioré"""
    
    def __init__(self, route_num, route, truck, driver, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # En-tête avec gradient
        header_widget = QWidget()
        header_widget.setFixedHeight(60)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Numéro de tournée avec badge
        badge = QLabel(f"#{route_num}")
        badge.setFont(QFont("Segoe UI", 20, QFont.Bold))
        badge.setStyleSheet("color: white;")
        header_layout.addWidget(badge)
        
        # Titre
        title = QLabel("TOURNÉE")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Icône de camion
        truck_icon = QLabel("🚛")
        truck_icon.setFont(QFont("Segoe UI Emoji", 24))
        header_layout.addWidget(truck_icon)
        
        # Couleur de l'en-tête selon le numéro
        colors = ['#3498db', '#e74c3c', '#27ae60', '#f39c12', '#9b59b6', '#1abc9c']
        header_color = colors[(route_num - 1) % len(colors)]
        header_widget.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {header_color}, stop:1 {header_color}dd);
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
            }}
        """)
        
        layout.addWidget(header_widget)
        
        # Contenu avec padding
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 15, 20, 15)
        content_layout.setSpacing(10)
        
        # Informations principales avec style moderne
        info_html = f"""
        <style>
            .info-row {{ margin: 8px 0; font-size: 11pt; }}
            .label {{ color: #7f8c8d; font-weight: bold; }}
            .value {{ color: #2c3e50; }}
            .route {{ color: #3498db; font-weight: bold; }}
        </style>
        <div class="info-row">
            <span class="label">🚛 Camion:</span> 
            <span class="value">{truck.name}</span> 
            <span style="color: #95a5a6;">({truck.truck_type.value})</span>
        </div>
        <div class="info-row">
            <span class="label">👨‍✈️ Chauffeur:</span> 
            <span class="value">{driver.name}</span>
        </div>
        <div class="info-row">
            <span class="label">🗺️ Itinéraire:</span><br>
            <span class="route">{' → '.join(route.get_stops())}</span>
        </div>
        """
        
        info_label = QLabel(info_html)
        info_label.setWordWrap(True)
        info_label.setTextFormat(Qt.RichText)
        content_layout.addWidget(info_label)
        
        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #ecf0f1;")
        content_layout.addWidget(separator)
        
        # Statistiques en grille
        stats_widget = QWidget()
        stats_layout = QGridLayout(stats_widget)
        stats_layout.setSpacing(10)
        
        stats_data = [
            ("📦", "Commandes", str(len(route.orders)), 0, 0),
            ("🛣️", "Distance", format_distance(route.total_distance), 0, 1),
            ("⚖️", "Poids", format_weight(route.total_weight), 1, 0),
            ("💰", "Coût", format_cost(route.total_cost), 1, 1),
            ("📊", "Capacité", format_percentage((route.total_weight/truck.capacity)*100), 2, 0)
        ]
        
        for icon, label, value, row, col in stats_data:
            stat_frame = QFrame()
            stat_layout = QVBoxLayout(stat_frame)
            stat_layout.setContentsMargins(10, 8, 10, 8)
            stat_layout.setSpacing(2)
            
            icon_label = QLabel(f"{icon} {label}")
            icon_label.setFont(QFont("Segoe UI", 9))
            icon_label.setStyleSheet("color: #7f8c8d;")
            stat_layout.addWidget(icon_label)
            
            value_label = QLabel(value)
            value_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
            value_label.setStyleSheet("color: #2c3e50;")
            stat_layout.addWidget(value_label)
            
            stat_frame.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border-radius: 8px;
                }
            """)
            
            stats_layout.addWidget(stat_frame, row, col)
        
        content_layout.addWidget(stats_widget)
        
        # Commandes avec style
        if route.orders:
            orders_title = QLabel("📋 Détails des Commandes")
            orders_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
            orders_title.setStyleSheet("color: #34495e; margin-top: 10px;")
            content_layout.addWidget(orders_title)
            
            for i, order in enumerate(route.orders, 1):
                order_frame = QFrame()
                order_layout = QHBoxLayout(order_frame)
                order_layout.setContentsMargins(10, 5, 10, 5)
                
                # Numéro
                num_label = QLabel(f"{i}")
                num_label.setFixedSize(25, 25)
                num_label.setAlignment(Qt.AlignCenter)
                num_label.setStyleSheet("""
                    background-color: #3498db;
                    color: white;
                    border-radius: 12px;
                    font-weight: bold;
                """)
                order_layout.addWidget(num_label)
                
                # Détails
                order_text = f"""
                <b>{order.id}</b>: {order.origin} → {order.destination}<br>
                <span style="color: #7f8c8d; font-size: 9pt;">
                {format_weight(order.weight)} • {order.order_type.value}
                </span>
                """
                order_label = QLabel(order_text)
                order_label.setTextFormat(Qt.RichText)
                order_layout.addWidget(order_label)
                
                order_frame.setStyleSheet("""
                    QFrame {
                        background-color: white;
                        border-left: 3px solid #3498db;
                        border-radius: 5px;
                        margin: 2px 0;
                    }
                """)
                
                content_layout.addWidget(order_frame)
        
        layout.addWidget(content)
        
        # Style global de la carte avec ombre
        self.setStyleSheet("""
            RouteCard {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            }
            RouteCard:hover {
                border: 1px solid #3498db;
            }
        """)


class RoutesPanel(QWidget):
    """Panneau de visualisation des tournées"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("🗺️ DÉTAILS DES TOURNÉES")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 20px; color: #2c3e50;")
        layout.addWidget(title)
        
        # Zone de scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(10)
        
        scroll.setWidget(self.scroll_content)
        layout.addWidget(scroll)
    
    def display_routes(self, routes, trucks, drivers):
        """Affiche les tournées"""
        # Nettoyer
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not routes:
            label = QLabel("Aucune tournée à afficher")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #7f8c8d; font-size: 14px; padding: 50px;")
            self.scroll_layout.addWidget(label)
            return
        
        # Afficher chaque tournée
        for i, route in enumerate(routes, 1):
            truck = next((t for t in trucks if t.id == route.truck_id), None)
            driver = next((d for d in drivers if d.id == route.driver_id), None)
            
            if truck and driver:
                card = RouteCard(i, route, truck, driver)
                self.scroll_layout.addWidget(card)
        
        self.scroll_layout.addStretch()


class ChartPanel(QWidget):
    """Panneau de graphiques"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("📈 COMPARAISON DES TOURNÉES")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 20px; color: #2c3e50;")
        layout.addWidget(title)
        
        # Canvas matplotlib
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
    
    def draw_chart(self, routes, trucks):
        """Dessine un graphique moderne et élégant"""
        self.figure.clear()
        
        if not routes:
            return
        
        # Style moderne
        self.figure.patch.set_facecolor('#f8f9fa')
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#ffffff')
        
        # Données
        distances = [route.total_distance for route in routes]
        costs = [route.total_cost for route in routes]
        labels = []
        for i, route in enumerate(routes, 1):
            truck = next((t for t in trucks if t.id == route.truck_id), None)
            truck_name = truck.name[:12] if truck else f"T{i}"
            labels.append(f"#{i}\n{truck_name}")
        
        # Couleurs avec gradient
        colors = ['#3498db', '#e74c3c', '#27ae60', '#f39c12', '#9b59b6', '#1abc9c']
        bar_colors = [colors[i % len(colors)] for i in range(len(routes))]
        
        # Position des barres
        x = range(len(routes))
        width = 0.7
        
        # Graphique en barres avec style moderne
        bars = ax.bar(x, distances, width, color=bar_colors, 
                      edgecolor='white', linewidth=2, alpha=0.9)
        
        # Ajouter un effet de gradient sur les barres
        for bar, color in zip(bars, bar_colors):
            bar.set_linewidth(0)
            # Ombre subtile
            ax.bar(bar.get_x(), bar.get_height(), bar.get_width(),
                  bottom=0, color=color, alpha=0.1, zorder=0)
        
        # Labels et titre avec style moderne
        ax.set_xlabel('Tournées', fontsize=13, fontweight='bold', color='#2c3e50', labelpad=10)
        ax.set_ylabel('Distance (km)', fontsize=13, fontweight='bold', color='#2c3e50', labelpad=10)
        ax.set_title('📊 Comparaison des Distances par Tournée', 
                    fontsize=15, fontweight='bold', color='#2c3e50', pad=20)
        
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=10, color='#34495e')
        ax.tick_params(axis='y', labelsize=10, colors='#7f8c8d')
        
        # Grille moderne
        ax.grid(axis='y', alpha=0.2, linestyle='--', linewidth=1, color='#bdc3c7')
        ax.set_axisbelow(True)
        
        # Supprimer les bordures
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#bdc3c7')
        ax.spines['bottom'].set_color('#bdc3c7')
        
        # Valeurs au-dessus des barres avec style
        for i, (bar, distance, cost) in enumerate(zip(bars, distances, costs)):
            height = bar.get_height()
            # Distance
            ax.text(bar.get_x() + bar.get_width()/2., height + max(distances)*0.02,
                   f'{distance:.0f} km',
                   ha='center', va='bottom', fontweight='bold', 
                   fontsize=10, color='#2c3e50')
            # Coût en dessous
            ax.text(bar.get_x() + bar.get_width()/2., height/2,
                   f'{cost:.0f} TND',
                   ha='center', va='center', fontweight='bold',
                   fontsize=9, color='white',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.3, edgecolor='none'))
        
        # Ajuster les marges
        ax.set_ylim(0, max(distances) * 1.15)
        
        self.figure.tight_layout()
        self.canvas.draw()
