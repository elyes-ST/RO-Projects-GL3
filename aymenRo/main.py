# main.py
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import OptimizationApp
from data.data_manager import generate_example_data

if __name__ == "__main__":
    # Générer les données d'exemple si elles n'existent pas
    generate_example_data()
    
    app = QApplication(sys.argv)
    ex = OptimizationApp()
    ex.show()
    sys.exit(app.exec_())