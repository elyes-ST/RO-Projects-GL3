import sys
from PyQt5.QtWidgets import QApplication
from InterfaceApp import OrdonnancementApp

if __name__ == '__main__':
    # Initialisation de l'application
    app = QApplication(sys.argv)
    app.setApplicationName("Logistique Pro - Séquençage Intelligent")
    app.setOrganizationName("Logistique Optimisation")
    
    # Créer et afficher la fenêtre principale
    main_window = OrdonnancementApp()
    main_window.show()
    
    sys.exit(app.exec_())
