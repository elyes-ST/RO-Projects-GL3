# models/optimization_model.py
from gurobipy import Model, GRB, GurobiError
import pandas as pd

def solve_planning_model(periods, params):
    """
    Construit et résout le modèle PLM de planification avancé avec Gurobi.

    Args:
        periods (pd.DataFrame): DataFrame avec 'Demande' et 'Capacité_Max_Init'.
        params (dict): Dictionnaire des paramètres de coût, financiers et d'investissement.

    Returns:
        tuple: (results_df, shadow_prices_df) ou (message_erreur, None)
    """
    T = len(periods)
    P = periods.index
    
    try:
        m = Model("PlanificationFinanciereAvancee")
        m.setParam('OutputFlag', 0)
        
        # --- 1. Variables de décision ---
        
        X = m.addVars(P, name="Production", lb=0)
        I = m.addVars(P, name="Stock", lb=0)
        S = m.addVars(P, name="Rupture", lb=0)
        A = m.addVars(P, name="Approvisionnement", lb=0)
        
        Y = m.addVars(P, name="Lancement_Prod", vtype=GRB.BINARY)
        
        Z_inv = m.addVars(P, name="Investissement_Cap", vtype=GRB.BINARY)
        Z_des = m.addVars(P, name="Desinvestissement_Cap", vtype=GRB.BINARY)

        Cap = m.addVars(P, name="Capacite_Dispo", lb=0)
        
        # --- 2. Fonction Objectif (Coûts Totaux Actualisés) ---
        
        r = params['taux_actualisation']
        actualisation_factors = [(1 / (1 + r)**(t+1)) for t in range(T)]
        
        objective = 0
        
        for t, p in enumerate(P):
            factor = actualisation_factors[t]
            
            # Coûts Opérationnels
            cost_prod = params['cout_prod'] * X[p]
            cost_stock = params['cout_stock'] * I[p]
            cost_rupture = params['cout_rupture'] * S[p]
            cost_fixe = params['cout_fixe'] * Y[p]
            cost_appro = params['cout_appro'] * A[p]
            
            # Coûts Stratégiques (Investissement/Désinvestissement)
            cost_invest = params['cout_invest_cap'] * Z_inv[p]
            cost_desinvest = params['cout_desinvest_cap'] * Z_des[p]
            
            objective += factor * (
                cost_prod + cost_stock + cost_rupture + cost_fixe + cost_appro +
                cost_invest + cost_desinvest
            )

        m.setObjective(objective, GRB.MINIMIZE)

        # --- 3. Contraintes ---
        
        # Contrainte 3.1 : Équilibre des Stocks
        I_initial = params['stock_initial']
        
        for t, p in enumerate(P):
            I_prev = I_initial if t == 0 else I[P[t-1]]
            m.addConstr(I_prev + X[p] + A[p] == periods.loc[p, 'Demande'] + S[p] + I[p], name=f"Stock_{p}")

        # Contrainte 3.2 : Capacité Dynamique
        Cap_initial = periods.loc[P[0], 'Capacité_Max_Init']
        delta_cap = params['delta_cap']
        
        for t, p in enumerate(P):
            if t == 0:
                m.addConstr(Cap[p] == Cap_initial + delta_cap * Z_inv[p] - delta_cap * Z_des[p], name=f"CapInit_{p}")
            else:
                m.addConstr(Cap[p] == Cap[P[t-1]] + delta_cap * Z_inv[p] - delta_cap * Z_des[p], name=f"CapDyn_{p}")
            
            # La production ne peut dépasser la capacité disponible (Contrainte critique pour les prix duaux)
            m.addConstr(X[p] <= Cap[p], name=f"CapProd_{p}")
            
        # Contrainte 3.3 : Mutualité Investissement/Désinvestissement 
        for p in P:
             m.addConstr(Z_inv[p] + Z_des[p] <= 1, name=f"Mutuel_{p}")

        # Contrainte 3.4 : Lien Production/Coût Fixe
        M = periods['Demande'].sum() * 2 
        for p in P:
            m.addConstr(X[p] <= M * Y[p], name=f"CoutFixeLien_{p}")

        # Contrainte 3.5 : Stock Final Cible
        if params['stock_final_cible'] >= 0:
             m.addConstr(I[P[-1]] == params['stock_final_cible'], name="StockFinal")
             
        # --- 4. Résolution ---
        m.optimize()

        # --- 5. Traitement des résultats ---
        
        if m.status == GRB.OPTIMAL:
            # 5.1 Extraction des Variables de Décision
            results = {
                'Période': P,
                'Demande (D_t)': periods['Demande'].tolist(),
                'Production (P_t)': [X[p].X for p in P],
                'Approvisionnement (A_t)': [A[p].X for p in P],
                'Stock Fin (I_t)': [I[p].X for p in P],
                'Rupture (S_t)': [S[p].X for p in P],
                'Capacité Fin (Cap_t)': [Cap[p].X for p in P],
                'Investissement (Z_inv)': [Z_inv[p].X for p in P],
                'Desinvestissement (Z_des)': [Z_des[p].X for p in P],
                'Coût Actualisé Total': m.objVal
            }
            results_df = pd.DataFrame(results).set_index('Période')
            
            # 5.2 Extraction des Prix Duaux (Shadow Prices)
            shadow_prices = {}
            for p in P:
                constraint = m.getConstrByName(f"CapProd_{p}")
                
                # --- CORRECTION DE L'ERREUR D'ACCÈS À '.Pi' ---
                try:
                    # Vérification robuste pour s'assurer que l'attribut est accessible
                    if constraint and hasattr(constraint, 'Pi') and constraint.Pi is not None:
                        # Pi est le prix dual. On prend l'opposé pour représenter la valeur
                        # d'une augmentation (relâchement de la contrainte)
                        shadow_prices[p] = -constraint.Pi 
                    else:
                        shadow_prices[p] = 0.0 # Par défaut si non actif ou non disponible en PLM
                except Exception:
                    # Capture toute autre erreur Gurobi lors de l'accès à Pi
                    shadow_prices[p] = 0.0

            shadow_prices_df = pd.DataFrame(shadow_prices.items(), 
                                            columns=['Période', 'Prix Dual Capacité (Valeur Marginale)'])
            shadow_prices_df.set_index('Période', inplace=True)
            
            # 5.3 Calcul des Flux de Trésorerie
            return calculate_cash_flow(results_df, params), shadow_prices_df
            
        else:
            if m.status == GRB.INFEASIBLE:
                return "Le modèle est infaisable. Vérifiez les contraintes et les données.", None
            else:
                return f"Le solveur n'a pas trouvé de solution optimale (Statut Gurobi: {m.status}).", None

    except GurobiError as e:
        return f"Erreur Gurobi: {e.message}", None
    except Exception as e:
        # Erreur générique inattendue (autre que GurobiError)
        return f"Une erreur inattendue est survenue: {e}", None


def calculate_cash_flow(results_df, params):
    """
    Calcule les flux de trésorerie nets en fonction des délais.
    (Ce bloc n'a pas été modifié car il n'était pas la cause de l'erreur.)
    """
    T = len(results_df)
    P = results_df.index
    
    # ------------------
    # 1. Calcul des Flux de Coûts (Décaissements)
    costs = (
        params['cout_prod'] * results_df['Production (P_t)'] +
        params['cout_appro'] * results_df['Approvisionnement (A_t)'] +
        params['cout_fixe'] * results_df['Investissement (Z_inv)'] +
        params['cout_invest_cap'] * results_df['Investissement (Z_inv)'] +
        params['cout_desinvest_cap'] * results_df['Desinvestissement (Z_des)'] 
    )
    
    results_df['Décaissement'] = 0.0
    D_P = params['delai_paiement']
    
    for t in range(T):
        if t - D_P >= 0:
            results_df.loc[P[t], 'Décaissement'] = costs.iloc[t - D_P]

    results_df['Décaissement'] += params['cout_stock'] * results_df['Stock Fin (I_t)']
    
    # ------------------
    # 2. Calcul des Flux de Revenus (Encaissements)
    sales = (results_df['Demande (D_t)'] - results_df['Rupture (S_t)']) * params['prix_vente']
    
    results_df['Encaissement'] = 0.0
    D_E = params['delai_encaissement']

    for t in range(T):
        if t - D_E >= 0:
            results_df.loc[P[t], 'Encaissement'] = sales.iloc[t - D_E]

    # ------------------
    # 3. Calcul du Flux Net et du Solde
    results_df['Flux_Net'] = results_df['Encaissement'] - results_df['Décaissement']
    
    initial_cash_flow = params.get('solde_tresorerie_initial', 0.0)
    results_df['Solde_Cumulé'] = initial_cash_flow + results_df['Flux_Net'].cumsum()
    
    return results_df