"""
Fenêtre principale PyQt5 avec CRUD et Visualisations
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QTableWidget, QTableWidgetItem, QPushButton,
                             QLabel, QMessageBox, QHeaderView, QTextEdit, QFrame,
                             QSplitter, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Truck, TruckType, Driver, Order, OrderType
from services import FleetOptimizer, DataManager
from utils import format_distance, format_cost, format_weight, format_route, format_percentage

from ui.forms_pyqt import TruckFormDialog, DriverFormDialog, OrderFormDialog
from ui.visualizations_pyqt import StatisticsPanel, RoutesPanel, ChartPanel


class FleetManagementAppPyQt(QMainWindow):
    """Application principale PyQt5 de gestion de flotte"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion de Flotte Avancée V2.0 - PyQt5")
        self.setGeometry(100, 100, 1600, 900)
        
        # Charger les données
        data = DataManager.load_default_data()
        self.trucks = data['trucks']
        self.drivers = data['drivers']
        self.orders = data['orders']
        self.solution = None
        
        # Configurer l'interface
        self.setup_ui()
        self.load_data()
        
        # Appliquer le style
        self.apply_style()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # En-tête
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Onglets
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        main_layout.addWidget(self.tabs)
        
        # Créer les onglets
        self.create_trucks_tab()
        self.create_drivers_tab()
        self.create_orders_tab()
        self.create_optimization_tab()
        self.create_results_tab()
    
    def create_header(self):
        """Crée l'en-tête de l'application"""
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(100)
        
        layout = QVBoxLayout(header)
        layout.setAlignment(Qt.AlignCenter)
        
        # Titre principal
        title = QLabel("🚛 GESTION DE FLOTTE AVANCÉE V2.0")
        title.setObjectName("mainTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Sous-titre
        subtitle = QLabel("CRUD Complet • Visualisations Élégantes • Optimisation Multi-Trajets")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        return header
    
    def create_trucks_tab(self):
        """Onglet des camions avec CRUD"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Barre d'outils
        toolbar = self.create_toolbar(
            "Camions",
            self.add_truck,
            self.edit_truck,
            self.delete_truck
        )
        layout.addWidget(toolbar)
        
        # Tableau
        self.trucks_table = QTableWidget()
        self.trucks_table.setColumnCount(7)
        self.trucks_table.setHorizontalHeaderLabels([
            'ID', 'Nom', 'Type', 'Capacité', 'Types Compatibles', 'Coût/km', 'Max Commandes'
        ])
        self.trucks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.trucks_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.trucks_table.setSelectionMode(QTableWidget.SingleSelection)
        self.trucks_table.doubleClicked.connect(self.edit_truck)
        layout.addWidget(self.trucks_table)
        
        self.tabs.addTab(tab, "🚛 Camions")
    
    def create_drivers_tab(self):
        """Onglet des chauffeurs avec CRUD"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Barre d'outils
        toolbar = self.create_toolbar(
            "Chauffeurs",
            self.add_driver,
            self.edit_driver,
            self.delete_driver
        )
        layout.addWidget(toolbar)
        
        # Tableau
        self.drivers_table = QTableWidget()
        self.drivers_table.setColumnCount(6)
        self.drivers_table.setHorizontalHeaderLabels([
            'ID', 'Nom', 'Permis', 'Max Heures', 'Tarif/h', 'Disponible'
        ])
        self.drivers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.drivers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.drivers_table.setSelectionMode(QTableWidget.SingleSelection)
        self.drivers_table.doubleClicked.connect(self.edit_driver)
        layout.addWidget(self.drivers_table)
        
        self.tabs.addTab(tab, "👨‍✈️ Chauffeurs")
    
    def create_orders_tab(self):
        """Onglet des commandes avec CRUD"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Barre d'outils
        toolbar = self.create_toolbar(
            "Commandes",
            self.add_order,
            self.edit_order,
            self.delete_order
        )
        layout.addWidget(toolbar)
        
        # Tableau
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(7)
        self.orders_table.setHorizontalHeaderLabels([
            'ID', 'Origine', 'Destination', 'Poids', 'Type', 'Distance', 'Priorité'
        ])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.orders_table.setSelectionMode(QTableWidget.SingleSelection)
        self.orders_table.doubleClicked.connect(self.edit_order)
        layout.addWidget(self.orders_table)
        
        self.tabs.addTab(tab, "📦 Commandes")
    
    def create_optimization_tab(self):
        """Onglet d'optimisation"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Titre
        title = QLabel("🎯 Optimisation de la Flotte")
        title.setStyleSheet("""
            font-size: 24pt;
            font-weight: bold;
            color: #2c3e50;
            padding: 20px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Carte d'information élégante
        info_card = QFrame()
        info_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
                padding: 25px;
            }
        """)
        info_layout = QVBoxLayout(info_card)
        
        # Titre de la carte
        info_title = QLabel("📊 Problème de Recherche Opérationnelle")
        info_title.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        """)
        info_layout.addWidget(info_title)
        
        # Description du problème
        problem_desc = QLabel(
            "Ce système résout un <b>VRP (Vehicle Routing Problem)</b> avec contraintes multiples "
            "en utilisant la <b>Programmation Linéaire en Nombres Entiers (PLNE)</b>.<br><br>"
            "🎯 <b>Objectif :</b> Minimiser le coût total de transport<br>"
            "⚙️ <b>Méthode :</b> Algorithme Branch & Bound (Gurobi)<br>"
            "📐 <b>Variables :</b> Affectations camion-chauffeur-commande<br>"
            "🔒 <b>Contraintes :</b> Capacité, compatibilité, permis, disponibilité"
        )
        problem_desc.setStyleSheet("""
            font-size: 11pt;
            color: white;
            line-height: 1.6;
            padding: 15px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        """)
        problem_desc.setWordWrap(True)
        info_layout.addWidget(problem_desc)
        
        # Statistiques en grille
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setSpacing(15)
        
        # Fonction pour créer une stat box
        def create_stat_box(icon, value_text, label_text):
            box = QFrame()
            box.setStyleSheet("""
                QFrame {
                    background: rgba(255, 255, 255, 0.15);
                    border-radius: 10px;
                    padding: 15px;
                }
            """)
            box_layout = QVBoxLayout(box)
            box_layout.setSpacing(5)
            
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 24pt; color: white;")
            icon_label.setAlignment(Qt.AlignCenter)
            box_layout.addWidget(icon_label)
            
            value = QLabel(value_text)
            value.setStyleSheet("font-size: 18pt; font-weight: bold; color: white;")
            value.setAlignment(Qt.AlignCenter)
            box_layout.addWidget(value)
            
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 9pt; color: rgba(255,255,255,0.9);")
            label.setAlignment(Qt.AlignCenter)
            label.setWordWrap(True)
            box_layout.addWidget(label)
            
            return box
        
        # Calculer dynamiquement le nombre de variables
        n_trucks = len(self.trucks)
        n_drivers = len(self.drivers)
        n_orders = len(self.orders)
        n_variables = (n_trucks * n_drivers * n_orders) + (n_trucks * n_drivers)
        
        stats_layout.addWidget(create_stat_box("🚛", str(n_trucks), "Camions\nDisponibles"))
        stats_layout.addWidget(create_stat_box("👨‍✈️", str(n_drivers), "Chauffeurs\nQualifiés"))
        stats_layout.addWidget(create_stat_box("📦", str(n_orders), "Commandes\nÀ Livrer"))
        stats_layout.addWidget(create_stat_box("🎲", str(n_variables), "Variables\nBinaires"))
        
        info_layout.addWidget(stats_widget)
        
        layout.addWidget(info_card)
        
        # Spacer
        layout.addSpacing(20)
        
        # Bouton d'optimisation
        optimize_btn = QPushButton("🚀 OPTIMISER LA FLOTTE")
        optimize_btn.setObjectName("optimizeButton")
        optimize_btn.setFixedSize(400, 80)
        optimize_btn.clicked.connect(self.optimize_fleet)
        layout.addWidget(optimize_btn, alignment=Qt.AlignCenter)
        
        # Informations complémentaires
        info_group = QGroupBox("💡 Fonctionnalités Avancées")
        info_group.setObjectName("infoGroup")
        info_layout2 = QVBoxLayout(info_group)
        
        info_text = """
<ul>
<li>✅ <b>Tournées multi-commandes</b> - Un camion peut livrer plusieurs commandes</li>
<li>✅ <b>Types de marchandises variés</b> - Standard, Réfrigéré, Liquide, Fragile</li>
<li>✅ <b>Camions spécialisés</b> - Chaque camion a ses types compatibles</li>
<li>✅ <b>Gestion des permis</b> - Vérification automatique des qualifications</li>
<li>✅ <b>Optimisation du coût</b> - Minimisation carburant + main d'œuvre</li>
<li>✅ <b>Diagnostic intelligent</b> - Analyse automatique des erreurs</li>
</ul>
        """
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setTextFormat(Qt.RichText)
        info_layout2.addWidget(info_label)
        
        layout.addWidget(info_group)
        
        # Spacer final
        layout.addStretch()
        
        self.tabs.addTab(tab, "🎯 Optimisation")
    
    def create_results_tab(self):
        """Onglet des résultats avec visualisations"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Sous-onglets pour les visualisations
        self.results_tabs = QTabWidget()
        
        # Statistiques
        self.stats_panel = StatisticsPanel()
        self.results_tabs.addTab(self.stats_panel, "📈 Statistiques")
        
        # Tournées
        self.routes_panel = RoutesPanel()
        self.results_tabs.addTab(self.routes_panel, "🗺️ Tournées")
        
        # Graphiques
        self.chart_panel = ChartPanel()
        self.results_tabs.addTab(self.chart_panel, "📊 Graphiques")
        
        # Détails texte
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Courier", 9))
        text_layout.addWidget(self.results_text)
        self.results_tabs.addTab(text_widget, "📄 Détails Texte")
        
        layout.addWidget(self.results_tabs)
        
        self.tabs.addTab(tab, "📊 Résultats & Visualisations")
    
    def create_toolbar(self, entity_name, add_func, edit_func, delete_func):
        """Crée une barre d'outils CRUD"""
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        toolbar.setFixedHeight(80)
        
        layout = QHBoxLayout(toolbar)
        layout.setSpacing(10)
        
        # Boutons avec taille fixe
        add_btn = QPushButton(f"➕ Ajouter")
        add_btn.setObjectName("addButton")
        add_btn.setMinimumHeight(50)
        add_btn.setMinimumWidth(120)
        add_btn.clicked.connect(add_func)
        layout.addWidget(add_btn)
        
        edit_btn = QPushButton(f"✏️ Modifier")
        edit_btn.setObjectName("editButton")
        edit_btn.setMinimumHeight(50)
        edit_btn.setMinimumWidth(120)
        edit_btn.clicked.connect(edit_func)
        layout.addWidget(edit_btn)
        
        delete_btn = QPushButton(f"🗑️ Supprimer")
        delete_btn.setObjectName("deleteButton")
        delete_btn.setMinimumHeight(50)
        delete_btn.setMinimumWidth(120)
        delete_btn.clicked.connect(delete_func)
        layout.addWidget(delete_btn)
        
        layout.addStretch()
        
        # Compteur - mapper les noms français aux attributs anglais
        entity_map = {
            'Camions': 'trucks',
            'Chauffeurs': 'drivers',
            'Commandes': 'orders'
        }
        attr_name = entity_map.get(entity_name, entity_name.lower())
        count = len(getattr(self, attr_name, []))
        
        count_label = QLabel(f"Total: {count} {entity_name.lower()}")
        count_label.setObjectName("countLabel")
        layout.addWidget(count_label)
        
        # Sauvegarder la référence au label pour mise à jour dynamique
        if entity_name == 'Camions':
            self.trucks_count_label = count_label
        elif entity_name == 'Chauffeurs':
            self.drivers_count_label = count_label
        elif entity_name == 'Commandes':
            self.orders_count_label = count_label
        
        return toolbar
    
    def update_toolbar_count(self, entity_name):
        """Met à jour le compteur dans la toolbar"""
        # Mapper les noms français aux attributs anglais
        entity_map = {
            'Camions': ('trucks', 'trucks_count_label'),
            'Chauffeurs': ('drivers', 'drivers_count_label'),
            'Commandes': ('orders', 'orders_count_label')
        }
        
        if entity_name not in entity_map:
            return
        
        attr_name, label_attr = entity_map[entity_name]
        
        # Vérifier que le label existe
        if hasattr(self, label_attr):
            count = len(getattr(self, attr_name, []))
            label = getattr(self, label_attr)
            label.setText(f"Total: {count} {entity_name.lower()}")
    
    # CRUD Camions
    def add_truck(self):
        """Ajoute un camion"""
        dialog = TruckFormDialog(self)
        if dialog.exec_():
            truck = dialog.get_truck()
            self.trucks.append(truck)
            self.refresh_trucks()
            QMessageBox.information(self, "Succès", f"Camion {truck.id} ajouté avec succès!")
    
    def edit_truck(self):
        """Modifie un camion"""
        row = self.trucks_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Sélectionnez un camion à modifier!")
            return
        
        truck = self.trucks[row]
        dialog = TruckFormDialog(self, truck)
        if dialog.exec_():
            updated_truck = dialog.get_truck()
            self.trucks[row] = updated_truck
            self.refresh_trucks()
            QMessageBox.information(self, "Succès", f"Camion {updated_truck.id} modifié avec succès!")
    
    def delete_truck(self):
        """Supprime un camion"""
        row = self.trucks_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Sélectionnez un camion à supprimer!")
            return
        
        truck = self.trucks[row]
        reply = QMessageBox.question(self, "Confirmation", 
                                     f"Supprimer le camion {truck.id} ?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            del self.trucks[row]
            self.refresh_trucks()
            QMessageBox.information(self, "Succès", "Camion supprimé!")
    
    # CRUD Chauffeurs
    def add_driver(self):
        """Ajoute un chauffeur"""
        dialog = DriverFormDialog(self)
        if dialog.exec_():
            driver = dialog.get_driver()
            self.drivers.append(driver)
            self.refresh_drivers()
            QMessageBox.information(self, "Succès", f"Chauffeur {driver.id} ajouté avec succès!")
    
    def edit_driver(self):
        """Modifie un chauffeur"""
        row = self.drivers_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Sélectionnez un chauffeur à modifier!")
            return
        
        driver = self.drivers[row]
        dialog = DriverFormDialog(self, driver)
        if dialog.exec_():
            updated_driver = dialog.get_driver()
            self.drivers[row] = updated_driver
            self.refresh_drivers()
            QMessageBox.information(self, "Succès", f"Chauffeur {updated_driver.id} modifié avec succès!")
    
    def delete_driver(self):
        """Supprime un chauffeur"""
        row = self.drivers_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Sélectionnez un chauffeur à supprimer!")
            return
        
        driver = self.drivers[row]
        reply = QMessageBox.question(self, "Confirmation", 
                                     f"Supprimer le chauffeur {driver.id} ?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            del self.drivers[row]
            self.refresh_drivers()
            QMessageBox.information(self, "Succès", "Chauffeur supprimé!")
    
    # CRUD Commandes
    def add_order(self):
        """Ajoute une commande"""
        dialog = OrderFormDialog(self)
        if dialog.exec_():
            order = dialog.get_order()
            self.orders.append(order)
            self.refresh_orders()
            QMessageBox.information(self, "Succès", f"Commande {order.id} ajoutée avec succès!")
    
    def edit_order(self):
        """Modifie une commande"""
        row = self.orders_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Sélectionnez une commande à modifier!")
            return
        
        order = self.orders[row]
        dialog = OrderFormDialog(self, order)
        if dialog.exec_():
            updated_order = dialog.get_order()
            self.orders[row] = updated_order
            self.refresh_orders()
            QMessageBox.information(self, "Succès", f"Commande {updated_order.id} modifiée avec succès!")
    
    def delete_order(self):
        """Supprime une commande"""
        row = self.orders_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Sélectionnez une commande à supprimer!")
            return
        
        order = self.orders[row]
        reply = QMessageBox.question(self, "Confirmation", 
                                     f"Supprimer la commande {order.id} ?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            del self.orders[row]
            self.refresh_orders()
            QMessageBox.information(self, "Succès", "Commande supprimée!")
    
    # Refresh
    def refresh_trucks(self):
        """Rafraîchit l'affichage des camions"""
        self.trucks_table.setRowCount(len(self.trucks))
        for i, truck in enumerate(self.trucks):
            self.trucks_table.setItem(i, 0, QTableWidgetItem(truck.id))
            self.trucks_table.setItem(i, 1, QTableWidgetItem(truck.name))
            self.trucks_table.setItem(i, 2, QTableWidgetItem(truck.truck_type.value))
            self.trucks_table.setItem(i, 3, QTableWidgetItem(f"{truck.capacity}t"))
            self.trucks_table.setItem(i, 4, QTableWidgetItem(", ".join(truck.compatible_order_types)))
            self.trucks_table.setItem(i, 5, QTableWidgetItem(f"{truck.cost_per_km} TND"))
            self.trucks_table.setItem(i, 6, QTableWidgetItem(str(truck.max_orders)))
        
        # Mettre à jour le compteur dans la toolbar
        self.update_toolbar_count('Camions')
        
        # Rafraîchir l'onglet optimisation
        self.refresh_optimization_tab()
    
    def refresh_drivers(self):
        """Rafraîchit l'affichage des chauffeurs"""
        self.drivers_table.setRowCount(len(self.drivers))
        for i, driver in enumerate(self.drivers):
            self.drivers_table.setItem(i, 0, QTableWidgetItem(driver.id))
            self.drivers_table.setItem(i, 1, QTableWidgetItem(driver.name))
            # Afficher les permis
            license_display = ", ".join(driver.license_types) if hasattr(driver, 'license_types') else "N/A"
            self.drivers_table.setItem(i, 2, QTableWidgetItem(license_display))
            # Types de camions qu'il peut conduire (basé sur ses permis)
            can_drive_display = "Tous" if 'C' in driver.license_types or 'CE' in driver.license_types else "Légers"
            self.drivers_table.setItem(i, 3, QTableWidgetItem(can_drive_display))
            self.drivers_table.setItem(i, 4, QTableWidgetItem(f"{driver.hourly_rate} TND"))
            self.drivers_table.setItem(i, 5, QTableWidgetItem("✅ Oui" if driver.available else "❌ Non"))
        
        # Mettre à jour le compteur dans la toolbar
        self.update_toolbar_count('Chauffeurs')
        
        # Rafraîchir l'onglet optimisation
        self.refresh_optimization_tab()
    
    def refresh_orders(self):
        """Rafraîchit l'affichage des commandes"""
        self.orders_table.setRowCount(len(self.orders))
        for i, order in enumerate(self.orders):
            self.orders_table.setItem(i, 0, QTableWidgetItem(order.id))
            self.orders_table.setItem(i, 1, QTableWidgetItem(order.origin))
            self.orders_table.setItem(i, 2, QTableWidgetItem(order.destination))
            self.orders_table.setItem(i, 3, QTableWidgetItem(f"{order.weight}t"))
            self.orders_table.setItem(i, 4, QTableWidgetItem(order.order_type.value))
            self.orders_table.setItem(i, 5, QTableWidgetItem(f"{order.distance} km"))
            self.orders_table.setItem(i, 6, QTableWidgetItem(str(order.priority)))
        
        # Mettre à jour le compteur dans la toolbar
        self.update_toolbar_count('Commandes')
        
        # Rafraîchir l'onglet optimisation
        self.refresh_optimization_tab()
    
    def load_data(self):
        """Charge les données initiales"""
        self.refresh_trucks()
        self.refresh_drivers()
        self.refresh_orders()
    
    def refresh_optimization_tab(self):
        """Rafraîchit les statistiques dans l'onglet optimisation"""
        # Recréer l'onglet optimisation avec les nouvelles données
        # Trouver l'index de l'onglet optimisation
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == "🎯 Optimisation":
                # Supprimer l'ancien onglet
                old_tab = self.tabs.widget(i)
                self.tabs.removeTab(i)
                old_tab.deleteLater()
                
                # Créer le nouvel onglet
                self.create_optimization_tab()
                
                # Déplacer l'onglet à la bonne position (avant Résultats)
                # L'onglet est ajouté à la fin, on doit le déplacer
                last_index = self.tabs.count() - 1
                if last_index > i:
                    # Déplacer l'onglet de la fin vers la position i
                    tab_widget = self.tabs.widget(last_index)
                    tab_text = self.tabs.tabText(last_index)
                    self.tabs.removeTab(last_index)
                    self.tabs.insertTab(i, tab_widget, tab_text)
                break
    
    def optimize_fleet(self):
        """Lance l'optimisation"""
        try:
            # Validation des données
            if not self.trucks or not self.drivers or not self.orders:
                QMessageBox.critical(self, "❌ Erreur - Données Manquantes", 
                                   "Ajoutez au moins un camion, un chauffeur et une commande!")
                return
            
            # Créer l'optimiseur
            optimizer = FleetOptimizer(self.trucks, self.drivers, self.orders)
            
            # Résoudre
            QMessageBox.information(self, "⏳ Optimisation en cours", 
                                  "Résolution en cours...\nCela peut prendre quelques secondes.")
            self.solution = optimizer.optimize(verbose=False)
            
            # Afficher les résultats
            if self.solution['status'] == 'optimal':
                self.display_results(optimizer)
                self.tabs.setCurrentIndex(4)  # Aller à l'onglet résultats
                QMessageBox.information(self, "✅ Succès", "Optimisation terminée avec succès!")
            elif self.solution['status'] == 'infeasible':
                self.display_infeasible_error()
            else:
                error_msg = self.solution.get('error', 'Erreur inconnue')
                self.display_optimization_error(error_msg)
            
        except Exception as e:
            self.display_optimization_error(str(e))
    
    def display_results(self, optimizer):
        """Affiche les résultats avec visualisations"""
        stats = optimizer.get_statistics(self.solution)
        
        # Mettre à jour les visualisations
        self.stats_panel.update_statistics(stats)
        self.routes_panel.display_routes(self.solution['routes'], self.trucks, self.drivers)
        self.chart_panel.draw_chart(self.solution['routes'], self.trucks)
        
        # Afficher les détails texte
        self.display_text_results(optimizer, stats)
    
    def display_text_results(self, optimizer, stats):
        """Affiche les résultats en format texte"""
        output = []
        output.append("="*80)
        output.append("RÉSULTATS DE L'OPTIMISATION")
        output.append("="*80)
        output.append("")
        output.append("✅ SOLUTION OPTIMALE TROUVÉE")
        output.append("")
        
        # Statistiques
        output.append("="*80)
        output.append("STATISTIQUES GLOBALES")
        output.append("="*80)
        output.append(f"Coût total minimal: {format_cost(stats['total_cost'])}")
        output.append(f"Distance totale: {format_distance(stats['total_distance'])}")
        output.append(f"Poids total transporté: {format_weight(stats['total_weight'])}")
        output.append(f"Camions utilisés: {stats['trucks_used']}/{stats['total_trucks']}")
        output.append(f"Chauffeurs utilisés: {stats['trucks_used']}/{stats['total_drivers']}")
        output.append(f"Commandes livrées: {stats['total_orders']}/{len(self.orders)}")
        output.append(f"Moyenne commandes/camion: {stats['avg_orders_per_truck']:.1f}")
        output.append(f"Moyenne distance/camion: {format_distance(stats['avg_distance_per_truck'])}")
        output.append(f"Utilisation moyenne capacité: {format_percentage(stats['avg_capacity_utilization'])}")
        output.append("")
        
        # Détails des tournées
        output.append("="*80)
        output.append("DÉTAILS DES TOURNÉES")
        output.append("="*80)
        output.append("")
        
        for i, route in enumerate(self.solution['routes'], 1):
            truck = next(t for t in self.trucks if t.id == route.truck_id)
            driver = next(d for d in self.drivers if d.id == route.driver_id)
            
            output.append(f"TOURNÉE #{i}")
            output.append("-" * 80)
            output.append(f"Camion: {truck.name} ({truck.truck_type.value})")
            output.append(f"Chauffeur: {driver.name}")
            output.append(f"Itinéraire: {format_route(route.get_stops())}")
            output.append(f"Nombre de commandes: {len(route.orders)}")
            output.append(f"Distance totale: {format_distance(route.total_distance)}")
            output.append(f"Poids total: {format_weight(route.total_weight)}")
            output.append(f"Utilisation capacité: {format_percentage((route.total_weight/truck.capacity)*100)}")
            output.append(f"Coût de la tournée: {format_cost(route.total_cost)}")
            output.append("")
            
            output.append("Commandes dans cette tournée:")
            for j, order in enumerate(route.orders, 1):
                output.append(f"  {j}. {order.id}: {order.origin} → {order.destination}")
                output.append(f"     Type: {order.order_type.value}, Poids: {format_weight(order.weight)}, Distance: {format_distance(order.distance)}")
            
            output.append("")
        
        output.append("="*80)
        
        self.results_text.setPlainText("\n".join(output))
    
    def display_infeasible_error(self):
        """Affiche une erreur détaillée quand le problème est infaisable"""
        # Analyser les causes possibles
        causes = []
        
        # Vérifier les capacités
        total_weight = sum(order.weight for order in self.orders)
        total_capacity = sum(truck.capacity for truck in self.trucks)
        if total_weight > total_capacity:
            causes.append(f"⚖️ Capacité insuffisante:\n   Poids total: {total_weight}t\n   Capacité totale: {total_capacity}t")
        
        # Vérifier les compatibilités
        incompatible_orders = []
        for order in self.orders:
            compatible_trucks = [t for t in self.trucks if order.order_type.value in t.compatible_order_types]
            if not compatible_trucks:
                incompatible_orders.append(f"   • {order.id} ({order.order_type.value})")
        
        if incompatible_orders:
            causes.append(f"🚫 Commandes sans camion compatible:\n" + "\n".join(incompatible_orders))
        
        # Vérifier les chauffeurs
        available_drivers = [d for d in self.drivers if d.available]
        if len(available_drivers) == 0:
            causes.append("👨‍✈️ Aucun chauffeur disponible")
        elif len(available_drivers) < len(self.orders):
            causes.append(f"👨‍✈️ Pas assez de chauffeurs:\n   Disponibles: {len(available_drivers)}\n   Commandes: {len(self.orders)}")
        
        # Vérifier les permis
        drivers_with_c = [d for d in self.drivers if 'C' in d.license_types or 'CE' in d.license_types]
        if len(drivers_with_c) == 0 and len(self.trucks) > 0:
            causes.append("🪪 Aucun chauffeur avec permis C/CE pour les camions")
        
        # Construire le message
        error_msg = "❌ PROBLÈME INFAISABLE\n\n"
        error_msg += "L'optimisation ne peut pas trouver de solution.\n\n"
        error_msg += "📋 CAUSES POSSIBLES:\n\n"
        
        if causes:
            error_msg += "\n\n".join(causes)
        else:
            error_msg += "• Contraintes trop strictes\n"
            error_msg += "• Nombre de commandes > capacité totale\n"
            error_msg += "• Incompatibilité types marchandises/camions"
        
        error_msg += "\n\n💡 SOLUTIONS:\n\n"
        error_msg += "1. Ajoutez plus de camions\n"
        error_msg += "2. Ajoutez plus de chauffeurs avec permis C\n"
        error_msg += "3. Vérifiez les types de marchandises compatibles\n"
        error_msg += "4. Augmentez la capacité des camions\n"
        error_msg += "5. Réduisez le nombre de commandes"
        
        # Afficher dans une boîte de dialogue détaillée
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("❌ Optimisation Impossible")
        msg_box.setText("Le problème est INFAISABLE")
        msg_box.setDetailedText(error_msg)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Augmenter la taille de la fenêtre
        msg_box.setStyleSheet("""
            QMessageBox {
                min-width: 600px;
                min-height: 400px;
            }
            QMessageBox QLabel {
                min-width: 550px;
                font-size: 11pt;
            }
            QTextEdit {
                min-width: 700px;
                min-height: 500px;
                font-size: 10pt;
                font-family: 'Segoe UI', Arial;
            }
        """)
        
        msg_box.exec_()
        
        # Afficher aussi dans l'onglet résultats
        self.results_text.setPlainText(error_msg)
        self.tabs.setCurrentIndex(4)
    
    def display_optimization_error(self, error_message):
        """Affiche une erreur d'optimisation avec détails"""
        error_msg = f"""
❌ ERREUR LORS DE L'OPTIMISATION

Une erreur s'est produite pendant la résolution du problème.

📋 DÉTAILS DE L'ERREUR:
{error_message}

📊 ÉTAT ACTUEL:
• Camions: {len(self.trucks)}
• Chauffeurs: {len(self.drivers)}
• Commandes: {len(self.orders)}

💡 VÉRIFICATIONS:
1. Tous les camions ont une capacité > 0
2. Tous les chauffeurs ont un tarif horaire > 0
3. Toutes les commandes ont un poids > 0
4. Les types de marchandises sont compatibles
5. Au moins un chauffeur a le permis C ou CE

🔧 ACTIONS RECOMMANDÉES:
• Vérifiez les données saisies
• Assurez-vous d'avoir assez de ressources
• Consultez les logs pour plus de détails
        """
        
        # Afficher dans une boîte de dialogue
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("❌ Erreur d'Optimisation")
        msg_box.setText("Une erreur s'est produite")
        msg_box.setDetailedText(error_msg)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Augmenter la taille de la fenêtre
        msg_box.setStyleSheet("""
            QMessageBox {
                min-width: 600px;
                min-height: 400px;
            }
            QMessageBox QLabel {
                min-width: 550px;
                font-size: 11pt;
            }
            QTextEdit {
                min-width: 700px;
                min-height: 500px;
                font-size: 10pt;
                font-family: 'Segoe UI', Arial;
            }
        """)
        
        msg_box.exec_()
        
        # Afficher aussi dans l'onglet résultats
        self.results_text.setPlainText(error_msg)
        self.tabs.setCurrentIndex(4)
    
    def apply_style(self):
        """Applique le style CSS à l'application"""
        style = """
        QMainWindow {
            background-color: #f0f0f0;
        }
        
        #header {
            background-color: #2c3e50;
        }
        
        #mainTitle {
            color: white;
            font-size: 24px;
            font-weight: bold;
            padding: 10px;
        }
        
        #subtitle {
            color: #ecf0f1;
            font-size: 12px;
            padding: 5px;
        }
        
        #toolbar {
            background-color: #ecf0f1;
            padding: 10px;
        }
        
        #addButton {
            background-color: #27ae60;
            color: white;
            font-weight: bold;
            padding: 15px 25px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
        }
        
        #addButton:hover {
            background-color: #229954;
        }
        
        #editButton {
            background-color: #3498db;
            color: white;
            font-weight: bold;
            padding: 15px 25px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
        }
        
        #editButton:hover {
            background-color: #2980b9;
        }
        
        #deleteButton {
            background-color: #e74c3c;
            color: white;
            font-weight: bold;
            padding: 15px 25px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
        }
        
        #deleteButton:hover {
            background-color: #c0392b;
        }
        
        #countLabel {
            font-weight: bold;
            font-size: 14px;
            padding: 10px;
        }
        
        #optimizeButton {
            background-color: #3498db;
            color: white;
            font-size: 20px;
            font-weight: bold;
            border: none;
            border-radius: 10px;
        }
        
        #optimizeButton:hover {
            background-color: #2980b9;
        }
        
        #infoGroup {
            font-size: 11px;
            padding: 20px;
        }
        
        QTableWidget {
            background-color: white;
            alternate-background-color: #f9f9f9;
            selection-background-color: #3498db;
            gridline-color: #ddd;
        }
        
        QTableWidget::item {
            padding: 5px;
        }
        
        QHeaderView::section {
            background-color: #34495e;
            color: white;
            padding: 8px;
            font-weight: bold;
            border: none;
        }
        
        QTabWidget::pane {
            border: 1px solid #ddd;
            background-color: white;
        }
        
        QTabBar::tab {
            background-color: #ecf0f1;
            color: #2c3e50;
            padding: 10px 20px;
            margin-right: 2px;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
        }
        
        QTabBar::tab:selected {
            background-color: white;
            font-weight: bold;
        }
        
        QTabBar::tab:hover {
            background-color: #d5dbdb;
        }
        """
        
        self.setStyleSheet(style)
