# 🚀 Projets de Recherche Opérationnelle - GL3 INSAT

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)](https://pypi.org/project/PyQt5/)
[![Gurobi](https://img.shields.io/badge/Gurobi-11.0+-red.svg)](https://www.gurobi.com/)
[![License](https://img.shields.io/badge/License-Academic-yellow.svg)](LICENSE)

## 📋 Vue d'Ensemble

Ce dépôt contient **5 projets complémentaires** de Recherche Opérationnelle développés dans le cadre du cours de GL3 à l'INSAT. Chaque projet résout un problème d'optimisation différent en utilisant **Gurobi** et propose une interface graphique moderne avec **PyQt5**.

---

## 🎯 Les 5 Projets

### 🚛 Projet 1 : Gestion de Flotte (Elyes)
**Problème :** Vehicle Routing Problem (VRP) avec contraintes multiples  
**Technologies :** PyQt5, Gurobi, Matplotlib  
**Fonctionnalités :**
- ✅ CRUD complet (Camions, Chauffeurs, Commandes)
- ✅ Optimisation VRP avec 8 types de contraintes
- ✅ 4 types de visualisations élégantes
- ✅ Diagnostic intelligent des erreurs

### 📊 Projet 2 : Plus Court Chemin (Makki)
**Problème :** Plus court chemin avec passage obligatoire par checkpoint  
**Technologies :** PyQt5, Gurobi, NetworkX, Matplotlib  
**Fonctionnalités :**
- ✅ Optimisation sur graphes
- ✅ Visualisation NetworkX
- ✅ Import/Export CSV
- ✅ Résolution en temps réel

### 🌐 Projet 3 : Réseau de Transport (Yassine)
**Problème :** Design optimal de réseau de transport  
**Technologies :** PyQt5, Gurobi, NetworkX, Matplotlib  
**Fonctionnalités :**
- ✅ Gestion entrepôts et clients
- ✅ Configuration des routes
- ✅ Visualisation de réseau
- ✅ Interface dark theme

### 💰 Projet 4 : Planification Financière (Aymen)
**Problème :** Optimisation production, stocks et investissements  
**Technologies :** PyQt5, Gurobi, Pandas, NumPy  
**Fonctionnalités :**
- ✅ Planification multi-période
- ✅ Gestion production et stocks
- ✅ Investissement en capacité
- ✅ Coûts actualisés

### ⏱️ Projet 5 : Ordonnancement de Camions (Ahmed)
**Problème :** Ordonnancement sur machines parallèles (quais)  
**Technologies :** PyQt5, Gurobi, Matplotlib  
**Fonctionnalités :**
- ✅ Ordonnancement sur quais
- ✅ Minimisation du Makespan
- ✅ Diagramme de Gantt
- ✅ Contraintes de séquencement

---

## 🚀 Démarrage Rapide

### Installation

```bash
# Cloner le dépôt
git clone https://github.com/VOTRE-USERNAME/RO-Projects-GL3.git
cd RO-Projects-GL3

# Installer les dépendances (Windows)
INSTALLER_DEPENDANCES.bat

# Ou manuellement
pip install -r requirements.txt
```

### Lancement

**Option 1 : Launcher (Recommandé)**
```bash
python launcher.py
```

**Option 2 : Lancement Direct**
```bash
# Projet 1
cd elyesRo && python main.py

# Projet 2
cd makkiRo && python main.py

# Projet 3
cd yassineRo && python main.py

# Projet 4
cd aymenRo && python main.py

# Projet 5
cd logistique && python main.py
```

---

## 📦 Prérequis

- **Python** 3.10+
- **PyQt5** 5.15+
- **Gurobi** 11.0+ (licence académique gratuite)
- **NetworkX** (pour projets 2 et 3)
- **Matplotlib** (pour visualisations)
- **Pandas** (pour projets 2 et 4)

### Installation de Gurobi

1. Téléchargez Gurobi : [gurobi.com](https://www.gurobi.com/downloads/)
2. Obtenez une licence académique gratuite
3. Installez le package Python :
```bash
pip install gurobipy
```
4. Activez votre licence :
```bash
grbgetkey VOTRE-CLE-LICENCE
```

---

## 📁 Structure du Projet

```
RO/
├── launcher.py                    # Interface de sélection des projets
├── requirements.txt               # Dépendances Python
├── .gitignore                     # Fichiers à ignorer
│
├── elyesRo/                       # Projet 1 - Gestion de Flotte
│   ├── main.py
│   ├── src/
│   └── Documentation/
│
├── makkiRo/                       # Projet 2 - Plus Court Chemin
│   ├── main.py
│   ├── ui/
│   └── models/
│
├── yassineRo/                     # Projet 3 - Réseau de Transport
│   ├── main.py
│   ├── ui/
│   └── model/
│
├── aymenRo/                       # Projet 4 - Planification Financière
│   ├── main.py
│   ├── ui/
│   └── models/
│
└── logistique/                    # Projet 5 - Ordonnancement
    ├── main.py
    ├── ModeleGurobi.py
    └── InterfaceApp.py
```

---

## 🎨 Interface Launcher

Le launcher offre une interface moderne pour choisir entre les 5 projets :

```
┌─────────────────────────────────────────────────────┐
│        Recherche Opérationnelle                     │
│        5 Projets • Gurobi & PyQt5                   │
├─────────────────────────────────────────────────────┤
│  [P1]    [P2]    [P3]    [P4]    [P5]              │
│ Elyes   Makki  Yassine  Aymen   Ahmed              │
└─────────────────────────────────────────────────────┘
```

---

## 📊 Comparaison des Projets

| Projet | Type | Variables | Contraintes | Objectif |
|--------|------|-----------|-------------|----------|
| **P1 - Elyes** | PLNE | 225 binaires | 8 types | Min coût transport |
| **P2 - Makki** | PLNE | 13 binaires | 3 types | Min coût chemin |
| **P3 - Yassine** | PLM | 6c + 6b | 4 types | Min coût réseau |
| **P4 - Aymen** | PLM | 15c + 9b | 6 types | Min coût actualisé |
| **P5 - Ahmed** | PLM | 3c + 9b | 6 types | Min Makespan |

*c = continues, b = binaires*

---

## 📚 Documentation

Chaque projet contient sa propre documentation détaillée :

- **Projet 1** : 6 fichiers de documentation technique
- **Projet 2** : Guide de présentation et améliorations
- **Projet 3** : README avec architecture
- **Projet 4** : Documentation du modèle
- **Projet 5** : README avec formulation mathématique

---

## 🛠️ Technologies

### Optimisation
- **Gurobi** : Solveur PLNE/PLM professionnel
- **Branch & Bound** : Algorithme d'optimisation exacte

### Interface
- **PyQt5** : Framework GUI moderne
- **Widgets personnalisés** : Cartes, graphiques, formulaires

### Visualisation
- **Matplotlib** : Graphiques et charts
- **NetworkX** : Visualisation de graphes

### Données
- **Pandas** : Manipulation de données
- **NumPy** : Calculs numériques
- **CSV** : Import/Export

---

## 👥 Équipe

| Membre | Projet | Domaine |
|--------|--------|---------|
| **Elyes Mlawah** | Projet 1 | Gestion de Flotte |
| **Makki Aloulou** | Projet 2 | Chemin Optimal |
| **Mohamed Yassine Kallel** | Projet 3 | Réseau de Transport |
| **Aymen Abid** | Projet 4 | Planification Financière |
| **Ahmed Loubiri** | Projet 5 | Ordonnancement |

**Classe :** GL3  
**Institution :** INSAT (Institut National des Sciences Appliquées et de Technologie)  
**Année :** 2025-2026

---

## 🐛 Résolution de Problèmes

### Erreur : Module non trouvé

```bash
pip install -r requirements.txt
```

### Erreur : Licence Gurobi

Obtenez une licence académique gratuite sur [gurobi.com/academia](https://www.gurobi.com/academia/)

### Le launcher ne trouve pas les projets

Vérifiez que la structure des dossiers correspond à celle décrite ci-dessus.

---

## 📄 Licence

Ce projet est développé dans un cadre académique à l'INSAT.

---

## 🎓 Contexte Académique

Ces projets ont été développés dans le cadre du cours de **Recherche Opérationnelle** en GL3 à l'INSAT. Ils démontrent :

- ✅ Maîtrise de la modélisation PLNE et PLM
- ✅ Utilisation avancée de Gurobi
- ✅ Développement d'interfaces PyQt5
- ✅ Résolution de problèmes variés d'optimisation
- ✅ Travail en équipe et documentation

---

## 🌟 Points Forts

- **Diversité** : 5 problèmes d'optimisation différents
- **Complémentarité** : VRP, Graphes, Réseaux, Finance, Ordonnancement
- **Professionnalisme** : Interfaces modernes et documentation complète
- **Maîtrise technique** : Gurobi, PyQt5, NetworkX, Matplotlib
- **Launcher unifié** : Interface élégante pour tous les projets

---

## 🚀 Contribution

Ce projet est académique. Pour toute suggestion ou amélioration, n'hésitez pas à ouvrir une issue.

---

**Développé avec ❤️ par l'équipe GL3 INSAT**
