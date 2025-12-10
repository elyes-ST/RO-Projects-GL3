"""
Point d'entrée de l'application de gestion de flotte
"""

import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window_pyqt import FleetManagementAppPyQt


def main():
    """Lance l'application"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Style moderne
    
    window = FleetManagementAppPyQt()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
