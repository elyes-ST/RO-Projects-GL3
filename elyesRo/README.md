# 🚛 Gestion de Flotte Avancée V2.0

## 📋 Description

Application professionnelle de gestion de flotte avec interface PyQt5 moderne, optimisation Gurobi et visualisations élégantes.

---

## ✨ Fonctionnalités

### 🔧 CRUD Complet
- **Camions** - Ajouter, Modifier, Supprimer
- **Chauffeurs** - Ajouter, Modifier, Supprimer
- **Commandes** - Ajouter, Modifier, Supprimer

### 🎯 Optimisation
- Algorithme Gurobi pour minimiser les coûts
- Tournées multi-commandes
- Contraintes de capacité, compatibilité, permis
- Types de marchandises variés

### 📊 Visualisations
- **6 cartes de statistiques** colorées
- **Cartes détaillées** des tournées
- **Graphiques Matplotlib** professionnels
- **Détails texte** complets

---

## 🚀 Installation

### 1. Prérequis
```bash
Python 3.8+
```

### 2. Installer les Dépendances
```bash
pip install -r requirements.txt
```

### 3. Configurer Gurobi
- Obtenir une licence académique gratuite sur [gurobi.com](https://www.gurobi.com/academia/)
- Installer la licence : `grbgetkey VOTRE-CLE`

---

## 🎮 Utilisation

### Lancement Rapide
```bash
# Méthode 1 : Double-clic
LANCER_APP.bat

# Méthode 2 : Ligne de commande
python main.py
```

### Workflow
1. **Gérer les données** - Onglets Camions/Chauffeurs/Commandes
2. **Optimiser** - Onglet Optimisation → Bouton "🚀 OPTIMISER"
3. **Voir les résultats** - Onglet Résultats avec 4 visualisations

---

## 📁 Structure du Projet

```
GL3/
├── main.py                    # Point d'entrée
├── LANCER_APP.bat            # Lanceur rapide
├── requirements.txt          # Dépendances
│
├── 📚 Documentation/
│   ├── COMMENCER_ICI.txt
│   ├── GUIDE_DEMARRAGE.md
│   ├── GUIDE_CRUD.md
│   ├── GUIDE_VISUALISATIONS.md
│   ├── GUIDE_PYQT.md
│   └── PRESENTATION.md
│
└── src/
    ├── models/               # Modèles de données
    │   ├── truck.py
    │   ├── driver.py
    │   ├── order.py
    │   └── route.py
    │
    ├── services/             # Services métier
    │   ├── optimizer.py
    │   └── data_manager.py
    │
    ├── utils/                # Utilitaires
    │   ├── formatters.py
    │   └── validators.py
    │
    └── ui/                   # Interface PyQt5
        ├── main_window_pyqt.py
        ├── forms_pyqt.py
        └── visualizations_pyqt.py
```

---

## 🎨 Interface PyQt5

### Design Moderne
- En-tête élégant avec fond bleu foncé
- Boutons colorés avec effets hover
- Tableaux avec lignes alternées
- Cartes de statistiques avec bordures colorées
- Graphiques Matplotlib professionnels

### Style CSS
- Personnalisation complète
- Couleurs harmonieuses
- Coins arrondis
- Effets visuels

---

## 🎯 Fonctionnalités Avancées

### Optimisation
- **Variables** : x[t,d,o] pour affectation camion-chauffeur-commande
- **Objectif** : Minimiser coût total (carburant + main d'œuvre)
- **Contraintes** :
  - Capacité des camions
  - Compatibilité types marchandise/camion
  - Permis des chauffeurs
  - Max commandes par tournée
  - Disponibilité chauffeurs

### Types de Marchandises
- Standard
- Fragile
- Alimentaire
- Réfrigéré
- Liquide

### Types de Camions
- Standard
- Réfrigéré
- Citerne
- Benne
- Plateau

---

## 📊 Visualisations

### 1. Statistiques (6 cartes)
- 💰 Coût Total
- 🛣️ Distance Totale
- 🚛 Camions Utilisés
- 📊 Utilisation Moyenne
- 📦 Commandes
- 📈 Moy. Commandes/Camion

### 2. Tournées
- Cartes visuelles détaillées
- Itinéraires complets
- Statistiques par tournée
- Liste des commandes

### 3. Graphiques
- Graphique en barres Matplotlib
- Comparaison des distances
- Couleurs distinctes
- Valeurs affichées

### 4. Détails Texte
- Résultats complets
- Format professionnel
- Copie facile

---

## 💡 Données par Défaut

L'application inclut un jeu de données tunisien :
- **5 camions** (différents types)
- **5 chauffeurs** (différents permis)
- **8 commandes** (différentes villes)

---

## 🎓 Documentation

### Guides Disponibles
- **COMMENCER_ICI.txt** - Démarrage rapide (5 min)
- **GUIDE_DEMARRAGE.md** - Guide détaillé (15 min)
- **GUIDE_CRUD.md** - Gestion des données (10 min)
- **GUIDE_VISUALISATIONS.md** - Comprendre les résultats (10 min)
- **GUIDE_PYQT.md** - Interface PyQt5 (15 min)
- **PRESENTATION.md** - Support de présentation (20 min)

---

## 🛠️ Technologies

- **Python 3.8+**
- **PyQt5** - Interface graphique moderne
- **Gurobi** - Optimisation mathématique
- **Matplotlib** - Graphiques professionnels
- **NumPy** - Calculs numériques
- **Pandas** - Manipulation de données

---

## ✅ Tests

### Vérifier l'Installation
```bash
python main.py
```

### Tester les Fonctionnalités
1. CRUD - Ajouter/Modifier/Supprimer des données
2. Optimisation - Lancer une optimisation
3. Visualisations - Explorer les 4 sous-onglets

---

## 🐛 Dépannage

### PyQt5 non trouvé
```bash
pip install PyQt5
```

### Gurobi non configuré
- Vérifier la licence : `gurobi.sh` ou `gurobi.bat`
- Réinstaller : `pip install gurobipy`

### Erreur d'import
```bash
# Vérifier que vous êtes dans le bon dossier
cd GL3
python main.py
```

---

## 📝 Licence

Projet académique - Gestion de Flotte avec Optimisation

---

## 👥 Auteur

Projet de gestion de flotte avancée avec interface PyQt5

---

## 🎯 Points Forts

- ✅ **Interface moderne** PyQt5
- ✅ **CRUD complet** pour toutes les données
- ✅ **Optimisation avancée** avec Gurobi
- ✅ **4 types de visualisations** élégantes
- ✅ **Code bien structuré** et modulaire
- ✅ **Documentation complète** (7 guides)
- ✅ **Prêt pour présentation** professionnelle

---

**Application professionnelle de gestion de flotte ! 🚀**
