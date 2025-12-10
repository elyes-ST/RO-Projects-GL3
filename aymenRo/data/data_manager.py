import pandas as pd
import numpy as np
import os

def load_period_data(file_path='data_example.csv'):
    """
    Charge les données de demande (D_t) et de capacité (Cap_t)
    à partir d'un fichier CSV.
    """
    try:
        df = pd.read_csv(file_path, sep=';', index_col='Période')
        
        required_cols = ['Demande', 'Capacité_Max_Init']
        if not all(col in df.columns for col in required_cols):
            raise ValueError("Le fichier CSV doit contenir les colonnes 'Période', 'Demande' et 'Capacité_Max_Init'.")
            
        return df
    except FileNotFoundError:
        return f"Erreur: Le fichier {file_path} est introuvable."
    except Exception as e:
        return f"Erreur lors du chargement des données: {e}"

def generate_example_data(file_path='data_example.csv', num_periods=12):
    """Génère un fichier CSV d'exemple pour l'horizon de 12 mois."""
    if os.path.exists(file_path):
        return
        
    data = {
        'Période': [f'Mois {i+1}' for i in range(num_periods)],
        # Demande saisonnière
        'Demande': [int(x) for x in np.linspace(3000, 4500, 6).tolist() + np.linspace(4200, 3000, 6).tolist()],
        # Capacité initiale (peut être sujette à investissement)
        'Capacité_Max_Init': [4000] * 12
    }
    df = pd.DataFrame(data)
    df.set_index('Période', inplace=True)
    df.to_csv(file_path, sep=';')
    print(f"Fichier '{file_path}' généré.")

if __name__ == '__main__':
    generate_example_data()