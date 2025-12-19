import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QLineEdit, QLabel, QHeaderView, QGroupBox,
    QProgressBar, QSpinBox, QDoubleSpinBox, QFileDialog, QSplitter
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon

# Import Matplotlib pour le diagramme de Gantt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.patches as mpatches

# Import du module Gurobi
from ModeleGurobi import resoudre_ordonnancement_avance 
import numpy as np
import json
from datetime import datetime


class MplCanvas(FigureCanvas):
    """Classe pour intégrer un graphique Matplotlib dans une fenêtre PyQt."""
    def __init__(self, parent=None, width=10, height=6, dpi=100):
        # Style moderne pour les graphiques
        plt.style.use('seaborn-v0_8-darkgrid')
        fig, self.axes = plt.subplots(figsize=(width, height), dpi=dpi, 
                                       facecolor='#2b2b2b')
        super(MplCanvas, self).__init__(fig)
        self.setParent(parent)
        self.fig = fig
        # Configuration du style sombre
        self.axes.set_facecolor('#1e1e1e')
        self.axes.tick_params(colors='white', which='both')
        self.axes.spines['bottom'].set_color('white')
        self.axes.spines['top'].set_color('white')
        self.axes.spines['left'].set_color('white')
        self.axes.spines['right'].set_color('white')


class ModernButton(QPushButton):
    """Bouton personnalisé avec style moderne."""
    def __init__(self, text, color="#4CAF50", icon_text=""):
        super().__init__()
        self.setText(f"{icon_text} {text}")
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color, 0.8)};
            }}
            QPushButton:disabled {{
                background-color: #555;
                color: #999;
            }}
        """)
    
    def _darken_color(self, color, factor=0.85):
        """Assombrir une couleur hex."""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(int(c * factor) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*rgb)


class StatsWidget(QWidget):
    """Widget pour afficher les statistiques de performance."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Titre
        title = QLabel("📊 Statistiques de Performance")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(title)
        
        # Grille de statistiques
        self.stats_labels = {}
        stats_layout = QVBoxLayout()
        
        stats = [
            ("cmax", "⏱️ Makespan (Cmax)", "N/A"),
            ("penalty", "⚠️ Coût Pénalité", "N/A"),
            ("total", "💰 Coût Total (Z)", "N/A"),
            ("utilization", "📈 Taux d'Utilisation", "N/A"),
            ("delays", "⏰ Retards Totaux", "N/A"),
        ]
        
        for key, label_text, default_value in stats:
            stat_frame = QGroupBox()
            stat_frame.setStyleSheet("""
                QGroupBox {
                    background-color: #2b2b2b;
                    border: 2px solid #3d3d3d;
                    border-radius: 8px;
                    padding: 10px;
                    margin-top: 5px;
                }
            """)
            stat_layout = QHBoxLayout(stat_frame)
            
            label = QLabel(label_text)
            label.setStyleSheet("color: #ccc; font-size: 13px;")
            
            value = QLabel(default_value)
            value.setStyleSheet("color: #4CAF50; font-size: 16px; font-weight: bold;")
            value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            stat_layout.addWidget(label)
            stat_layout.addWidget(value)
            
            self.stats_labels[key] = value
            stats_layout.addWidget(stat_frame)
        
        layout.addLayout(stats_layout)
        layout.addStretch()
    
    def update_stats(self, cmax, penalty, total, utilization, delays):
        """Met à jour les statistiques affichées."""
        self.stats_labels["cmax"].setText(f"{cmax:.2f}")
        self.stats_labels["penalty"].setText(f"{penalty:.0f}")
        self.stats_labels["total"].setText(f"{total:.2f}")
        self.stats_labels["utilization"].setText(f"{utilization:.1f}%")
        self.stats_labels["delays"].setText(f"{delays:.2f}")


class OrdonnancementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚚 Logistique Pro - Séquençage Intelligent des Camions")
        self.setGeometry(50, 50, 1600, 900)
        
        self.M = 2  # Nombre de quais initial
        self.N = 0  # Nombre de camions initial
        self.current_solution = None  # Stocker la solution actuelle
        
        # Appliquer le thème sombre
        self._apply_dark_theme()
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        self._setup_ui()
        self.add_truck_row()  # Ajout d'un camion par défaut
        
    def _apply_dark_theme(self):
        """Applique un thème sombre moderne à l'application."""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(45, 45, 45))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        
        self.setPalette(palette)
        
        # Style global
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 13px;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox {
                background-color: #2b2b2b;
                color: white;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #4CAF50;
            }
            QTableWidget {
                background-color: #2b2b2b;
                alternate-background-color: #323232;
                color: white;
                gridline-color: #3d3d3d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #4CAF50;
            }
            QHeaderView::section {
                background-color: #3d3d3d;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                background-color: #1e1e1e;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #2b2b2b;
                color: #aaa;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #3d3d3d;
                color: white;
            }
            QGroupBox {
                border: 2px solid #3d3d3d;
                border-radius: 8px;
                margin-top: 10px;
                font-weight: bold;
                color: #4CAF50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QMessageBox {
                background-color: #2b2b2b;
            }
            QProgressBar {
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                text-align: center;
                background-color: #2b2b2b;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
    def _setup_ui(self):
        """Configuration de l'interface utilisateur."""
        
        # --- En-tête avec titre et barre de statut ---
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🚚 Optimisation Logistique - PLNE Avancée")
        title_label.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #4CAF50;
            padding: 10px;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Indicateur de statut
        self.status_label = QLabel("⚪ Prêt")
        self.status_label.setStyleSheet("""
            font-size: 14px;
            padding: 8px 15px;
            background-color: #2b2b2b;
            border-radius: 5px;
            color: #aaa;
        """)
        header_layout.addWidget(self.status_label)
        
        self.layout.addLayout(header_layout)
        
        # --- Barre de contrôles principaux ---
        control_group = QGroupBox("⚙️ Paramètres Généraux")
        control_layout = QHBoxLayout(control_group)
        
        # Nombre de quais avec SpinBox
        control_layout.addWidget(QLabel("Quais (M):"))
        self.quais_input = QSpinBox()
        self.quais_input.setMinimum(1)
        self.quais_input.setMaximum(20)
        self.quais_input.setValue(self.M)
        self.quais_input.setFixedWidth(80)
        self.quais_input.setToolTip("Nombre de quais de chargement disponibles")
        self.quais_input.valueChanged.connect(self.update_tables_structure)
        control_layout.addWidget(self.quais_input)
        
        control_layout.addWidget(QLabel("Coût Pénalité (C_swap):"))
        self.cswap_input = QDoubleSpinBox()
        self.cswap_input.setMinimum(0)
        self.cswap_input.setMaximum(100000)
        self.cswap_input.setValue(1000)
        self.cswap_input.setFixedWidth(100)
        self.cswap_input.setToolTip("Coût unitaire pour affectations non autorisées")
        control_layout.addWidget(self.cswap_input)
        
        control_layout.addStretch()
        
        # Boutons d'action avec icônes
        self.add_camion_btn = ModernButton("Ajouter Camion", "#2196F3", "➕")
        self.add_camion_btn.setToolTip("Ajouter un nouveau camion à planifier")
        self.add_camion_btn.clicked.connect(self.add_truck_row)
        control_layout.addWidget(self.add_camion_btn)
        
        self.remove_camion_btn = ModernButton("Supprimer", "#f44336", "➖")
        self.remove_camion_btn.setToolTip("Supprimer le dernier camion")
        self.remove_camion_btn.clicked.connect(self.remove_truck_row)
        control_layout.addWidget(self.remove_camion_btn)
        
        self.clear_btn = ModernButton("Réinitialiser", "#FF9800", "🔄")
        self.clear_btn.setToolTip("Effacer toutes les données")
        self.clear_btn.clicked.connect(self.clear_all_data)
        control_layout.addWidget(self.clear_btn)
        
        self.layout.addWidget(control_group)
        
        # --- Barre d'action principale ---
        action_layout = QHBoxLayout()
        
        self.load_btn = ModernButton("Charger Exemple", "#9C27B0", "📂")
        self.load_btn.setToolTip("Charger un exemple de données")
        self.load_btn.clicked.connect(self.load_example_data)
        action_layout.addWidget(self.load_btn)
        
        self.save_btn = ModernButton("Sauvegarder", "#607D8B", "💾")
        self.save_btn.setToolTip("Sauvegarder les données actuelles")
        self.save_btn.clicked.connect(self.save_data)
        action_layout.addWidget(self.save_btn)
        
        action_layout.addStretch()
        
        self.optimize_btn = ModernButton("🚀 Lancer l'Optimisation", "#4CAF50")
        self.optimize_btn.setFixedHeight(50)
        self.optimize_btn.setMinimumWidth(250)
        self.optimize_btn.setToolTip("Résoudre le problème d'ordonnancement avec Gurobi")
        self.optimize_btn.clicked.connect(self.run_optimization)
        action_layout.addWidget(self.optimize_btn)
        
        self.layout.addLayout(action_layout)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.layout.addWidget(self.progress_bar)
        
        # --- Conteneur principal avec séparateur ---
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Partie gauche : Onglets
        self.tabs = QTabWidget()
        self.tab_input = QWidget()
        self.tab_results = QWidget()
        self.tab_gantt = QWidget()
        self.tab_charts = QWidget()
        self.tab_analysis = QWidget()
        
        self.tabs.addTab(self.tab_input, "📝 Saisie des Données")
        self.tabs.addTab(self.tab_results, "📊 Résultats & Métriques")
        self.tabs.addTab(self.tab_gantt, "📈 Diagramme de Gantt")
        self.tabs.addTab(self.tab_charts, "📊 Graphiques Détaillés")
        self.tabs.addTab(self.tab_analysis, "🔍 Analyse Avancée")
        
        self._setup_input_tab()
        self._setup_results_tab()
        self._setup_gantt_tab()
        self._setup_charts_tab()
        self._setup_analysis_tab()
        
        main_splitter.addWidget(self.tabs)
        
        # Partie droite : Statistiques
        self.stats_widget = StatsWidget()
        main_splitter.addWidget(self.stats_widget)
        
        main_splitter.setStretchFactor(0, 3)
        main_splitter.setStretchFactor(1, 1)
        
        self.layout.addWidget(main_splitter)
        
    def _setup_input_tab(self):
        """Configuration de l'onglet de saisie des données."""
        input_layout = QVBoxLayout(self.tab_input)
        input_layout.setSpacing(15)
        
        # Section propriétés des camions
        camions_group = QGroupBox("🚛 Propriétés des Camions")
        camions_layout = QVBoxLayout(camions_group)
        
        help_label = QLabel(
            "💡 <b>Aide:</b> p = Temps traitement, r = Date disponibilité, "
            "d = Date échéance, prep = Temps préparation"
        )
        help_label.setStyleSheet("color: #aaa; font-size: 12px; padding: 5px;")
        help_label.setWordWrap(True)
        camions_layout.addWidget(help_label)
        
        self.camions_table = QTableWidget()
        self.camions_table.setColumnCount(4)
        self.camions_table.setHorizontalHeaderLabels([
            "⏱️ Temps Traitement (p)", 
            "🕐 Date Dispo (r)", 
            "📅 Date Échéance (d)", 
            "🔧 Temps Prépa (prep)"
        ])
        self.camions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.camions_table.setAlternatingRowColors(True)
        camions_layout.addWidget(self.camions_table)
        
        input_layout.addWidget(camions_group)
        
        # Section affectations
        affectation_group = QGroupBox("🎯 Restrictions d'Affectation aux Quais")
        affectation_layout = QVBoxLayout(affectation_group)
        
        help_label2 = QLabel(
            "💡 <b>1</b> = Affectation autorisée | <b>0</b> = Affectation interdite"
        )
        help_label2.setStyleSheet("color: #aaa; font-size: 12px; padding: 5px;")
        affectation_layout.addWidget(help_label2)
        
        self.affectation_table = QTableWidget()
        self.affectation_table.setAlternatingRowColors(True)
        affectation_layout.addWidget(self.affectation_table)
        
        input_layout.addWidget(affectation_group)
        
    def _setup_results_tab(self):
        """Configuration de l'onglet des résultats."""
        results_layout = QVBoxLayout(self.tab_results)
        results_layout.setSpacing(15)
        
        # Métriques principales
        metrics_group = QGroupBox("📊 Métriques Optimales")
        metrics_layout = QVBoxLayout(metrics_group)
        
        self.metrics_label = QLabel("En attente de l'optimisation...")
        self.metrics_label.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            color: #4CAF50;
            padding: 15px;
            background-color: #2b2b2b;
            border-radius: 5px;
        """)
        self.metrics_label.setWordWrap(True)
        metrics_layout.addWidget(self.metrics_label)
        
        results_layout.addWidget(metrics_group)
        
        # Tableau détaillé
        details_group = QGroupBox("📋 Détails du Séquencement Optimal")
        details_layout = QVBoxLayout(details_group)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "🚛 Camion", 
            "🏭 Quai", 
            "⏰ Début (S)", 
            "⏱️ Fin (C)", 
            "⚠️ Retard (T)",
            "📊 Statut"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setAlternatingRowColors(True)
        details_layout.addWidget(self.results_table)
        
        results_layout.addWidget(details_group)
        
        # Bouton d'export
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        
        self.export_btn = ModernButton("Exporter les Résultats", "#00BCD4", "📤")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.export_results)
        export_layout.addWidget(self.export_btn)
        
        results_layout.addLayout(export_layout)
        
    def _setup_gantt_tab(self):
        """Configuration de l'onglet du diagramme de Gantt."""
        gantt_layout = QVBoxLayout(self.tab_gantt)
        gantt_layout.setSpacing(10)
        
        # Contrôles du graphique
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("🎨 Visualisation:"))
        
        self.refresh_gantt_btn = ModernButton("Actualiser", "#2196F3", "🔄")
        self.refresh_gantt_btn.setEnabled(False)
        self.refresh_gantt_btn.clicked.connect(self.refresh_gantt)
        controls_layout.addWidget(self.refresh_gantt_btn)
        
        controls_layout.addStretch()
        gantt_layout.addLayout(controls_layout)
        
        # Canvas Matplotlib
        self.sc = MplCanvas(self, width=12, height=7, dpi=100)
        gantt_layout.addWidget(self.sc)
        
    def _setup_charts_tab(self):
        """Configuration de l'onglet des graphiques détaillés."""
        charts_layout = QVBoxLayout(self.tab_charts)
        charts_layout.setSpacing(10)
        
        # Titre
        title = QLabel("📊 Visualisations Détaillées")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; padding: 10px;")
        charts_layout.addWidget(title)
        
        # Conteneur pour les graphiques
        charts_container = QSplitter(Qt.Vertical)
        
        # Graphique 1: Utilisation des quais
        self.chart1_canvas = MplCanvas(self, width=10, height=4, dpi=100)
        charts_container.addWidget(self.chart1_canvas)
        
        # Graphique 2: Distribution des retards
        self.chart2_canvas = MplCanvas(self, width=10, height=4, dpi=100)
        charts_container.addWidget(self.chart2_canvas)
        
        charts_layout.addWidget(charts_container)
        
    def _setup_analysis_tab(self):
        """Configuration de l'onglet d'analyse avancée."""
        analysis_layout = QVBoxLayout(self.tab_analysis)
        analysis_layout.setSpacing(10)
        
        # Titre
        title = QLabel("🔍 Analyse de Performance Avancée")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; padding: 10px;")
        analysis_layout.addWidget(title)
        
        # Conteneur pour les graphiques d'analyse
        analysis_container = QSplitter(Qt.Vertical)
        
        # Graphique 1: Temps par camion (barres)
        self.analysis1_canvas = MplCanvas(self, width=10, height=4, dpi=100)
        analysis_container.addWidget(self.analysis1_canvas)
        
        # Graphique 2: Charge de travail par quai (camembert)
        self.analysis2_canvas = MplCanvas(self, width=10, height=4, dpi=100)
        analysis_container.addWidget(self.analysis2_canvas)
        
        analysis_layout.addWidget(analysis_container)
        
    def update_tables_structure(self):
        """Met à jour les dimensions des tableaux de saisie."""
        try:
            self.M = self.quais_input.value()
        except:
            self.M = 2
            
        self.N = self.camions_table.rowCount()
        
        # Mise à jour du tableau d'affectation
        self.affectation_table.setRowCount(self.N)
        self.affectation_table.setColumnCount(self.M)
        
        quai_labels = [f"🏭 Quai {k+1}" for k in range(self.M)]
        self.affectation_table.setHorizontalHeaderLabels(quai_labels)
        
        for i in range(self.N):
            for k in range(self.M):
                item = self.affectation_table.item(i, k)
                if item is None:
                    item = QTableWidgetItem("1")
                    self.affectation_table.setItem(i, k, item)
                    
            self.camions_table.setVerticalHeaderItem(i, QTableWidgetItem(f"C{i+1}"))
            self.affectation_table.setVerticalHeaderItem(i, QTableWidgetItem(f"C{i+1}"))
            
        self.affectation_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
    def add_truck_row(self):
        """Ajoute une ligne de camion dans les tableaux."""
        current_row = self.camions_table.rowCount()
        self.camions_table.insertRow(current_row)
        
        default_values = ["10", "0", "20", "2"]
        for col, val in enumerate(default_values):
            self.camions_table.setItem(current_row, col, QTableWidgetItem(val))
            
        self.update_tables_structure()
        self.N = self.camions_table.rowCount()
        self._update_status("✅ Camion ajouté", "#4CAF50")
        
    def remove_truck_row(self):
        """Supprime la dernière ligne de camion."""
        current_row = self.camions_table.rowCount()
        
        if current_row > 0:
            self.camions_table.removeRow(current_row - 1)
            self.affectation_table.removeRow(current_row - 1)
            self.N = current_row - 1
            self.update_tables_structure()
            self._update_status("✅ Camion supprimé", "#FF9800")
        else:
            QMessageBox.information(self, "Information", "Aucun camion à supprimer.")
            
    def clear_all_data(self):
        """Efface toutes les données."""
        reply = QMessageBox.question(
            self, 
            "Confirmation",
            "Voulez-vous vraiment effacer toutes les données ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.camions_table.setRowCount(0)
            self.affectation_table.setRowCount(0)
            self.N = 0
            self.results_table.setRowCount(0)
            self.sc.axes.clear()
            self.sc.draw()
            self._update_status("🔄 Données effacées", "#f44336")
            
    def load_example_data(self):
        """Charge un exemple de données prédéfini."""
        # Effacer les données actuelles
        self.camions_table.setRowCount(0)
        self.N = 0
        
        # Configuration de l'exemple
        self.quais_input.setValue(3)
        
        # Ajouter 3 camions avec données d'exemple
        examples = [
            ["10", "0", "25", "2"],
            ["8", "5", "20", "1"],
            ["12", "0", "30", "3"],
        ]
        
        for data in examples:
            self.add_truck_row()
            row = self.camions_table.rowCount() - 1
            for col, val in enumerate(data):
                self.camions_table.setItem(row, col, QTableWidgetItem(val))
        
        # Restrictions d'exemple
        self.affectation_table.setItem(0, 2, QTableWidgetItem("0"))
        self.affectation_table.setItem(2, 0, QTableWidgetItem("0"))
        
        self._update_status("✅ Exemple chargé", "#4CAF50")
        QMessageBox.information(
            self, 
            "Exemple Chargé", 
            "Un exemple avec 3 camions et 3 quais a été chargé.\n\n"
            "Restrictions:\n"
            "• Camion 1 interdit sur Quai 3\n"
            "• Camion 3 interdit sur Quai 1"
        )
        
    def save_data(self):
        """Sauvegarde les données dans un fichier JSON."""
        if self.N == 0:
            QMessageBox.warning(self, "Attention", "Aucune donnée à sauvegarder.")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Sauvegarder les données", 
            f"logistique_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )
        
        if filename:
            data = self.get_input_data()
            if data:
                N, M, p, r, d, prep, a, C_swap = data
                save_dict = {
                    "N": N,
                    "M": M,
                    "p": p,
                    "r": r,
                    "d": d,
                    "prep": prep,
                    "a": a,
                    "C_swap": C_swap,
                    "timestamp": datetime.now().isoformat()
                }
                
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(save_dict, f, indent=2, ensure_ascii=False)
                    self._update_status("✅ Données sauvegardées", "#4CAF50")
                    QMessageBox.information(self, "Succès", f"Données sauvegardées dans:\n{filename}")
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde:\n{e}")
                    
    def export_results(self):
        """Exporte les résultats dans un fichier texte."""
        if not self.current_solution:
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter les résultats",
            f"resultats_optimisation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("=" * 70 + "\n")
                    f.write("RAPPORT D'OPTIMISATION LOGISTIQUE\n")
                    f.write("=" * 70 + "\n\n")
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"Nombre de camions: {self.N}\n")
                    f.write(f"Nombre de quais: {self.M}\n\n")
                    f.write(self.metrics_label.text().replace("<br>", "\n") + "\n\n")
                    f.write("-" * 70 + "\n")
                    f.write("DÉTAILS DU SÉQUENCEMENT\n")
                    f.write("-" * 70 + "\n\n")
                    
                    for sol in self.current_solution:
                        f.write(f"Camion {sol['Camion']}:\n")
                        f.write(f"  - Quai affecté: {sol['Quai']}\n")
                        f.write(f"  - Début chargement: {sol['Debut_Chargement']:.2f}\n")
                        f.write(f"  - Fin opération: {sol['Fin_Operation']:.2f}\n")
                        f.write(f"  - Retard: {sol['Retard']:.2f}\n\n")
                        
                self._update_status("✅ Résultats exportés", "#4CAF50")
                QMessageBox.information(self, "Succès", f"Résultats exportés dans:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export:\n{e}")
                
    def get_input_data(self):
        """Récupère et valide toutes les données d'entrée."""
        try:
            M = self.quais_input.value()
            C_swap = self.cswap_input.value()
            N = self.camions_table.rowCount()
            
            if N == 0 or M == 0:
                QMessageBox.warning(self, "Attention", "Veuillez ajouter au moins un camion et un quai.")
                return None
            
            p, r, d, prep = [], [], [], []
            a = np.zeros((N, M), dtype=int)
            
            for i in range(N):
                try:
                    p.append(float(self.camions_table.item(i, 0).text()))
                    r.append(float(self.camions_table.item(i, 1).text()))
                    d.append(float(self.camions_table.item(i, 2).text()))
                    prep.append(float(self.camions_table.item(i, 3).text()))
                except:
                    QMessageBox.critical(
                        self, 
                        "Erreur", 
                        f"Valeur invalide pour le camion {i+1}.\nVeuillez vérifier les données."
                    )
                    return None
            
            for i in range(N):
                for k in range(M):
                    try:
                        a[i, k] = int(self.affectation_table.item(i, k).text())
                    except:
                        a[i, k] = 1
                        
            return N, M, p, r, d, prep, a.tolist(), C_swap
        
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Erreur de Saisie", 
                f"Veuillez vérifier les valeurs.\nDétail: {e}"
            )
            return None
            
    def run_optimization(self):
        """Lance l'optimisation Gurobi et affiche les résultats."""
        data = self.get_input_data()
        if data is None:
            return
            
        N, M, p, r, d, prep, a, C_swap = data
        
        # Animation de la barre de progression
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Mode indéterminé
        self._update_status("⏳ Optimisation en cours...", "#FF9800")
        self.optimize_btn.setEnabled(False)
        
        QApplication.processEvents()
        
        # Appel du solveur
        Cmax_opt, P_cost_opt, solution = resoudre_ordonnancement_avance(
            N, M, p, r, d, prep, a, C_swap
        )
        
        self.progress_bar.setVisible(False)
        self.optimize_btn.setEnabled(True)
        
        if isinstance(solution, str):
            QMessageBox.critical(self, "Erreur Gurobi", solution)
            self._update_status("❌ Échec de l'optimisation", "#f44336")
            return
        
        self.current_solution = solution
        
        # Calcul des statistiques
        total_cost = Cmax_opt + C_swap * P_cost_opt
        total_delays = sum(s['Retard'] for s in solution)
        
        # Calcul du taux d'utilisation
        total_work = sum(p)
        total_available = Cmax_opt * M
        utilization = (total_work / total_available * 100) if total_available > 0 else 0
        
        # Mise à jour des métriques
        self.metrics_label.setText(
            f"<b>✅ OPTIMISATION RÉUSSIE</b><br><br>"
            f"<span style='font-size: 14px;'>"
            f"⏱️ Makespan (C<sub>max</sub>) = <b>{Cmax_opt:.2f}</b> unités<br>"
            f"⚠️ Coût Pénalité = <b>{P_cost_opt:.0f}</b><br>"
            f"💰 Coût Total (Z) = <b>{total_cost:.2f}</b><br>"
            f"📈 Taux d'Utilisation = <b>{utilization:.1f}%</b>"
            f"</span>"
        )
        
        # Mise à jour du widget de statistiques
        self.stats_widget.update_stats(Cmax_opt, P_cost_opt, total_cost, utilization, total_delays)
        
        # Mise à jour du tableau de résultats
        self.results_table.setRowCount(N)
        for i, res in enumerate(solution):
            # Déterminer le statut
            if res['Retard'] > 0:
                statut = "⚠️ Retard"
                statut_color = "#FF9800"
            else:
                statut = "✅ À temps"
                statut_color = "#4CAF50"
                
            items = [
                QTableWidgetItem(str(res['Camion'])),
                QTableWidgetItem(str(res['Quai'])),
                QTableWidgetItem(f"{res['Debut_Chargement']:.2f}"),
                QTableWidgetItem(f"{res['Fin_Operation']:.2f}"),
                QTableWidgetItem(f"{res['Retard']:.2f}"),
                QTableWidgetItem(statut)
            ]
            
            for col, item in enumerate(items):
                if col == 5:  # Colonne statut
                    item.setForeground(QColor(statut_color))
                self.results_table.setItem(i, col, item)
        
        # Génération du diagramme de Gantt
        self.draw_gantt(N, M, solution, d, r, prep)
        
        # Génération des graphiques détaillés
        self.draw_utilization_chart(N, M, solution, p)
        self.draw_delays_chart(N, solution, d)
        
        # Génération des graphiques d'analyse
        self.draw_timeline_chart(N, solution, p, r, prep)
        self.draw_workload_pie(N, M, solution, p)
        
        # Activer les boutons d'export
        self.export_btn.setEnabled(True)
        self.refresh_gantt_btn.setEnabled(True)
        
        self._update_status("✅ Optimisation terminée avec succès", "#4CAF50")
        self.tabs.setCurrentIndex(1)  # Passer à l'onglet résultats
        
    def refresh_gantt(self):
        """Actualise tous les diagrammes."""
        if self.current_solution:
            data = self.get_input_data()
            if data:
                N, M, p, r, d, prep, a, C_swap = data
                # Rafraîchir tous les graphiques
                self.draw_gantt(N, M, self.current_solution, d, r, prep)
                self.draw_utilization_chart(N, M, self.current_solution, p)
                self.draw_delays_chart(N, self.current_solution, d)
                self.draw_timeline_chart(N, self.current_solution, p, r, prep)
                self.draw_workload_pie(N, M, self.current_solution, p)
                self._update_status("🔄 Tous les graphiques actualisés", "#2196F3")
                
    def draw_gantt(self, N, M, solution, d, r, prep):
        """Dessine un diagramme de Gantt moderne et informatif."""
        self.sc.axes.clear()
        
        # Configuration du style
        colors = plt.cm.get_cmap('tab20', N)
        
        solution_sorted = sorted(solution, key=lambda x: (x['Quai'], x['Debut_Chargement']))
        
        legend_elements = []
        
        for i, res in enumerate(solution_sorted):
            camion_index = res['Camion'] - 1
            quai = res['Quai']
            start_op = res['Debut_Chargement']
            end_op = res['Fin_Operation']
            duration_chargement = end_op - start_op
            prep_time = prep[camion_index]
            prep_start = start_op - prep_time
            due_date = d[camion_index]
            
            color = colors(camion_index)
            
            # Barre de chargement principale
            bar = self.sc.axes.barh(
                quai, duration_chargement,
                left=start_op,
                height=0.7,
                color=color,
                alpha=0.9,
                edgecolor='white',
                linewidth=2
            )
            
            # Barre de préparation
            if prep_time > 0:
                self.sc.axes.barh(
                    quai, prep_time,
                    left=prep_start,
                    height=0.35,
                    color=color,
                    alpha=0.4,
                    edgecolor='white',
                    linewidth=1,
                    linestyle='--'
                )
            
            # Marque de deadline
            self.sc.axes.plot(
                [due_date, due_date], 
                [quai - 0.45, quai + 0.45],
                '--', 
                color='#FFC107', 
                linewidth=2.5, 
                alpha=0.8
            )
            
            # Marque de retard
            if end_op > due_date:
                self.sc.axes.barh(
                    quai, end_op - due_date,
                    left=due_date,
                    height=0.7,
                    color='none',
                    edgecolor='#f44336',
                    hatch='///',
                    linewidth=0,
                    alpha=0.6
                )
            
            # Label du camion
            self.sc.axes.text(
                start_op + duration_chargement / 2, quai,
                f'C{camion_index+1}',
                ha='center', va='center',
                color='white',
                fontsize=11,
                fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.3)
            )
            
            # Légende
            if camion_index not in [le.get_label() for le in legend_elements]:
                legend_elements.append(
                    mpatches.Patch(color=color, label=f'Camion {camion_index+1}')
                )
        
        # Configuration des axes
        self.sc.axes.set_yticks(np.arange(1, M + 1))
        self.sc.axes.set_yticklabels([f'🏭 Quai {k+1}' for k in range(M)])
        self.sc.axes.set_xlabel("Temps (unités)", color='white', fontsize=12, fontweight='bold')
        self.sc.axes.set_ylabel("Quais de Chargement", color='white', fontsize=12, fontweight='bold')
        self.sc.axes.set_title(
            "📊 Diagramme de Gantt - Séquencement Optimal", 
            color='white', 
            fontsize=14, 
            fontweight='bold',
            pad=20
        )
        self.sc.axes.grid(axis='x', linestyle='--', alpha=0.3, color='white')
        
        # Légende
        if legend_elements:
            self.sc.axes.legend(
                handles=legend_elements,
                loc='upper right',
                facecolor='#2b2b2b',
                edgecolor='white',
                fontsize=10
            )
        
        # Ajustement des limites
        all_starts = [res['Debut_Chargement'] for res in solution_sorted]
        start_min = min(all_starts) if all_starts else 0
        self.sc.axes.set_xlim(left=max(0, start_min - 5))
        
        self.sc.fig.tight_layout()
        self.sc.draw()
        
    def draw_utilization_chart(self, N, M, solution, p):
        """Dessine un graphique d'utilisation des quais."""
        self.chart1_canvas.axes.clear()
        
        # Calculer le temps de travail par quai
        workload_per_dock = [0] * M
        for res in solution:
            quai_idx = res['Quai'] - 1
            camion_idx = res['Camion'] - 1
            workload_per_dock[quai_idx] += p[camion_idx]
        
        # Créer le graphique en barres
        quais = [f'Quai {i+1}' for i in range(M)]
        colors_palette = plt.cm.get_cmap('viridis', M)
        colors = [colors_palette(i) for i in range(M)]
        
        bars = self.chart1_canvas.axes.bar(quais, workload_per_dock, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
        
        # Ajouter les valeurs sur les barres
        for bar, value in zip(bars, workload_per_dock):
            height = bar.get_height()
            self.chart1_canvas.axes.text(
                bar.get_x() + bar.get_width()/2., height,
                f'{value:.1f}',
                ha='center', va='bottom', color='white', fontsize=11, fontweight='bold'
            )
        
        self.chart1_canvas.axes.set_xlabel('Quais', color='white', fontsize=12, fontweight='bold')
        self.chart1_canvas.axes.set_ylabel('Temps de Travail (unités)', color='white', fontsize=12, fontweight='bold')
        self.chart1_canvas.axes.set_title('⚙️ Charge de Travail par Quai', color='white', fontsize=14, fontweight='bold', pad=15)
        self.chart1_canvas.axes.grid(axis='y', linestyle='--', alpha=0.3, color='white')
        
        self.chart1_canvas.fig.tight_layout()
        self.chart1_canvas.draw()
        
    def draw_delays_chart(self, N, solution, d):
        """Dessine un graphique de distribution des retards."""
        self.chart2_canvas.axes.clear()
        
        # Préparer les données
        camions = [f'C{res["Camion"]}' for res in solution]
        retards = [res['Retard'] for res in solution]
        
        # Couleurs : vert si à temps, rouge si en retard
        colors = ['#4CAF50' if r == 0 else '#f44336' for r in retards]
        
        bars = self.chart2_canvas.axes.bar(camions, retards, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
        
        # Ajouter les valeurs
        for bar, value in zip(bars, retards):
            if value > 0:
                height = bar.get_height()
                self.chart2_canvas.axes.text(
                    bar.get_x() + bar.get_width()/2., height,
                    f'{value:.1f}',
                    ha='center', va='bottom', color='white', fontsize=10, fontweight='bold'
                )
        
        self.chart2_canvas.axes.set_xlabel('Camions', color='white', fontsize=12, fontweight='bold')
        self.chart2_canvas.axes.set_ylabel('Retard (unités)', color='white', fontsize=12, fontweight='bold')
        self.chart2_canvas.axes.set_title('⏰ Retards par Camion', color='white', fontsize=14, fontweight='bold', pad=15)
        self.chart2_canvas.axes.grid(axis='y', linestyle='--', alpha=0.3, color='white')
        
        # Ligne de référence à 0
        self.chart2_canvas.axes.axhline(y=0, color='white', linestyle='-', linewidth=1, alpha=0.5)
        
        self.chart2_canvas.fig.tight_layout()
        self.chart2_canvas.draw()
        
    def draw_timeline_chart(self, N, solution, p, r, prep):
        """Dessine un graphique chronologique par camion."""
        self.analysis1_canvas.axes.clear()
        
        # Préparer les données
        camions = [f'C{res["Camion"]}' for res in solution]
        
        # Composantes du temps pour chaque camion
        disponibilites = [r[res['Camion']-1] for res in solution]
        preparations = [prep[res['Camion']-1] for res in solution]
        debuts = [res['Debut_Chargement'] for res in solution]
        durees = [p[res['Camion']-1] for res in solution]
        
        # Attentes (temps entre disponibilité+préparation et début réel)
        attentes = [max(0, debuts[i] - (disponibilites[i] + preparations[i])) for i in range(N)]
        
        # Graphique en barres empilées
        bar_width = 0.6
        indices = np.arange(N)
        
        # Barre 1: Disponibilité + Préparation
        p1 = self.analysis1_canvas.axes.barh(indices, disponibilites, bar_width, 
                                             label='Disponibilité', color='#9E9E9E', alpha=0.7)
        
        # Barre 2: Préparation
        p2 = self.analysis1_canvas.axes.barh(indices, preparations, bar_width, 
                                             left=disponibilites, label='Préparation', color='#FF9800', alpha=0.7)
        
        # Barre 3: Attente
        left_attente = [disponibilites[i] + preparations[i] for i in range(N)]
        p3 = self.analysis1_canvas.axes.barh(indices, attentes, bar_width, 
                                             left=left_attente, label='Attente', color='#2196F3', alpha=0.7)
        
        # Barre 4: Chargement
        left_chargement = [left_attente[i] + attentes[i] for i in range(N)]
        p4 = self.analysis1_canvas.axes.barh(indices, durees, bar_width, 
                                             left=left_chargement, label='Chargement', color='#4CAF50', alpha=0.8)
        
        self.analysis1_canvas.axes.set_yticks(indices)
        self.analysis1_canvas.axes.set_yticklabels(camions)
        self.analysis1_canvas.axes.set_xlabel('Temps (unités)', color='white', fontsize=12, fontweight='bold')
        self.analysis1_canvas.axes.set_ylabel('Camions', color='white', fontsize=12, fontweight='bold')
        self.analysis1_canvas.axes.set_title('⏱️ Décomposition du Temps par Camion', color='white', fontsize=14, fontweight='bold', pad=15)
        self.analysis1_canvas.axes.legend(loc='upper right', facecolor='#2b2b2b', edgecolor='white', fontsize=9)
        self.analysis1_canvas.axes.grid(axis='x', linestyle='--', alpha=0.3, color='white')
        
        self.analysis1_canvas.fig.tight_layout()
        self.analysis1_canvas.draw()
        
    def draw_workload_pie(self, N, M, solution, p):
        """Dessine un diagramme circulaire de répartition du travail."""
        self.analysis2_canvas.axes.clear()
        
        # Calculer le temps de travail par quai
        workload_per_dock = [0] * M
        for res in solution:
            quai_idx = res['Quai'] - 1
            camion_idx = res['Camion'] - 1
            workload_per_dock[quai_idx] += p[camion_idx]
        
        # Filtrer les quais avec du travail
        labels = [f'Quai {i+1}\n({workload_per_dock[i]:.1f}u)' for i in range(M) if workload_per_dock[i] > 0]
        sizes = [workload_per_dock[i] for i in range(M) if workload_per_dock[i] > 0]
        
        # Couleurs
        colors_palette = plt.cm.get_cmap('Set3', len(sizes))
        colors = [colors_palette(i) for i in range(len(sizes))]
        
        # Créer le camembert
        wedges, texts, autotexts = self.analysis2_canvas.axes.pie(
            sizes, 
            labels=labels, 
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'color': 'white', 'fontsize': 11, 'fontweight': 'bold'}
        )
        
        # Style des pourcentages
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontsize(12)
            autotext.set_fontweight('bold')
        
        self.analysis2_canvas.axes.set_title(
            '🥧 Répartition de la Charge de Travail', 
            color='white', 
            fontsize=14, 
            fontweight='bold',
            pad=15
        )
        
        self.analysis2_canvas.fig.tight_layout()
        self.analysis2_canvas.draw()
        
    def _update_status(self, message, color="#aaa"):
        """Met à jour le label de statut avec animation."""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"""
            font-size: 14px;
            padding: 8px 15px;
            background-color: #2b2b2b;
            border-radius: 5px;
            color: {color};
            border: 2px solid {color};
        """)
        
        # Animation simple
        QTimer.singleShot(3000, lambda: self.status_label.setStyleSheet(f"""
            font-size: 14px;
            padding: 8px 15px;
            background-color: #2b2b2b;
            border-radius: 5px;
            color: #aaa;
        """))


def main():
    app = QApplication(sys.argv)
    
    # Configuration de la police par défaut
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    main_window = OrdonnancementApp()
    main_window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
