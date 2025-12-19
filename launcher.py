"""
Interface de Lancement - Sélection de Projet RO
Permet de choisir entre les deux projets de Recherche Opérationnelle
"""

import sys
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon


class ProjectLauncher(QMainWindow):
    """Interface de sélection de projet"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 Launcher - Projets Recherche Opérationnelle")
        
        # Taille responsive basée sur l'écran
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        width = min(1700, int(screen.width() * 0.88))
        height = min(750, int(screen.height() * 0.75))
        
        # Centrer la fenêtre
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        
        self.setGeometry(x, y, width, height)
        self.setMinimumSize(1400, 700)
        
        self.setup_ui()
        self.apply_style()
    
    def setup_ui(self):
        """Configure l'interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(35, 20, 35, 20)
        
        # En-tête
        header = self.create_header()
        layout.addWidget(header)
        
        # Spacer
        layout.addSpacing(10)
        
        # Tous les projets sur une seule ligne
        projects_layout = QHBoxLayout()
        projects_layout.setSpacing(15)
        
        # Projet Elyes
        elyes_card = self.create_project_card(
            "01 • ELYES",
            "Gestion de Flotte Avancée",
            [
                "• Interface PyQt5 moderne",
                "• CRUD complet",
                "• Optimisation VRP",
                "• Visualisations élégantes",
                "• Diagnostic intelligent"
            ],
            "#6366f1",
            "#4f46e5",
            lambda: self.launch_project("elyesRo")
        )
        projects_layout.addWidget(elyes_card)
        
        # Projet Makki
        makki_card = self.create_project_card(
            "02 • MAKKI",
            "Plus Court Chemin",
            [
                "• Chemin avec checkpoint",
                "• Optimisation Gurobi",
                "• Visualisation NetworkX",
                "• Import/Export CSV",
                "• Résolution temps réel"
            ],
            "#8b5cf6",
            "#7c3aed",
            lambda: self.launch_project("makkiRo")
        )
        projects_layout.addWidget(makki_card)
        
        # Projet Yassine
        yassine_card = self.create_project_card(
            "03 • YASSINE",
            "Réseau de Transport",
            [
                "• Design de réseau optimal",
                "• Gestion nœuds/routes",
                "• Optimisation Gurobi",
                "• Visualisation NetworkX",
                "• Interface dark theme"
            ],
            "#06b6d4",
            "#0891b2",
            lambda: self.launch_project("yassineRo")
        )
        projects_layout.addWidget(yassine_card)
        
        # Projet Aymen
        aymen_card = self.create_project_card(
            "04 • AYMEN",
            "Planification Financière",
            [
                "• Production & stocks",
                "• Investissement capacité",
                "• Optimisation Gurobi",
                "• Coûts actualisés",
                "• Interface PyQt5"
            ],
            "#10b981",
            "#059669",
            lambda: self.launch_project("aymenRo")
        )
        projects_layout.addWidget(aymen_card)
        
        # Projet Ahmed
        ahmed_card = self.create_project_card(
            "05 • AHMED",
            "Ordonnancement de Camions",
            [
                "• Ordonnancement sur quais",
                "• Machines parallèles",
                "• Optimisation Gurobi",
                "• Diagramme de Gantt",
                "• Interface PyQt5"
            ],
            "#f59e0b",
            "#d97706",
            lambda: self.launch_project("ahmedRo")
        )
        projects_layout.addWidget(ahmed_card)
        
        layout.addLayout(projects_layout)
        
        # Spacer
        layout.addStretch()
        
        # Footer
        footer_widget = QWidget()
        footer_widget.setStyleSheet("border-radius: 8px;")
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setSpacing(5)
        
        footer = QLabel("Sélectionnez un projet pour commencer")
        footer.setStyleSheet("""
            font-size: 10.5pt;
            font-weight: 500;
            color: #475569;
            padding: 3px;
            border-radius: 6px;
        """)
        footer.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(footer)         
        layout.addWidget(footer_widget)
    
    def create_header(self):
        """Crée l'en-tête"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                border-radius: 12px;
                padding: 20px 20px 15px 20px;
            }
        """)
        
        layout = QVBoxLayout(header)
        layout.setSpacing(10)
        
        
        
        # Titre
        title = QLabel("Recherche Opérationnelle")
        title.setStyleSheet("""
            font-size: 30pt;
            font-weight: 700;
            color: #1e293b;
            letter-spacing: -1px;
            border-radius: 8px;
        """)
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        layout.addWidget(title)
        
        # Sous-titre
        subtitle = QLabel("5 Projets Recherche Opérationnelle • Gurobi & PyQt5")
        subtitle.setStyleSheet("""
            font-size: 11pt;
            font-weight: 400;
            color: #64748b;
            margin-top: 3px;
            border-radius: 8px;
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        
        return header
    
    def create_project_card(self, title, subtitle, features, color1, color2, launch_func):
        """Crée une carte de projet"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                min-width: 200px;
                max-width: 260px;
            }}
            QFrame:hover {{
                background: white;
                border: 1px solid {color1};
                border-radius: 16px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Badge numéro
        number = title.split("•")[0].strip()
        badge_num = QLabel(number)
        badge_num.setStyleSheet(f"""
            font-size: 9pt;
            font-weight: 700;
            color: {color1};
            background: rgba(99, 102, 241, 0.08);
            padding: 4px 10px;
            border-radius: 10px;
            letter-spacing: 1px;
        """)
        badge_num.setMaximumWidth(60)
        layout.addWidget(badge_num)
        
        layout.addSpacing(6)
        
        # Titre du projet
        project_name = title.split("•")[1].strip() if "•" in title else title
        title_label = QLabel(project_name)
        title_label.setStyleSheet(f"""
            font-size: 16pt;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 3px;
            border-radius: 6px;
        """)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Sous-titre
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("""
            font-size: 9.5pt;
            font-weight: 400;
            color: #64748b;
            margin-bottom: 8px;
            border-radius: 6px;
        """)
        subtitle_label.setWordWrap(True)
        layout.addWidget(subtitle_label)
        
        # Fonctionnalités
        features_widget = QWidget()
        features_widget.setStyleSheet("border-radius: 8px;")
        features_layout = QVBoxLayout(features_widget)
        features_layout.setSpacing(4)
        features_layout.setContentsMargins(0, 6, 0, 6)
        
        for feature in features:
            # Container pour chaque feature avec icône
            feature_container = QWidget()
            feature_container.setStyleSheet("border-radius: 5px;")
            feature_hlayout = QHBoxLayout(feature_container)
            feature_hlayout.setContentsMargins(0, 0, 0, 0)
            feature_hlayout.setSpacing(12)
            
            # Icône check
            icon = QLabel("✓")
            icon.setStyleSheet(f"""
                font-size: 10pt;
                font-weight: 700;
                color: {color1};
                min-width: 18px;
                max-width: 18px;
                border-radius: 9px;
            """)
            icon.setAlignment(Qt.AlignCenter)
            feature_hlayout.addWidget(icon)
            
            # Texte de la feature
            feature_text = feature.replace("•", "").strip()
            feature_label = QLabel(feature_text)
            feature_label.setStyleSheet("""
                font-size: 9.5pt;
                color: #475569;
                font-weight: 400;
                border-radius: 5px;
            """)
            feature_label.setWordWrap(True)
            feature_hlayout.addWidget(feature_label, 1)
            
            features_layout.addWidget(feature_container)
        
        layout.addWidget(features_widget)
        
        # Spacer
        layout.addStretch()
        
        # Bouton de lancement
        launch_btn = QPushButton("Lancer le projet →")
        launch_btn.setStyleSheet(f"""
            QPushButton {{
                background: {color1};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 18px;
                font-size: 10pt;
                font-weight: 600;
                letter-spacing: 0.3px;
            }}
            QPushButton:hover {{
                background: {color2};
                border-radius: 10px;
            }}
            QPushButton:pressed {{
                background: {color1};
                border-radius: 10px;
                padding: 13px 17px 11px 19px;
            }}
        """)
        launch_btn.clicked.connect(launch_func)
        layout.addWidget(launch_btn)
        
        return card
    
    def launch_project(self, project_name):
        """Lance le projet sélectionné"""
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        if project_name == "elyesRo":
            project_path = os.path.join(base_path, "elyesRo")
            main_file = os.path.join(project_path, "main.py")
        elif project_name == "makkiRo":
            project_path = os.path.join(base_path, "makkiRo")
            main_file = os.path.join(project_path, "main.py")
        elif project_name == "yassineRo":
            project_path = os.path.join(base_path, "yassineRo")
            main_file = os.path.join(project_path, "main.py")
        elif project_name == "aymenRo":
            project_path = os.path.join(base_path, "aymenRo")
            main_file = os.path.join(project_path, "main.py")
        elif project_name == "ahmedRo":
            project_path = os.path.join(base_path, "ahmedRo")
            main_file = os.path.join(project_path, "main.py")
        else:
            return
        
        # Vérifier que le fichier existe
        if not os.path.exists(main_file):
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "❌ Erreur",
                f"Le fichier main.py n'existe pas dans:\n{project_path}"
            )
            return
        
        # Lancer le projet dans un nouveau processus
        try:
            if sys.platform == "win32":
                # Windows
                subprocess.Popen(
                    [sys.executable, main_file],
                    cwd=project_path,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                # Linux/Mac
                subprocess.Popen(
                    [sys.executable, main_file],
                    cwd=project_path
                )
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "❌ Erreur de Lancement",
                f"Impossible de lancer le projet:\n{str(e)}"
            )
    
    def apply_style(self):
        """Applique le style global"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8fafc, stop:1 #f1f5f9);
            }
            QWidget {
                font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
            }
        """)


def main():
    """Point d'entrée de l'application"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    launcher = ProjectLauncher()
    launcher.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
