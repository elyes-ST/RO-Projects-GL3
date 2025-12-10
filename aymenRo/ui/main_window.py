# ui/main_window.py
import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QPushButton, QTextEdit, QTableWidget, 
    QTableWidgetItem, QHeaderView, QGroupBox, QFileDialog, QSizePolicy, 
    QTabWidget, QDoubleSpinBox, QSpinBox
)
from PyQt5.QtCore import Qt, QLocale
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Import des modules locaux
try:
    from models.optimization_model import solve_planning_model
    from data.data_manager import load_period_data
except ImportError:
    pass 


class MplCanvas(FigureCanvas):
    """Widget pour Matplotlib dans PyQt"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
        self.setMinimumHeight(250)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class OptimizationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💰 Planification Financière et Opérationnelle AVANCÉE")
        self.setGeometry(100, 100, 1400, 800)
        self.data_df = None
        self.results_df = None
        self.shadow_prices_df = None
        self.init_ui()
        self.apply_styles()

    def apply_styles(self):
        """Applique des styles CSS de base pour un look plus moderne."""
        self.setStyleSheet("""
            QWidget { font-size: 10pt; }
            QGroupBox { 
                font-weight: bold; 
                margin-top: 10px; 
                border: 1px solid #C0C0C0; 
                border-radius: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
            QPushButton#RunButton {
                background-color: #007ACC; 
                color: white; 
                font-weight: bold; 
                height: 30px;
                border-radius: 5px;
            }
            QLabel#KPI_Label {
                font-size: 11pt;
                color: #333333;
                padding: 3px;
            }
        """)

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # --- 1. Zone de Configuration (Haut) ---
        config_layout = QHBoxLayout()
        
        # 1.1. Conteneur des Paramètres par Onglets
        self.param_tabs = QTabWidget()
        self.param_tabs.addTab(self.create_operational_tab(), "📊 Opérationnel")
        self.param_tabs.addTab(self.create_strategic_tab(), "⚙️ Stratégique (Capacité)")
        self.param_tabs.addTab(self.create_financial_tab(), "€ Financier & Délais")
        
        self.params_group = QGroupBox("Configuration du Modèle (Entrées)")
        params_vbox = QVBoxLayout()
        params_vbox.addWidget(self.param_tabs)
        self.params_group.setLayout(params_vbox)
        config_layout.addWidget(self.params_group)
        
        # 1.2. Groupe Fichier et Résolution
        file_group = QGroupBox("▶️ Contrôle du Solveur")
        file_layout = QVBoxLayout()
        
        self.data_path_label = QLabel("Fichier de données: data_example.csv")
        file_layout.addWidget(self.data_path_label)
        
        load_btn = QPushButton("Charger Fichier CSV (Demande/Capacité Initiale)")
        load_btn.clicked.connect(self.load_data)
        file_layout.addWidget(load_btn)
        
        self.run_btn = QPushButton("Lancer l'Optimisation Gurobi Avancée")
        self.run_btn.setObjectName("RunButton")
        self.run_btn.clicked.connect(self.run_optimization)
        file_layout.addWidget(self.run_btn)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setText("Prêt à charger les données et lancer le modèle...")
        self.log_output.setMaximumHeight(100)
        file_layout.addWidget(self.log_output)
        
        file_group.setLayout(file_layout)
        config_layout.addWidget(file_group)
        
        main_layout.addLayout(config_layout)
        
        # --- 2. Zone des Résultats Détaillés (Milieu) ---
        self.results_tabs = QTabWidget()
        self.results_table = self.create_results_table()
        self.shadow_table = self.create_results_table()
        
        self.results_tabs.addTab(self.results_table, "Plan Opérationnel et Financier")
        self.results_tabs.addTab(self.shadow_table, "Analyse d'Incidence (Prix Duaux)")
        
        main_layout.addWidget(self.results_tabs)
        
        # --- 3. Zone des Indicateurs Clés et Graphiques (Bas) ---
        kpi_graph_layout = QHBoxLayout()
        
        # 3.1. Indicateurs de Performance (KPIs)
        self.kpi_group = QGroupBox("🏆 Indicateurs Clés (KPIs)")
        self.kpi_layout = QVBoxLayout()
        self.kpi_cost_label = QLabel("Coût Total Actualisé Optimal: N/A")
        self.kpi_cost_label.setObjectName("KPI_Label")
        self.kpi_stock_label = QLabel("Stock Final Réalisé: N/A")
        self.kpi_stock_label.setObjectName("KPI_Label")
        self.kpi_cash_label = QLabel("Solde Trésorerie Final: N/A")
        self.kpi_cash_label.setObjectName("KPI_Label")
        self.kpi_invest_label = QLabel("Coût Total Investissement: N/A")
        self.kpi_invest_label.setObjectName("KPI_Label")
        
        self.kpi_layout.addWidget(self.kpi_cost_label)
        self.kpi_layout.addWidget(self.kpi_stock_label)
        self.kpi_layout.addWidget(self.kpi_cash_label)
        self.kpi_layout.addWidget(self.kpi_invest_label)
        self.kpi_layout.addStretch(1)
        self.kpi_group.setLayout(self.kpi_layout)
        self.kpi_group.setMaximumWidth(350)
        kpi_graph_layout.addWidget(self.kpi_group)

        # 3.2. Graphiques
        self.sc_production = MplCanvas(self)
        self.sc_cashflow = MplCanvas(self)
        
        graph_group = QGroupBox("📈 Visualisation des Résultats")
        graph_layout = QHBoxLayout()
        graph_layout.addWidget(self.sc_production)
        graph_layout.addWidget(self.sc_cashflow)
        graph_group.setLayout(graph_layout)
        
        kpi_graph_layout.addWidget(graph_group)
        main_layout.addLayout(kpi_graph_layout)
        
        self.setLayout(main_layout)
        
        # Chargement des données par défaut au démarrage
        self.load_data(default_path='data_example.csv')

    def create_results_table(self):
        table = QTableWidget()
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        return table

    # --- Fonctions de Création d'Onglets (Refactorisées pour la clarté) ---

    def create_operational_tab(self):
        tab = QWidget()
        layout = QGridLayout()
        
        # Ligne 0 : Coût Fixe Lancement (seul sur 2 colonnes)
        self.add_param_field(layout, "Coût Fixe Lancement (€)", "cout_fixe", 0, 0, field_type='float', default_value=10000.0,
                             tooltip_text="Coût fixe engagé pour chaque période où la production (X_t > 0) est lancée.")
        
        # Ligne 1 : Coût Prod vs Coût Appro
        self.add_param_field(layout, "Coût Prod (€/U)", "cout_prod", 1, 0, field_type='float', default_value=100.0,
                             tooltip_text="Coût variable par unité produite, hors approvisionnement externe.")
        self.add_param_field(layout, "Coût Appro (€/U)", "cout_appro", 1, 2, field_type='float', default_value=80.0,
                             tooltip_text="Coût d'achat par unité si la demande est satisfaite par approvisionnement externe (A_t).") 
        
        # Ligne 2 : Coût Stockage vs Coût Rupture
        self.add_param_field(layout, "Coût Stockage (€/U/P)", "cout_stock", 2, 0, field_type='float', default_value=2.0,
                             tooltip_text="Coût de maintien d'une unité de stock (I_t) pour une période.")
        self.add_param_field(layout, "Coût Rupture (€/U)", "cout_rupture", 2, 2, field_type='float', default_value=500.0,
                             tooltip_text="Pénalité encourue par unité de demande non satisfaite (S_t). Doit être élevé.")
        
        # Ligne 3 : Stock Initial vs Stock Final Cible
        self.add_param_field(layout, "Stock Initial (U)", "stock_initial", 3, 0, field_type='int', default_value=500,
                             tooltip_text="Niveau de stock au début de la première période (t=0).")
        self.add_param_field(layout, "Stock Final Cible (U)", "stock_final_cible", 3, 2, field_type='int', default_value=500,
                             tooltip_text="Niveau de stock souhaité à la fin de la dernière période (t=T).")
        
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)
        layout.setRowStretch(4, 1)
        
        tab.setLayout(layout)
        return tab

    def create_strategic_tab(self):
        tab = QWidget()
        layout = QGridLayout()
        
        # Ligne 0 : Coût Invest vs Coût Désinvest
        self.add_param_field(layout, "Coût Invest Cap (€)", "cout_invest_cap", 0, 0, field_type='float', default_value=500000.0,
                             tooltip_text="Coût total pour une décision d'investissement (Z_inv = 1) augmentant la capacité de Delta Cap.")
        self.add_param_field(layout, "Coût Désinvest Cap (€)", "cout_desinvest_cap", 0, 2, field_type='float', default_value=50000.0,
                             tooltip_text="Gain (ou coût négatif) pour une décision de désinvestissement (Z_des = 1).")
        
        # Ligne 1 : Delta Cap (seul sur 2 colonnes)
        self.add_param_field(layout, "Delta Cap (U)", "delta_cap", 1, 0, field_type='int', default_value=1000,
                             tooltip_text="Quantité d'unités ajoutée ou retirée de la capacité par décision (Z_inv ou Z_des).")
        
        layout.setRowStretch(2, 1) 
        tab.setLayout(layout)
        return tab

    def create_financial_tab(self):
        tab = QWidget()
        layout = QGridLayout()
        
        # Ligne 0 : Taux Actualisation vs Prix de Vente
        self.add_param_field(layout, "Taux Actualisation (r)", "taux_actualisation", 0, 0, field_type='float', decimals=4, default_value=0.01,
                             tooltip_text="Taux d'intérêt utilisé pour actualiser les flux de trésorerie futurs (ex: 0.01 pour 1%).")
        self.add_param_field(layout, "Prix de Vente (€/U)", "prix_vente", 0, 2, field_type='float', default_value=150.0,
                             tooltip_text="Prix de vente par unité. Utilisé pour calculer les revenus (Encaissements).")
        
        # Ligne 1 : Solde Trésorerie Initial (seul sur 2 colonnes)
        self.add_param_field(layout, "Solde Trésorerie Initial (€)", "solde_tresorerie_initial", 1, 0, field_type='float', default_value=50000.0,
                             tooltip_text="Encaisse disponible au début de la période de planification.")
        
        # Ligne 2 : Délais Paiement vs Encaissement
        self.add_param_field(layout, "Délai Paiement (pér.)", "delai_paiement", 2, 0, field_type='int', default_value=1,
                             tooltip_text="Nombre de périodes de décalage entre l'engagement du coût et le décaissement réel.")
        self.add_param_field(layout, "Délai Encaissement (pér.)", "delai_encaissement", 2, 2, field_type='int', default_value=2,
                             tooltip_text="Nombre de périodes de décalage entre la vente (Demande - Rupture) et l'encaissement réel.")
        
        layout.setRowStretch(3, 1) 
        tab.setLayout(layout)
        return tab

    # --- Fonctions Utilitaires ---

    def add_param_field(self, layout, label_text, key, row, col, field_type='float', decimals=2, default_value=0.0, tooltip_text=""):
        """Ajoute un label, un champ SpinBox/DoubleSpinBox et un Tooltip."""
        label = QLabel(label_text)
        
        if field_type == 'float':
            field = QDoubleSpinBox()
            field.setRange(-99999999.00, 99999999.00)
            field.setValue(float(default_value)) 
            field.setDecimals(decimals)
            field.setSingleStep(1 if decimals == 0 else 0.1)
            # Correction pour la locale décimale
            field.setLocale(QLocale(QLocale.English, QLocale.UnitedStates)) 
            
        else: # int
            field = QSpinBox()
            field.setRange(-99999999, 99999999)
            field.setValue(int(default_value)) 

        field.setObjectName(key)
        
        if tooltip_text:
            field.setToolTip(tooltip_text)
            label.setToolTip(tooltip_text)

        # Ajout des widgets au QGridLayout (Label en 'col', Champ en 'col + 1')
        layout.addWidget(label, row, col) 
        layout.addWidget(field, row, col + 1)


    def get_params(self):
        """Récupère les paramètres de l'interface."""
        params = {}
        param_names = [
            'cout_prod', 'cout_appro', 'cout_stock', 'cout_rupture', 'cout_fixe', 'prix_vente',
            'cout_invest_cap', 'cout_desinvest_cap', 'delta_cap',
            'taux_actualisation', 'stock_initial', 'stock_final_cible', 
            'delai_paiement', 'delai_encaissement', 'solde_tresorerie_initial'
        ]
        
        all_widgets = self.findChildren(QDoubleSpinBox) + self.findChildren(QSpinBox)

        for name in param_names:
            found = False
            for widget in all_widgets:
                if widget.objectName() == name:
                    params[name] = widget.value()
                    found = True
                    break
            
            if not found:
                 self.log_output.setText(f"Erreur: Le champ de paramètre '{name}' est introuvable.")
                 return None
        
        return params

    def load_data(self, default_path=None):
        """Charge les données de demande et capacité à partir d'un CSV."""
        if not default_path:
            file_name, _ = QFileDialog.getOpenFileName(self, "Charger Données CSV", "", "CSV Files (*.csv)")
            if not file_name:
                return
        else:
            file_name = default_path

        try:
            self.data_df = load_period_data(file_name)
        except NameError:
             self.log_output.setText("Erreur : Le module 'load_period_data' n'est pas accessible. Assurez-vous que data_manager.py est présent.")
             return

        if isinstance(self.data_df, pd.DataFrame):
            self.data_path_label.setText(f"Fichier de données chargé: {file_name.split('/')[-1]} ({len(self.data_df)} périodes)")
            self.log_output.setText(f"Données de {len(self.data_df)} périodes chargées avec succès.")
        else:
            self.log_output.setText(str(self.data_df))
            self.data_df = None

    def run_optimization(self):
        """Lance l'optimisation Gurobi et affiche les résultats."""
        if self.data_df is None:
            self.log_output.setText("Erreur: Veuillez charger les données avant de lancer l'optimisation.")
            return

        params = self.get_params()
        if params is None:
            return

        self.log_output.setText("Lancement de l'optimisation Gurobi avancée... (Veuillez patienter)")
        QApplication.processEvents()

        try:
            results_tuple = solve_planning_model(self.data_df, params)
        except NameError:
             self.log_output.setText("Erreur : Le module 'solve_planning_model' n'est pas accessible. Assurez-vous que optimization_model.py est présent.")
             return
        
        if isinstance(results_tuple[0], pd.DataFrame):
            self.results_df, self.shadow_prices_df = results_tuple
            self.log_output.setText("✅ Optimisation terminée avec succès. Résultats et Prix Duaux calculés.")
            self.display_results(params)
            self.plot_results()
        else:
            self.log_output.setText(f"❌ Échec de l'optimisation: {results_tuple[0]}")

    def display_results(self, params):
        """Affiche les résultats dans les tableaux et met à jour les KPIs."""
        
        df = self.results_df.round(2)
        rows, cols = df.shape
        self.results_table.setRowCount(rows)
        self.results_table.setColumnCount(cols)
        self.results_table.setHorizontalHeaderLabels(df.columns)

        for i in range(rows):
            for j in range(cols):
                item = QTableWidgetItem(str(df.iloc[i, j]))
                self.results_table.setItem(i, j, item)
            
            period_item = QTableWidgetItem(df.index[i])
            self.results_table.setVerticalHeaderItem(i, period_item)
        
        self.results_table.resizeColumnsToContents()
        
        df_shadow = self.shadow_prices_df.round(4)
        rows_s, cols_s = df_shadow.shape
        self.shadow_table.setRowCount(rows_s)
        self.shadow_table.setColumnCount(cols_s)
        self.shadow_table.setHorizontalHeaderLabels(df_shadow.columns)

        for i in range(rows_s):
            for j in range(cols_s):
                item = QTableWidgetItem(str(df_shadow.iloc[i, j]))
                self.shadow_table.setItem(i, j, item)
            
            period_item = QTableWidgetItem(df_shadow.index[i])
            self.shadow_table.setVerticalHeaderItem(i, period_item)

        self.shadow_table.resizeColumnsToContents()

        # --- Mise à jour des KPIs ---
        cost_total = df['Coût Actualisé Total'].iloc[0]
        stock_final = df['Stock Fin (I_t)'].iloc[-1]
        cash_final = df['Solde_Cumulé'].iloc[-1]
        
        total_invest_cost = (
            df['Investissement (Z_inv)'].sum() * params['cout_invest_cap']
        )
        
        self.kpi_cost_label.setText(f"Coût Total Actualisé Optimal: <b>{cost_total:,.2f} €</b>")
        self.kpi_stock_label.setText(f"Stock Final Réalisé: <b>{stock_final:,.0f} U</b>")
        self.kpi_cash_label.setText(f"Solde Trésorerie Final: <b>{cash_final:,.2f} €</b>")
        self.kpi_invest_label.setText(f"Coût Total Investissement: <b>{total_invest_cost:,.2f} €</b>")


    def plot_results(self):
        """Trace les graphiques des résultats."""
        df = self.results_df
        periods = df.index
        x = range(len(periods))
        
        # --- Graphique 1 : Plan Opérationnel et Capacités ---
        self.sc_production.axes.clear()
        
        self.sc_production.axes.bar(x, df['Production (P_t)'], width=0.8, label='Production (P_t)', color='#4CAF50')
        self.sc_production.axes.bar(x, df['Approvisionnement (A_t)'], bottom=df['Production (P_t)'], width=0.8, label='Approvisionnement (A_t)', color='#FFC107')
        
        self.sc_production.axes.plot(x, df['Demande (D_t)'], 'k--', marker='o', label='Demande (D_t)')
        
        self.sc_production.axes.plot(x, df['Capacité Fin (Cap_t)'], 'b-', marker='^', label='Capacité Disponible', linewidth=2)
        
        self.sc_production.axes.set_xticks(x)
        self.sc_production.axes.set_xticklabels(periods, rotation=45, ha='right')
        self.sc_production.axes.set_title("Plan Opérationnel, Approvisionnement & Capacité")
        self.sc_production.axes.legend(loc='upper left', fontsize=8)
        self.sc_production.axes.grid(True, axis='y', linestyle='--')
        self.sc_production.draw()

        # --- Graphique 2 : Flux de Trésorerie ---
        self.sc_cashflow.axes.clear()
        
        colors = ['#28A745' if val >= 0 else '#DC3545' for val in df['Flux_Net']]
        self.sc_cashflow.axes.bar(periods, df['Flux_Net'], color=colors, label='Flux de Trésorerie Net')

        ax2 = self.sc_cashflow.axes.twinx()
        ax2.plot(periods, df['Solde_Cumulé'], 'b-o', label='Solde Cumulé (Échelle Droite)', linewidth=3)
        ax2.set_ylabel('Solde de Trésorerie Cumulé (€)', color='blue')
        ax2.tick_params(axis='y', labelcolor='blue')
        
        self.sc_cashflow.axes.axhline(0, color='grey', linestyle='-') 
        self.sc_cashflow.axes.set_xticklabels(periods, rotation=45, ha='right')
        self.sc_cashflow.axes.set_title("Analyse des Flux de Trésorerie")
        
        lines, labels = self.sc_cashflow.axes.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        self.sc_cashflow.axes.legend(lines + lines2, labels + labels2, loc='upper left', fontsize=8)

        self.sc_cashflow.axes.grid(True, axis='y', linestyle='--')
        self.sc_cashflow.draw()


if __name__ == "__main__":
    import os
    if not (os.path.exists("../data/data_manager.py") and os.path.exists("../models/optimization_model.py")):
         pass
        
    app = QApplication(sys.argv)
    ex = OptimizationApp()
    ex.show()
    sys.exit(app.exec_())