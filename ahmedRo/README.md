# 🚚 Logistique Pro - Séquençage Intelligent des Camions

Application d'optimisation logistique utilisant la Programmation Linéaire en Nombres Entiers (PLNE) pour le séquençage de camions sur des quais de chargement.

## 🎨 Fonctionnalités Principales

### 1. Interface Moderne et Élégante ✨

#### Design Sombre Professionnel

- **Thème sombre complet** pour réduire la fatigue oculaire
- **Palette de couleurs harmonieuse** avec des accents verts (#4CAF50)
- **Effets visuels modernes** : ombres, bordures arrondies, animations
- **Typographie optimisée** avec Segoe UI pour une meilleure lisibilité

#### Boutons Interactifs

- **Boutons personnalisés** avec effets hover et pressed
- **Icônes émojis** pour une identification rapide des actions
- **Curseur pointeur** pour une meilleure UX
- **États désactivés** visuellement distincts

### 2. Fonctionnalités Avancées 🚀

#### Gestion des Données

- ✅ **Charger un exemple** : Données prédéfinies pour tester rapidement
- 💾 **Sauvegarder** : Export des données en JSON avec timestamp
- 📤 **Exporter les résultats** : Rapport détaillé en format texte
- 🔄 **Réinitialiser** : Effacer toutes les données avec confirmation

#### Validation et Feedback

- ⚡ **Validation en temps réel** des entrées numériques
- 💡 **Messages d'aide contextuels** dans chaque section
- 🎯 **Tooltips informatifs** sur tous les contrôles
- 📊 **Indicateur de statut** en temps réel avec codes couleur
- ⏳ **Barre de progression** pendant l'optimisation

### 3. Visualisations Complètes 📊

#### 5 Types de Diagrammes Automatiques

L'application génère automatiquement **5 visualisations différentes** après chaque optimisation :

1. **📈 Diagramme de Gantt** (Onglet 3)

   - Planning visuel complet des opérations
   - Barres de chargement et de préparation
   - Marqueurs de deadlines et retards
   - Légende par camion avec couleurs distinctes

2. **⚙️ Charge de Travail par Quai** (Onglet 4)

   - Graphique en barres comparant les quais
   - Détection des déséquilibres de charge
   - Valeurs numériques affichées

3. **⏰ Retards par Camion** (Onglet 4)

   - Code couleur : vert (à temps) / rouge (en retard)
   - Identification rapide des problèmes
   - Magnitude des retards

4. **⏱️ Décomposition du Temps** (Onglet 5)

   - Analyse détaillée par camion
   - 4 composantes : disponibilité, préparation, attente, chargement
   - Identification des inefficacités

5. **🥧 Répartition de la Charge** (Onglet 5)
   - Diagramme circulaire (camembert)
   - Distribution en pourcentage
   - Vue d'ensemble de l'équilibre

👉 **Voir [VISUALISATIONS.md](VISUALISATIONS.md) pour le guide détaillé**

#### Widget de Statistiques

Panel dédié affichant en temps réel :

- ⏱️ **Makespan (Cmax)** : Durée totale optimale
- ⚠️ **Coût Pénalité** : Nombre de violations
- 💰 **Coût Total (Z)** : Objectif optimisé
- 📈 **Taux d'Utilisation** : Efficacité des quais
- ⏰ **Retards Totaux** : Somme des retards

#### Diagramme de Gantt Amélioré

- 🎨 **Palette de couleurs distincte** pour chaque camion
- 📍 **Marqueurs de deadline** en jaune pointillé
- ⚠️ **Hachures rouges** pour les retards
- 🔧 **Barres de préparation** semi-transparentes
- 📝 **Labels clairs** sur chaque opération
- 🌟 **Légende interactive** par camion
- 🎭 **Style sombre cohérent** avec l'interface

#### Tableau de Résultats Enrichi

- ✅ **Colonne statut** avec indicateurs visuels
- 🎨 **Alternance de couleurs** pour faciliter la lecture
- 📏 **Colonnes auto-ajustables**
- 🎯 **Headers avec icônes** pour identification rapide

### 4. Améliorations Techniques 🛠️

#### Interface Utilisateur

- **SpinBox/DoubleSpinBox** au lieu de LineEdit pour les nombres
- **QSplitter** pour redimensionner dynamiquement les panneaux
- **GroupBox** pour organiser visuellement les sections
- **Layout optimisés** avec espacement et marges cohérents

#### Gestion de l'État

- Stockage de la solution actuelle pour export/rafraîchissement
- Activation/désactivation intelligente des boutons
- Messages de statut avec auto-effacement après 3 secondes

#### Code Optimisé

- Classes réutilisables (ModernButton, MplCanvas, StatsWidget)
- Séparation des responsabilités
- Gestion d'erreurs robuste
- Commentaires détaillés

### 5. Expérience Utilisateur Améliorée 🎯

#### Workflow Intuitif

1. **Configuration rapide** avec l'exemple prédéfini
2. **Modification facile** des paramètres avec SpinBox
3. **Visualisation en temps réel** du statut
4. **Navigation par onglets** claire et logique
5. **Export simple** des résultats

#### Messages et Alertes

- 💬 **Dialogues informatifs** avec contexte
- ⚠️ **Validations avant actions critiques** (effacement)
- ✅ **Confirmations des actions réussies**
- ❌ **Messages d'erreur détaillés**

## 📦 Installation et Utilisation

### Prérequis

```bash
pip install pyqt5 numpy matplotlib gurobipy
```

### Lancement de l'Application

**Linux/Mac:**

```bash
python main.py
```

**Windows:**

```bash
LANCER_APP.bat
```

## 🎓 Guide d'Utilisation Rapide

### 1. Charger un Exemple

- Cliquez sur **"📂 Charger Exemple"** pour des données de test
- L'exemple inclut 3 camions et 3 quais avec restrictions

### 2. Personnaliser les Données

- Ajustez le nombre de quais avec le SpinBox
- Modifiez le coût de pénalité selon vos besoins
- Ajoutez/supprimez des camions avec les boutons ➕/➖
- Remplissez les tableaux :
  - **Propriétés** : temps, disponibilités, échéances
  - **Restrictions** : 1 = autorisé, 0 = interdit

### 3. Optimiser

- Cliquez sur **"🚀 Lancer l'Optimisation"**
- La barre de progression s'affiche pendant le calcul
- Les résultats apparaissent automatiquement

### 4. Analyser les Résultats

- **Onglet Résultats** : Métriques et tableau détaillé
- **Panneau Statistiques** : Vue synthétique des KPIs
- **Onglet Gantt** : Visualisation du planning

### 5. Exporter

- **💾 Sauvegarder** : Enregistrer les données d'entrée (JSON)
- **📤 Exporter** : Générer un rapport des résultats (TXT)

## 📊 Fonctionnalités Clés

| Fonctionnalité         | Statut |
| ---------------------- | ------ |
| Thème sombre           | ✅     |
| Boutons stylisés       | ✅     |
| Tooltips               | ✅     |
| SpinBox pour nombres   | ✅     |
| Statistiques visuelles | ✅     |
| Export résultats       | ✅     |
| Sauvegarde JSON        | ✅     |
| Exemples prédéfinis    | ✅     |
| Barre de progression   | ✅     |
| Statut en temps réel   | ✅     |
| Gantt interactif       | ✅     |
| Validation entrées     | ✅     |

## 🚀 Améliorations Futures Possibles

1. **Import de fichiers CSV/Excel** pour les données
2. **Graphiques supplémentaires** (histogrammes, courbes)
3. **Comparaison de solutions** multiples
4. **Mode clair/sombre** basculable
5. **Rapports PDF** avec graphiques
6. **Historique des optimisations**
7. **Paramètres de Gurobi personnalisables**
8. **Mode multi-langues** (FR/EN)

## 📝 Notes Techniques

### Compatibilité

- Python 3.7+
- PyQt5
- Matplotlib 3.0+
- NumPy
- Gurobi Optimizer

### Performance

- Interface fluide même avec 20+ camions
- Optimisation Gurobi performante
- Rendu Gantt optimisé avec Matplotlib

### Structure du Code

```
logistique/
├── InterfaceApp.py     # Interface graphique PyQt5
├── ModeleGurobi.py     # Modèle PLNE avec Gurobi
├── main.py             # Lanceur principal
├── LANCER_APP.bat      # Script Windows
├── README.md           # Cette documentation
└── requirements.txt    # Dépendances Python
```

## 🎯 Points Forts

✅ **Interface moderne et attirante**
✅ **Workflow utilisateur optimisé**
✅ **Visualisations de données claires**
✅ **Fonctionnalités pratiques**
✅ **Code structuré et documenté**
✅ **Expérience utilisateur fluide**

---

**Développé avec ❤️ pour une logistique optimisée !**
