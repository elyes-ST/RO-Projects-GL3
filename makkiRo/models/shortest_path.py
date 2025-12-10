"""
═══════════════════════════════════════════════════════════════════════════════
MODÉLISATION MATHÉMATIQUE - Chemin le moins cher avec point de contrôle
═══════════════════════════════════════════════════════════════════════════════

PROBLÈME:
    Trouver le chemin le moins coûteux entre une source et une cible qui passe
    par au moins un point de contrôle (checkpoint).

VARIABLES DE DÉCISION:
    • x_i ∈ {0,1}  pour i ∈ E (arêtes)
        x_i = 1 si l'arête i est utilisée dans le chemin optimal
        x_i = 0 sinon
    
    • z_c ∈ {0,1}  pour c ∈ CP (checkpoints)
        z_c = 1 si le checkpoint c est visité
        z_c = 0 sinon

FONCTION OBJECTIF:
    Minimiser: ∑(i∈E) cost_i × x_i
    
    Où cost_i est le coût de l'arête i

CONTRAINTES:

    1) Conservation du flot (pour chaque nœud n):
       ∑(arêtes sortant de n) x_i - ∑(arêtes entrant dans n) x_i = b_n
       
       Où b_n = { +1  si n = source
                  -1  si n = cible
                   0  sinon
       
       → Assure un chemin continu de la source à la cible

    2) Visite des checkpoints (pour chaque checkpoint c):
       a) ∑(arêtes incidentes à c) x_i ≥ z_c
          → Si z_c = 1, au moins une arête touche c
       
       b) ∑(arêtes incidentes à c) x_i ≤ M × z_c
          → Si z_c = 0, aucune arête ne touche c (Big-M)
       
       Où M = |E| (nombre d'arêtes, suffisamment grand)

    3) Au moins un checkpoint visité:
       ∑(c∈CP) z_c ≥ 1
       
       → Garantit qu'au moins un checkpoint est sur le chemin

TYPE DE PROBLÈME:
    PLNE (Programme Linéaire en Nombres Entiers)
    - Variables binaires uniquement
    - Contraintes linéaires
    - Fonction objectif linéaire

═══════════════════════════════════════════════════════════════════════════════
"""

from gurobipy import Model, GRB, GurobiError

def solve_shortest_path(nodes, edges, source, target, checkpoints, stop_flag=None, log=None):
    """
    Résout le problème du plus court chemin avec passage obligatoire par au moins un checkpoint.
    
    Args:
        nodes: iterable de node ids (hashable)
        edges: list de tuples (u, v, cost)
        source: node id de la source
        target: node id de la cible
        checkpoints: list de node ids (checkpoints)
        stop_flag: callable qui retourne True si l'exécution doit être arrêtée
        log: PyQt signal (callable) pour logger des messages

    Returns: 
        tuple: (objective_value, chosen_edges_list, solution_details)
        
    Raises:
        ValueError: Si les entrées sont invalides
        RuntimeError: Si le modèle est infaisable ou erreur Gurobi
    """
    # ═══════════════════════════════════════════════════════════════
    # VALIDATION DES DONNÉES D'ENTRÉE
    # ═══════════════════════════════════════════════════════════════
    
    if not nodes or not edges:
        raise ValueError("Les nœuds et arêtes ne peuvent pas être vides")
    
    if source not in nodes:
        raise ValueError(f"La source '{source}' n'existe pas dans les nœuds")
    
    if target not in nodes:
        raise ValueError(f"La cible '{target}' n'existe pas dans les nœuds")
    
    if source == target:
        raise ValueError("La source et la cible doivent être différentes")
    
    valid_checkpoints = [cp for cp in checkpoints if cp in nodes]
    if not valid_checkpoints:
        raise ValueError("Aucun checkpoint valide trouvé dans les nœuds")
    
    if log:
        log.emit(f'Validation OK: {len(nodes)} nœuds, {len(edges)} arêtes, {len(valid_checkpoints)} checkpoints')
        log.emit('Construction du modèle Gurobi...')

    # ═══════════════════════════════════════════════════════════════
    # PRÉPARATION DES DONNÉES
    # ═══════════════════════════════════════════════════════════════

    # ═══════════════════════════════════════════════════════════════
    # PRÉPARATION DES DONNÉES
    # ═══════════════════════════════════════════════════════════════

    # Map edges to IDs
    E = list(range(len(edges)))
    u = {i: edges[i][0] for i in E}
    v = {i: edges[i][1] for i in E}
    cost = {i: float(edges[i][2]) for i in E}

    # ═══════════════════════════════════════════════════════════════
    # CRÉATION DU MODÈLE GUROBI
    # ═══════════════════════════════════════════════════════════════
    
    try:
        m = Model('shortest_path_checkpoint')
        m.setParam('OutputFlag', 0)
        
    except GurobiError as e:
        raise RuntimeError(f"Erreur lors de la création du modèle Gurobi: {e}")

    # ═══════════════════════════════════════════════════════════════
    # VARIABLES DE DÉCISION
    # ═══════════════════════════════════════════════════════════════
    
    # x[i] = 1 si l'arête i est sélectionnée, 0 sinon
    x = m.addVars(E, vtype=GRB.BINARY, name='x')
    
    if log:
        log.emit(f'Variables x créées: {len(E)} variables binaires pour les arêtes')

    # ═══════════════════════════════════════════════════════════════
    # CONTRAINTES: CONSERVATION DU FLOT
    # ═══════════════════════════════════════════════════════════════

    # For each node, flow conservation: out - in = b
    # b = 1 for source, -1 for target, 0 otherwise
    b = {n: 0 for n in nodes}
    b[source] = 1
    b[target] = -1

    # Build flow constraints
    for node in nodes:
        expr = 0
        for i in E:
            if u[i] == node:
                expr += x[i]
            if v[i] == node:
                expr -= x[i]
        m.addConstr(expr == b[node], name=f'flow_{node}')
    
    if log:
        log.emit(f'Contraintes de conservation du flot: {len(nodes)} contraintes')

    # ═══════════════════════════════════════════════════════════════
    # VARIABLES ET CONTRAINTES: CHECKPOINTS
    # ═══════════════════════════════════════════════════════════════

    # z[cp] = 1 si le checkpoint cp est visité, 0 sinon
    z = {}
    bigM = len(edges)  # Big-M suffisamment grand
    
    for cp in valid_checkpoints:
        z[cp] = m.addVar(vtype=GRB.BINARY, name=f'z_{cp}')
        
        # Arêtes incidentes au checkpoint
        inc = []
        for i in E:
            if u[i] == cp or v[i] == cp:
                inc.append(x[i])
        
        if inc:
            # Si z[cp] = 1, au moins une arête incidente doit être sélectionnée
            m.addConstr(sum(inc) >= z[cp], name=f'visit_lb_{cp}')
            # Si z[cp] = 0, aucune arête incidente n'est sélectionnée
            m.addConstr(sum(inc) <= bigM * z[cp], name=f'visit_ub_{cp}')
        else:
            m.addConstr(z[cp] == 0)

    # ═══════════════════════════════════════════════════════════════
    # CONTRAINTE: AU MOINS UN CHECKPOINT VISITÉ
    # ═══════════════════════════════════════════════════════════════
    
    if z:
        m.addConstr(sum(z.values()) >= 1, name='at_least_one_cp')
        if log:
            log.emit(f'Contraintes checkpoints: {len(z)} checkpoints, au moins 1 visité')
    else:
        raise ValueError('No valid checkpoints in node list')

    # ═══════════════════════════════════════════════════════════════
    # FONCTION OBJECTIF
    # ═══════════════════════════════════════════════════════════════

    # Minimiser: ∑(i∈E) cost_i × x_i
    m.setObjective(sum(cost[i] * x[i] for i in E), GRB.MINIMIZE)
    
    if log:
        log.emit('Lancement de l\'optimisation...')

    # ═══════════════════════════════════════════════════════════════
    # OPTIMISATION
    # ═══════════════════════════════════════════════════════════════

    try:
        if stop_flag:
            # Callback pour interruption
            def callback(model, where):
                if where == GRB.Callback.MIP or where == GRB.Callback.MIPNODE:
                    if stop_flag():
                        model.terminate()
            m.optimize(callback)
        else:
            m.optimize()
    except GurobiError as e:
        raise RuntimeError(f"Erreur pendant l'optimisation: {e}")

    # ═══════════════════════════════════════════════════════════════
    # TRAITEMENT DES RÉSULTATS
    # ═══════════════════════════════════════════════════════════════

    if m.status == GRB.OPTIMAL:
        chosen = [edges[i] for i in E if x[i].x > 0.5]
        obj = m.objVal
        
        # Détails de la solution
        visited_checkpoints = [cp for cp in z if z[cp].x > 0.5]
        
        solution_details = {
            'objective': obj,
            'chosen_edges': chosen,
            'visited_checkpoints': visited_checkpoints,
            'num_edges_used': len(chosen),
            'all_variables': {
                'x': {i: x[i].x for i in E},
                'z': {cp: z[cp].x for cp in z}
            },
            'status': 'OPTIMAL',
            'solve_time': m.Runtime
        }
        
        if log:
            log.emit(f'Solution optimale trouvée! Coût: {obj:.2f}')
            log.emit(f'Checkpoints visités: {", ".join(visited_checkpoints)}')
            log.emit(f'Nombre d\'arêtes: {len(chosen)}')
        
        return obj, chosen, solution_details
        
    elif m.status == GRB.INTERRUPTED:
        if log:
            log.emit('Optimisation interrompue par l\'utilisateur')
        raise RuntimeError('Optimisation interrompue par l\'utilisateur')
        
    elif m.status in (GRB.INFEASIBLE, GRB.INF_OR_UNBD):
        if log:
            log.emit('Problème infaisable: aucun chemin valide trouvé')
        raise RuntimeError('Modèle infaisable: impossible de trouver un chemin de la source à la cible passant par au moins un checkpoint')
        
    else:
        raise RuntimeError(f'Gurobi terminé avec le statut {m.status}')
