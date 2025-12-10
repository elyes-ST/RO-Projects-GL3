import sys
from PyQt5.QtWidgets import QApplication, QTableWidgetItem
from InterfaceApp import OrdonnancementApp

if __name__ == '__main__':
    # Initialisation de l'application
    app = QApplication(sys.argv)
    main_window = OrdonnancementApp()
    
    # --- Configuration par défaut pour un exemple simple ---
    
    # Mettre 3 quais
    main_window.quais_input.setText("3") 
    main_window.update_tables_structure() # Synchroniser la structure pour 3 quais
    
    # Ajouter 2 camions supplémentaires (il y en a déjà 1 par défaut)
    main_window.add_truck_row() 
    main_window.add_truck_row() 
    
    # Données d'exemple (à entrer dans l'interface, ici c'est pour l'initialisation)
    # Camion 1: (p=10, r=0, d=15, prep=2)
    # Camion 2: (p=8, r=0, d=25, prep=5)
    # Camion 3: (p=12, r=5, d=20, prep=1)
    
    data_exemple = [
        ["10", "0", "15", "2"],
        ["8", "0", "25", "5"],
        ["12", "5", "20", "1"],
    ]
    
    # Remplissage des données de base
    for i in range(main_window.camions_table.rowCount()):
        for j in range(main_window.camions_table.columnCount()):
            main_window.camions_table.setItem(i, j, QTableWidgetItem(data_exemple[i][j]))

    # Exemple de restrictions (1 = Autorisé / 0 = Interdit)
    # Camion 1 interdit sur Quai 3 (0, 2)
    main_window.affectation_table.setItem(0, 2, QTableWidgetItem("0")) 
    # Camion 3 interdit sur Quai 1 (2, 0)
    main_window.affectation_table.setItem(2, 0, QTableWidgetItem("0")) 
    
    # --- Lancement de l'application ---
    main_window.show()
    sys.exit(app.exec_())