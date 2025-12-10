import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QLineEdit, QLabel, QHeaderView
)
from PyQt5.QtCore import Qt

# Import Matplotlib pour le diagramme de Gantt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Import du module Gurobi (doit être dans le même dossier ou accessible)
from ModeleGurobi import resoudre_ordonnancement_avance 
import numpy as np

class MplCanvas(FigureCanvas):
    """Classe pour intégrer un graphique Matplotlib dans une fenêtre PyQt."""
    def __init__(self, parent=None, width=8, height=4, dpi=100):
        # Utiliser tight_layout pour éviter le rognage des titres/labels
        fig, self.axes = plt.subplots(figsize=(width, height), dpi=dpi, layout='constrained') 
        super(MplCanvas, self).__init__(fig)
        self.setParent(parent)
        self.fig = fig # Stocker la figure pour la vider ou la mettre à jour

class OrdonnancementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logistique: Séquençage des Camions - Optimisation PLNE")
        self.setGeometry(100, 100, 1200, 800)
        
        self.M = 2 # Nombre de quais initial
        self.N = 0 # Nombre de camions initial
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self._setup_ui()
        self.add_truck_row() # Ajout d'un camion par défaut
        
    def _setup_ui(self):
        """Configuration de l'interface utilisateur."""
        
        # --- 1. Contrôles généraux (M, C_swap, Add/Remove) ---
        control_layout = QHBoxLayout()
        
        control_layout.addWidget(QLabel("Nombre de Quais (M):"))
        self.quais_input = QLineEdit(str(self.M))
        self.quais_input.setFixedWidth(50)
        # NOUVEAU: Mettre à jour la structure dès que l'édition est terminée (pour synchroniser les colonnes)
        self.quais_input.editingFinished.connect(self.update_tables_structure)
        control_layout.addWidget(self.quais_input)

        control_layout.addWidget(QLabel("Coût de Pénalité (C_swap):"))
        self.cswap_input = QLineEdit("1000")
        self.cswap_input.setFixedWidth(80)
        control_layout.addWidget(self.cswap_input)
        
        self.add_camion_btn = QPushButton("➕ Ajouter Camion")
        self.add_camion_btn.clicked.connect(self.add_truck_row)
        control_layout.addWidget(self.add_camion_btn)

        # NOUVEAU: Bouton pour supprimer le dernier camion
        self.remove_camion_btn = QPushButton("➖ Supprimer dernier Camion")
        self.remove_camion_btn.clicked.connect(self.remove_truck_row)
        control_layout.addWidget(self.remove_camion_btn)

        control_layout.addStretch(1)
        
        self.optimize_btn = QPushButton("Lancer l'Optimisation")
        self.optimize_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.optimize_btn.clicked.connect(self.run_optimization)
        control_layout.addWidget(self.optimize_btn)
        
        self.layout.addLayout(control_layout)

        # --- 2. Conteneur à onglets ---
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Onglets
        self.tab_input = QWidget()
        self.tab_results = QWidget()
        self.tab_gantt = QWidget()
        
        self.tabs.addTab(self.tab_input, "1. Saisie des Données")
        self.tabs.addTab(self.tab_results, "2. Résultats et Métriques")
        self.tabs.addTab(self.tab_gantt, "3. Diagramme de Gantt")

        self._setup_input_tab()
        self._setup_results_tab()
        self._setup_gantt_tab()

    def _setup_input_tab(self):
        """Configuration de l'onglet de saisie des données."""
        input_layout = QVBoxLayout(self.tab_input)
        
        # Tableau des propriétés des camions (p_i, r_i, d_i, prep_i)
        self.camions_table = QTableWidget()
        self.camions_table.setColumnCount(4)
        self.camions_table.setHorizontalHeaderLabels([
            "Temps Traitement (p)", "Date Dispo (r)", "Date Échéance (d)", "Temps Prépa (prep)"
        ])
        self.camions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        input_layout.addWidget(QLabel("Propriétés des Camions:"))
        input_layout.addWidget(self.camions_table)
        
        # Tableau des affectations autorisées (a_ik)
        self.affectation_table = QTableWidget()
        input_layout.addWidget(QLabel("Restrictions d'Affectation (1 = Autorisé / 0 = Interdit):"))
        input_layout.addWidget(self.affectation_table)
        
        # L'initialisation se fera dans l'__init__ via add_truck_row
        
    def _setup_results_tab(self):
        # ... (Le code des résultats reste inchangé)
        results_layout = QVBoxLayout(self.tab_results)
        
        self.metrics_label = QLabel("Métriques: Cmax = N/A | Coût Pénalité = N/A")
        self.metrics_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00796b;")
        results_layout.addWidget(self.metrics_label)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "Camion ID", "Quai Affecté", "Début Chargement (S)", "Fin Opération (C)", "Retard (T)"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        results_layout.addWidget(QLabel("Détails du Séquencement Optimal:"))
        results_layout.addWidget(self.results_table)


    def _setup_gantt_tab(self):
        # ... (Le code du Gantt reste inchangé)
        gantt_layout = QVBoxLayout(self.tab_gantt)
        
        self.sc = MplCanvas(self, width=8, height=6, dpi=100)
        gantt_layout.addWidget(self.sc)
        

    def update_tables_structure(self):
        """Met à jour les dimensions des tableaux de saisie, notamment le nombre de colonnes M."""
        try:
            # 1. Mise à jour du nombre de quais (M)
            new_M = int(self.quais_input.text())
            if new_M <= 0:
                raise ValueError("Le nombre de quais doit être > 0.")
            self.M = new_M
        except ValueError as e:
            QMessageBox.warning(self, "Erreur de Valeur", f"Erreur M : {e}\nValeur par défaut (2) sera utilisée.")
            self.M = 2
            self.quais_input.setText("2")
        
        self.N = self.camions_table.rowCount()

        # 2. Mise à jour du tableau d'affectation (N x M)
        self.affectation_table.setRowCount(self.N)
        self.affectation_table.setColumnCount(self.M)
        
        quai_labels = [f"Quai {k+1}" for k in range(self.M)]
        self.affectation_table.setHorizontalHeaderLabels(quai_labels)
        
        # S'assurer que les cellules nouvellement créées (en cas d'augmentation de M) sont initialisées à '1'
        for i in range(self.N):
            for k in range(self.M):
                item = self.affectation_table.item(i, k)
                if item is None:
                    # Remplir uniquement les nouvelles cellules
                    item = QTableWidgetItem("1")
                    self.affectation_table.setItem(i, k, item)
                    
            # Mettre à jour les headers verticaux (Camion ID)
            self.camions_table.setVerticalHeaderItem(i, QTableWidgetItem(f"Camion {i+1}"))
            self.affectation_table.setVerticalHeaderItem(i, QTableWidgetItem(f"Camion {i+1}"))
            
        self.affectation_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


    def add_truck_row(self):
        """Ajoute une ligne de camion dans les tableaux de saisie."""
        current_row = self.camions_table.rowCount()
        self.camions_table.insertRow(current_row)
        
        # Initialisation des valeurs par défaut dans le tableau de camions
        # p, r, d, prep
        default_values = ["10", "0", "20", "2"] 
        for col, val in enumerate(default_values):
            self.camions_table.setItem(current_row, col, QTableWidgetItem(val))
            
        # Mise à jour du tableau d'affectation pour inclure la nouvelle ligne
        self.update_tables_structure() 
        self.N = self.camions_table.rowCount()


    def remove_truck_row(self):
        """Supprime la dernière ligne de camion des tableaux de saisie."""
        current_row = self.camions_table.rowCount()
        
        if current_row > 0:
            # Supprimer la ligne dans les deux tableaux
            self.camions_table.removeRow(current_row - 1)
            self.affectation_table.removeRow(current_row - 1)
            
            # Mettre à jour le compteur N
            self.N = current_row - 1
            
            # Re-déclencher la mise à jour de la structure (pour les headers si nécessaire)
            self.update_tables_structure() 
        else:
            QMessageBox.information(self, "Avertissement", "Il n'y a plus de camion à supprimer.")


    def get_input_data(self):
        """Récupère et valide toutes les données d'entrée de l'utilisateur."""
        try:
            M = int(self.quais_input.text())
            C_swap = float(self.cswap_input.text())
            N = self.camions_table.rowCount()
            
            if N == 0 or M == 0:
                 QMessageBox.warning(self, "Avertissement", "Veuillez ajouter au moins un camion et un quai.")
                 return None
            
            p, r, d, prep = [], [], [], []
            a = np.zeros((N, M), dtype=int)
            
            # Récupération des propriétés (p, r, d, prep)
            for i in range(N):
                p.append(float(self.camions_table.item(i, 0).text()))
                r.append(float(self.camions_table.item(i, 1).text()))
                d.append(float(self.camions_table.item(i, 2).text()))
                prep.append(float(self.camions_table.item(i, 3).text()))
            
            # Récupération des affectations autorisées (a_ik)
            for i in range(N):
                for k in range(M):
                    a[i, k] = int(self.affectation_table.item(i, k).text())
                    
            return N, M, p, r, d, prep, a.tolist(), C_swap
        
        except Exception as e:
            QMessageBox.critical(self, "Erreur de Saisie", 
                                 f"Veuillez vérifier les valeurs numériques ou la structure des tableaux. Détail: {e}")
            return None


    def run_optimization(self):
        """Lance l'optimisation Gurobi et affiche les résultats."""
        data = self.get_input_data()
        if data is None:
            return
            
        N, M, p, r, d, prep, a, C_swap = data
        
        # Appel du solveur Gurobi
        Cmax_opt, P_cost_opt, solution = resoudre_ordonnancement_avance(N, M, p, r, d, prep, a, C_swap)
        
        if isinstance(solution, str):
            QMessageBox.critical(self, "Erreur Gurobi", solution)
            return

        # Affichage des métriques
        total_cost = Cmax_opt + C_swap * P_cost_opt
        self.metrics_label.setText(
            f"Métriques Optimales: Cmax = {Cmax_opt:.2f} | Coût Pénalité = {P_cost_opt:.0f} | Z (Total) = {total_cost:.2f}"
        )

        # Affichage du tableau de résultats
        self.results_table.setRowCount(N)
        for i, res in enumerate(solution):
            self.results_table.setItem(i, 0, QTableWidgetItem(str(res['Camion'])))
            self.results_table.setItem(i, 1, QTableWidgetItem(str(res['Quai'])))
            self.results_table.setItem(i, 2, QTableWidgetItem(f"{res['Debut_Chargement']:.2f}"))
            self.results_table.setItem(i, 3, QTableWidgetItem(f"{res['Fin_Operation']:.2f}"))
            self.results_table.setItem(i, 4, QTableWidgetItem(f"{res['Retard']:.2f}"))
            
        # Génération du diagramme de Gantt
        self.draw_gantt(N, M, solution, d, r, prep)
        self.tabs.setCurrentIndex(2) # Passer à l'onglet Gantt


    def draw_gantt(self, N, M, solution, d, r, prep):
        """Dessine le diagramme de Gantt des opérations.
        
        """
        
        self.sc.axes.clear()
        colors = plt.cm.get_cmap('hsv', N + 1) # Palette de couleurs
        
        # Tri de la solution par Quai et par Heure de Début pour l'affichage
        solution_sorted = sorted(solution, key=lambda x: (x['Quai'], x['Debut_Chargement']))
        
        for i, res in enumerate(solution_sorted):
            camion_index = res['Camion'] - 1 # Utiliser l'index pour accéder aux listes p, r, d, prep
            quai = res['Quai']
            start_op = res['Debut_Chargement']
            end_op = res['Fin_Operation']
            
            duration_chargement = end_op - start_op 
            prep_time = prep[camion_index]
            prep_start = start_op - prep_time
            due_date = d[camion_index]
            
            # 1. Barres de Chargement (Opération principale)
            self.sc.axes.barh(
                quai, duration_chargement, 
                left=start_op, 
                height=0.6, 
                color=colors(camion_index), 
                alpha=0.8
            )
            
            # 2. Barres de Préparation (Temps avant le chargement)
            if prep_time > 0:
                 self.sc.axes.barh(
                    quai, prep_time, 
                    left=prep_start, 
                    height=0.3, # Barre plus fine
                    color=colors(camion_index), 
                    alpha=0.3, # Plus transparent
                    edgecolor='none'
                )

            # 3. Marques pour l'heure d'échéance (d_i) et Retard
            if end_op > due_date:
                # Marquer la deadline dépassée
                self.sc.axes.plot([due_date, due_date], [quai - 0.5, quai + 0.5], 
                                 '--', color='red', linewidth=1.5, alpha=0.7)
                # Marquer le retard (hachures sur la partie en retard)
                self.sc.axes.barh(
                    quai, end_op - due_date, 
                    left=due_date, 
                    height=0.6, 
                    color='none', 
                    edgecolor='red', 
                    hatch='//',
                    linewidth=0
                )
            
            # 4. Texte de la tâche au centre de la barre de chargement
            self.sc.axes.text(start_op + duration_chargement / 2, quai, 
                             f'C{camion_index+1}', 
                             ha='center', va='center', color='black', fontsize=8, fontweight='bold')

        # Configuration finale du graphique
        self.sc.axes.set_yticks(np.arange(1, M + 1))
        self.sc.axes.set_yticklabels([f'Quai {k+1}' for k in range(M)])
        self.sc.axes.set_xlabel("Temps (Heures / Unités de temps)")
        self.sc.axes.set_ylabel("Quais de Chargement")
        self.sc.axes.set_title("Diagramme de Gantt - Séquencement Optimal des Camions")
        self.sc.axes.grid(axis='x', linestyle='--', alpha=0.6)
        
        # Début de l'axe des temps
        all_starts = [res['Debut_Chargement'] for res in solution_sorted]
        start_min = min(all_starts) if all_starts else 0
        self.sc.axes.set_xlim(left=max(0, start_min - 5)) 

        self.sc.draw()