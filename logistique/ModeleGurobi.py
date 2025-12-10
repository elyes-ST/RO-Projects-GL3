import gurobipy as gp
from gurobipy import GRB
import numpy as np

def resoudre_ordonnancement_avance(N, M, p, r, d, prep, a, C_swap):
    """
    Résout le modèle PLNE d'ordonnancement de camions sur M quais avec préférences et temps de préparation.

    Paramètres:
    N, M: Nombre de camions et de quais.
    p: Temps de traitement (chargement).
    r: Date de disponibilité.
    d: Date d'échéance.
    prep: Temps de préparation.
    a: Matrice d'affectation autorisée (N x M), doit être une liste de listes ou un numpy array convertible.
    C_swap: Coût de pénalité pour les affectations non autorisées.
    """
    if N == 0 or M == 0:
        return 0, 0, "Aucun camion ou quai à planifier."
        
    try:
        m = gp.Model("Ordonnancement_Avance_Logistique")
        m.Params.OutputFlag = 0  # Supprimer les logs Gurobi

        # Grande constante L
        L = sum(p) + max(r) + max(prep) + 100

        # --- 2. Variables de Décision ---
        S = m.addVars(N, vtype=GRB.CONTINUOUS, name="Start")
        Cmax = m.addVar(vtype=GRB.CONTINUOUS, name="Cmax")
        P_cost = m.addVar(vtype=GRB.CONTINUOUS, name="PenaltyCost")
        
        x = m.addVars(N, M, vtype=GRB.BINARY, name="Affectation")
        # Utiliser un dictionnaire pour y pour simplifier l'itération des indices
        indices_y = [(i, j) for i in range(N) for j in range(N) if i != j]
        y = m.addVars(indices_y, vtype=GRB.BINARY, name="Precedence") 

        # --- 3. Fonction Objectif (Minimiser Cmax + Coût de Pénalité * P_cost) ---
        m.setObjective(Cmax + C_swap * P_cost, GRB.MINIMIZE)

        # --- 4. Contraintes ---

        # 1. Chaque camion est sur un seul quai
        m.addConstrs((x.sum(i, '*') == 1 for i in range(N)), name="Affectation_Unique")

        # 2. et 3. Contrainte de préférence/restriction de quai (x_ik <= a_ik) et calcul de P_cost
        cost_pen = gp.LinExpr()
        for i in range(N):
            for k in range(M):
                # Si a[i, k] == 0, l'affectation est interdite, x[i, k] doit être 0.
                if a[i][k] == 0:
                     # Si x[i, k] est 1, cela ajoute 1 au coût de pénalité
                     cost_pen += x[i, k] 
        m.addConstr(P_cost == cost_pen, name="Calcul_Penalite")

        # 4. Heure de début >= Date de disponibilité + Temps de préparation
        m.addConstrs((S[i] >= r[i] + prep[i] for i in range(N)), name="Disponibilite_Prepa")

        # 6. Cmax >= Heure d'achèvement (S_i + p_i)
        m.addConstrs((Cmax >= S[i] + p[i] for i in range(N)), name="Cmax_Definition")

        # 5. Contraintes de non-chevauchement sur le même quai (i != j)
        for i in range(N):
            for j in range(i + 1, N):
                for k in range(M):
                    # i précède j (S_j >= S_i + p_i)
                    m.addConstr(S[j] >= S[i] + p[i] - L * (1 - y[i, j]) - L * (2 - x[i, k] - x[j, k]),
                                name=f"Precedence_1_{i}_{j}_{k}")
                    
                    # j précède i (S_i >= S_j + p_j)
                    m.addConstr(S[i] >= S[j] + p[j] - L * (1 - y[j, i]) - L * (2 - x[i, k] - x[j, k]),
                                name=f"Precedence_2_{i}_{j}_{k}")

                    # Soit i précède j, soit j précède i si sur même quai
                    m.addConstr(y[i, j] + y[j, i] >= x[i, k] + x[j, k] - 1,
                                name=f"Necessite_Precedence_{i}_{j}_{k}")

        # --- 5. Optimisation ---
        m.optimize()

        # --- 6. Extraction des résultats ---
        if m.status == GRB.OPTIMAL:
            Cmax_optimal = Cmax.X
            P_cost_optimal = P_cost.X
            solution = []
            
            for i in range(N):
                quai_affecte = -1
                for k in range(M):
                    if x[i, k].X > 0.5:
                        quai_affecte = k + 1
                        break
                
                # Le temps d'achèvement est S_i + p_i
                fin_i = S[i].X + p[i]
                retard_i = max(0, fin_i - d[i])
                
                solution.append({
                    "Camion": i + 1,
                    "Quai": quai_affecte,
                    "Debut_Chargement": S[i].X,
                    "Fin_Operation": fin_i,
                    "Retard": retard_i,
                    "Cout_Penalite": sum(1 for k in range(M) if x[i, k].X > 0.5 and a[i][k] == 0)
                })
            
            return Cmax_optimal, P_cost_optimal, solution
        
        if m.status == GRB.INFEASIBLE:
            return None, None, "Problème infaisable. Vérifiez les contraintes (e.g., restrictions de quai ou dates de disponibilité)."
        
        return None, None, f"Problème non résolu à l'optimum. Statut: {m.status}"

    except gp.GurobiError as e:
        return None, None, f"Erreur Gurobi: {e}"
    except Exception as e:
        return None, None, f"Erreur: {e}"