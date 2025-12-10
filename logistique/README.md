# 🚚 Séquençage des Camions sur les Quais (PLNE Avancée)

Ce document explique le modèle de **Programmation Linéaire en Nombres Entiers (PLNE)** utilisé pour optimiser l'affectation et le séquencement de $N$ camions sur $M$ quais de chargement (machines parallèles) en logistique.

## 1\. 🎯 Objectif du Modèle

Le modèle vise à trouver la meilleure affectation et le meilleur ordre de passage des camions sur les quais pour minimiser un objectif hybride, combinant la **durée totale de production** ($C_{\max}$, ou Makespan) et le **coût des pénalités** liées au non-respect des contraintes d'affectation spécifiques.


$$\min Z = C_{\max} + C_{swap} \cdot P_{cost}$$

| Symbole | Description |
| :---: | :--- |
| $C_{\max}$ | Temps d'achèvement maximal du dernier camion. |
| $P_{cost}$ | Nombre total d'affectations non autorisées (pénalité binaire). |
| $C_{swap}$ | Coût unitaire associé à chaque affectation non autorisée. |

## 2\. 🧩 Composants du Modèle

### A. Paramètres d'Entrée

Les données définies par l'utilisateur pour chaque camion $i$ et quai $k$:

| Symbole | Description | Impact |
| :---: | :--- | :--- |
| $p_i$ | Temps de traitement/chargement. | Détermine la durée de l'opération. |
| $r_i$ | Date de disponibilité du camion. | Contraint l'heure de début ($S_i$). |
| $d_i$ | Date d'échéance souhaitée. | Utilisée pour calculer le retard $T_i$ (dans l'analyse des résultats). |
| $prep_i$ | Temps de préparation incompressible. | Augmente le temps minimal avant le début du chargement. |
| $a_{ik}$ | Matrice binaire (1=Autorisé, 0=Interdit). | Force l'affectation à respecter les restrictions de quai (température, taille, etc.). |
| $L$ | Grande constante (Big $M$). | Utilisée pour les contraintes de séquencement logiques. |

### B. Variables de Décision

Les inconnues que le solveur Gurobi doit déterminer :

| Symbole | Type | Rôle |
| :---: | :--- | :--- |
| $C_{\max}$ | Continue | La valeur à minimiser. |
| $P_{cost}$ | Continue | Coût total des affectations non autorisées. |
| $S_i$ | Continue | **Heure de début du chargement** du camion $i$. |
| $x_{ik}$ | Binaire | **Affectation** : $1$ si le camion $i$ est sur le quai $k$. |
| $y_{ij}$ | Binaire | **Séquencement** : $1$ si le camion $i$ précède le camion $j$ sur le **même quai**. |

## 3\. ⚖️ Contraintes (Le Cœur du PLNE)

Les contraintes garantissent la faisabilité de la solution :

### 3.1. Affectation des Camions

1.  **Unique Affectation :** Chaque camion doit être affecté à **un et un seul** quai.
    $$\sum_{k=1}^M x_{ik} = 1 \quad \forall i$$

2.  **Respect des Restrictions :** Si un camion $i$ n'est pas autorisé sur le quai $k$ ($a_{ik}=0$), il ne peut pas y être affecté ($x_{ik}=0$).
    $$x_{ik} \le a_{ik} \quad \forall i, k$$
    *(Le terme $C_{swap} \cdot P_{cost}$ dans la fonction objectif pénalise fortement toute violation, garantissant le respect de cette restriction.)*

### 3.2. Contraintes de Temps

3.  **Heure de Début :** Le chargement ($S_i$) ne peut commencer qu'après que le camion soit disponible ($r_i$) **ET** que sa préparation soit terminée ($prep_i$).
    $$S_i \ge r_i + prep_i \quad \forall i$$

4.  **Makespan :** Le temps total ($C_{\max}$) doit être supérieur ou égal à l'heure de fin de tous les camions ($S_i + p_i$).
    $$C_{\max} \ge S_i + p_i \quad \forall i$$

### 3.3. Contraintes de Séquencement (Non-Chevauchement)

Ces contraintes utilisent la technique du *Big M* ($L$) pour garantir que deux camions affectés au même quai ne se chevauchent jamais.

5.  **Précédence $i \to j$ :** Si $i$ et $j$ sont sur le même quai $k$ (i.e., $x_{ik}=1$ et $x_{jk}=1$) ET $i$ précède $j$ ($y_{ij}=1$), alors l'heure de début de $j$ doit être $\ge$ l'heure de fin de $i$.
    $$S_j \ge (S_i + p_i) - L(1 - y_{ij}) - L(2 - x_{ik} - x_{jk}) \quad \forall i < j, \forall k$$

6.  **Précédence Réciproque :** Pour deux camions $i$ et $j$ sur le même quai, un seul ordre est possible.
    $$y_{ij} + y_{ji} \ge x_{ik} + x_{jk} - 1 \quad \forall i < j, \forall k$$

-----

## 🛠️ Exemple de Test pour `README.md`

Ce fichier `README.md` présente un scénario simple pour tester et comprendre les résultats du modèle.

# Application d'Ordonnancement Logistique (PyQt / Gurobi)

## 📖 Problématique

Optimiser l'affectation et le séquencement de camions sur des quais de chargement pour minimiser la durée totale des opérations ($C_{\max}$), tout en respectant les contraintes d'indisponibilité, de préparation et d'affectation spécifique des quais.

## 🧪 Scénario de Test Simple

Nous considérons **3 camions** à séquencer sur **2 quais** (M=2). Le coût de pénalité ($C_{swap}$) est fixé à **1000** pour garantir qu'aucune affectation non autorisée n'est choisie.

### 1. Données d'Entrée

| Camion | Temps Traitement (p) | Date Dispo (r) | Date Échéance (d) | Temps Prépa (prep) |
| :---: | :---: | :---: | :---: | :---: |
| **C1** | 10 | 0 | 25 | 2 |
| **C2** | 8 | 5 | 20 | 1 |
| **C3** | 6 | 0 | 18 | 0 |

### 2. Restrictions d'Affectation ($a_{ik}$)

La matrice indique si le camion $i$ est autorisé (1) ou interdit (0) sur le quai $k$.

| Camion | Quai 1 | Quai 2 |
| :---: | :---: | :---: |
| **C1** | 1 (Autorisé) | **0 (Interdit)** |
| **C2** | 1 (Autorisé) | 1 (Autorisé) |
| **C3** | 1 (Autorisé) | 1 (Autorisé) |

### 3. Résultat Attendu de l'Optimisation

L'objectif est d'atteindre le $C_{\max}$ le plus bas possible.

* **Contrainte critique :** C1 **DOIT** utiliser le Quai 1.
* **Quai 1 :** C1 (durée 10) doit passer. Les autres camions (C2, C3) sont en compétition pour le temps restant.
* **Quai 2 :** C2 (durée 8) et C3 (durée 6) se disputent le quai.

#### Solution Optimale (PLNE Résolu)

| Métrique | Valeur |
| :---: | :---: |
| **$C_{\max}$ (Optimal)** | **18.00** |
| **Coût Pénalité ($P_{cost}$)** | **0** |
| **Objectif Z (Total)** | **18.00** |

#### Détail du Séquencement

| Camion | Quai Affecté | Début Chargement ($S_i$) | Fin Opération ($C_i$) | Retard ($T_i$) |
| :---: | :---: | :---: | :---: | :---: |
| **C1** | 1 | 2.00 *($r_1+prep_1$)* | 12.00 | 0.00 |
| **C2** | 2 | 6.00 *($r_2+prep_2$)* | 14.00 | 0.00 |
| **C3** | 1 | 12.00 | **18.00** | 0.00 |

### 4. Interprétation du Gantt

1.  **Quai 1 :** C1 commence à 2 (dispo + prépa), finit à 12. C3 suit immédiatement à 12 et finit à 18. **(Cmax = 18)**.
2.  **Quai 2 :** C2 commence à 6 (dispo + prépa), finit à 14.
3.  Le temps final est déterminé par C3 à **18.00**.

Le modèle a minimisé le temps sans générer de pénalité ni de retard.
