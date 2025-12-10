from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QTableWidget, QTableWidgetItem, QMessageBox, 
    QLineEdit, QTextEdit, QSplitter, QGroupBox, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from worker.solver_thread import SolverThread
from utils.graph_utils import draw_graph, table_to_graph_data
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Optimisation: Chemin le moins cher avec checkpoint (Gurobi + PyQt5)')
        self.resize(1400, 900)
        self._build_ui()
        self.solver_thread = None
        self.last_solution_details = None

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()

        # ═══════════════════════════════════════════════════════════
        # SECTION CONTRÔLES
        # ═══════════════════════════════════════════════════════════
        controls_group = QGroupBox("Contrôles")
        controls_layout = QVBoxLayout()
        
        # Ligne 1: Boutons d'action
        row1 = QHBoxLayout()
        self.load_btn = QPushButton('📂 Charger CSV')
        self.load_btn.clicked.connect(self.load_csv)
        row1.addWidget(self.load_btn)

        self.run_btn = QPushButton('▶ Lancer le Solveur')
        self.run_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.run_btn.clicked.connect(self.run_solver)
        row1.addWidget(self.run_btn)

        self.stop_btn = QPushButton('⏹ Arrêter')
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.stop_btn.clicked.connect(self.stop_solver)
        self.stop_btn.setEnabled(False)
        row1.addWidget(self.stop_btn)
        
        controls_layout.addLayout(row1)

        # Ligne 2: Paramètres du problème
        row2 = QHBoxLayout()
        row2.addWidget(QLabel('Source:'))
        self.src_input = QLineEdit('A')
        self.src_input.setMaximumWidth(80)
        row2.addWidget(self.src_input)

        row2.addWidget(QLabel('Cible:'))
        self.tgt_input = QLineEdit('D')
        self.tgt_input.setMaximumWidth(80)
        row2.addWidget(self.tgt_input)

        row2.addWidget(QLabel('Checkpoints (séparés par virgule):'))
        self.checkpoints_input = QLineEdit('B,C')
        row2.addWidget(self.checkpoints_input)

        controls_layout.addLayout(row2)
        controls_group.setLayout(controls_layout)
        main_layout.addWidget(controls_group)

        # ═══════════════════════════════════════════════════════════
        # SPLITTER PRINCIPAL: Gauche (Données) / Droite (Résultats)
        # ═══════════════════════════════════════════════════════════
        splitter = QSplitter(Qt.Horizontal)
        
        # PARTIE GAUCHE: Saisie des données
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        data_group = QGroupBox("Données du graphe (arêtes)")
        data_layout = QVBoxLayout()
        
        # Table pour saisir les arêtes: u, v, cost
        self.table = QTableWidget(5, 3)
        self.table.setHorizontalHeaderLabels(['Nœud u', 'Nœud v', 'Coût'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Données exemple
        sample = [('A', 'B', '2'), ('B', 'C', '2'), ('C', 'D', '2'), ('A', 'D', '10'), ('A', 'C', '5')]
        for i, (u, v, c) in enumerate(sample):
            self.table.setItem(i, 0, QTableWidgetItem(u))
            self.table.setItem(i, 1, QTableWidgetItem(v))
            self.table.setItem(i, 2, QTableWidgetItem(c))
        
        data_layout.addWidget(self.table)
        
        # Boutons de gestion des lignes
        table_btns = QHBoxLayout()
        add_row_btn = QPushButton('+ Ajouter ligne')
        add_row_btn.clicked.connect(lambda: self.table.insertRow(self.table.rowCount()))
        table_btns.addWidget(add_row_btn)
        
        remove_row_btn = QPushButton('- Supprimer ligne')
        remove_row_btn.clicked.connect(lambda: self.table.removeRow(self.table.currentRow()) if self.table.currentRow() >= 0 else None)
        table_btns.addWidget(remove_row_btn)
        
        data_layout.addLayout(table_btns)
        data_group.setLayout(data_layout)
        left_layout.addWidget(data_group)
        
        # Bouton visualisation graphe
        self.show_graph_btn = QPushButton('📊 Visualiser le graphe')
        self.show_graph_btn.clicked.connect(self.show_graph)
        left_layout.addWidget(self.show_graph_btn)
        
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)
        
        # PARTIE DROITE: Résultats et logs
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        # Résultats principaux
        results_group = QGroupBox("Résultats de l'optimisation")
        results_layout = QVBoxLayout()
        
        self.result_label = QLabel('Statut: En attente...')
        result_font = QFont()
        result_font.setPointSize(11)
        result_font.setBold(True)
        self.result_label.setFont(result_font)
        results_layout.addWidget(self.result_label)
        
        # Tableau des résultats détaillés
        self.results_table = QTableWidget(0, 2)
        self.results_table.setHorizontalHeaderLabels(['Variable', 'Valeur'])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setMaximumHeight(200)
        results_layout.addWidget(self.results_table)
        
        results_group.setLayout(results_layout)
        right_layout.addWidget(results_group)
        
        # Zone de logs
        logs_group = QGroupBox("Logs d'exécution")
        logs_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(250)
        log_font = QFont("Courier New", 9)
        self.log_text.setFont(log_font)
        logs_layout.addWidget(self.log_text)
        
        clear_log_btn = QPushButton('🗑 Effacer les logs')
        clear_log_btn.clicked.connect(self.log_text.clear)
        logs_layout.addWidget(clear_log_btn)
        
        logs_group.setLayout(logs_layout)
        right_layout.addWidget(logs_group)
        
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)
        
        splitter.setSizes([600, 800])
        main_layout.addWidget(splitter)
        
        central.setLayout(main_layout)

    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Ouvrir fichier CSV', os.getcwd(), 'Fichiers CSV (*.csv)')
        if not path:
            return
        import pandas as pd
        try:
            df = pd.read_csv(path)
            self.log_text.append(f'📁 Chargement: {os.path.basename(path)}')
        except Exception as e:
            QMessageBox.critical(self, 'Erreur', f'Échec de lecture du CSV: {e}')
            return
        # Expect columns u,v,cost
        self.table.setRowCount(len(df))
        for i, row in df.iterrows():
            self.table.setItem(i, 0, QTableWidgetItem(str(row['u'])))
            self.table.setItem(i, 1, QTableWidgetItem(str(row['v'])))
            self.table.setItem(i, 2, QTableWidgetItem(str(row['cost'])))
        self.log_text.append(f'✓ {len(df)} arêtes chargées')

    def run_solver(self):
        # Read graph
        try:
            nodes, edges = table_to_graph_data(self.table)
            self.log_text.append(f'\n═══ NOUVELLE EXÉCUTION ═══')
            self.log_text.append(f'Nœuds: {", ".join(nodes)}')
            self.log_text.append(f'Arêtes: {len(edges)}')
        except Exception as e:
            QMessageBox.critical(self, 'Erreur', f'Données invalides: {e}')
            self.log_text.append(f'✗ ERREUR: {e}')
            return
            
        src = self.src_input.text().strip()
        tgt = self.tgt_input.text().strip()
        cps = [c.strip() for c in self.checkpoints_input.text().split(',') if c.strip()]
        
        self.log_text.append(f'Source: {src} → Cible: {tgt}')
        self.log_text.append(f'Checkpoints: {", ".join(cps)}')

        # Start worker thread
        if self.solver_thread is not None and self.solver_thread.isRunning():
            QMessageBox.warning(self, 'Solveur en cours', 'Le solveur est déjà en cours d\'exécution')
            return

        self.solver_thread = SolverThread(nodes, edges, src, tgt, cps)
        self.solver_thread.result_ready.connect(self.on_result)
        self.solver_thread.log.connect(self.on_log)
        self.solver_thread.error.connect(self.on_error)
        self.solver_thread.start()
        
        self.result_label.setText('⏳ Statut: Optimisation en cours...')
        self.results_table.setRowCount(0)
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_solver(self):
        if self.solver_thread is not None:
            self.solver_thread.request_stop()
            self.stop_btn.setEnabled(False)

    def on_result(self, objective, chosen_edges, details):
        self.result_label.setText(f'✓ Statut: OPTIMAL | Coût total: {objective:.2f}')
        self.last_solution_details = details
        
        # Remplir le tableau des résultats
        self.results_table.setRowCount(0)
        
        # Résumé
        self.results_table.insertRow(0)
        self.results_table.setItem(0, 0, QTableWidgetItem('Coût optimal'))
        self.results_table.setItem(0, 1, QTableWidgetItem(f'{objective:.2f}'))
        
        self.results_table.insertRow(1)
        self.results_table.setItem(1, 0, QTableWidgetItem('Temps de résolution'))
        self.results_table.setItem(1, 1, QTableWidgetItem(f'{details["solve_time"]:.3f} secondes'))
        
        self.results_table.insertRow(2)
        self.results_table.setItem(2, 0, QTableWidgetItem('Nombre d\'arêtes'))
        self.results_table.setItem(2, 1, QTableWidgetItem(str(details['num_edges_used'])))
        
        self.results_table.insertRow(3)
        self.results_table.setItem(3, 0, QTableWidgetItem('Checkpoints visités'))
        self.results_table.setItem(3, 1, QTableWidgetItem(', '.join(details['visited_checkpoints'])))
        
        # Détail des arêtes
        self.results_table.insertRow(4)
        self.results_table.setItem(4, 0, QTableWidgetItem('=== Arêtes sélectionnées ==='))
        self.results_table.setItem(4, 1, QTableWidgetItem(''))
        
        for i, (u, v, c) in enumerate(chosen_edges):
            row = 5 + i
            self.results_table.insertRow(row)
            self.results_table.setItem(row, 0, QTableWidgetItem(f'  Arête {i+1}: {u} → {v}'))
            self.results_table.setItem(row, 1, QTableWidgetItem(f'{c}'))
        
        # Visualiser automatiquement
        try:
            nodes, _ = table_to_graph_data(self.table)
            src = self.src_input.text().strip()
            tgt = self.tgt_input.text().strip()
            cps = [c.strip() for c in self.checkpoints_input.text().split(',') if c.strip()]
            
            img_path = draw_graph(chosen_edges, highlight_edges=chosen_edges, 
                                 source=src, target=tgt, checkpoints=cps)
            self.log_text.append(f'📊 Graphe solution sauvegardé: {img_path}')
        except Exception as e:
            self.log_text.append(f'Avertissement: visualisation échouée - {e}')
        
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def on_log(self, msg):
        self.log_text.append(msg)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def on_error(self, error_msg):
        self.result_label.setText(f'✗ Statut: ERREUR')
        QMessageBox.critical(self, 'Erreur d\'optimisation', error_msg)
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def show_graph(self):
        try:
            nodes, edges = table_to_graph_data(self.table)
            src = self.src_input.text().strip()
            tgt = self.tgt_input.text().strip()
            cps = [c.strip() for c in self.checkpoints_input.text().split(',') if c.strip()]
        except Exception as e:
            QMessageBox.critical(self, 'Erreur', f'Données invalides: {e}')
            return
        
        img_path = draw_graph(edges, source=src, target=tgt, checkpoints=cps)
        self.log_text.append(f'📊 Graphe complet sauvegardé: {img_path}')
        QMessageBox.information(self, 'Graphe', f'Graphe sauvegardé dans:\n{img_path}')
