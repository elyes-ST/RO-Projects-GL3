import gurobipy as gp
from gurobipy import GRB


class TransportOptimizer:
    def __init__(self):
        self.model = None

    def solve(self, nodes_data, arcs_data):
        """
        nodes_data: list of dicts {'id': 'A', 'demand': -10} (Neg=Demand, Pos=Supply)
        arcs_data: list of dicts {'source': 'A', 'target': 'B', 'fixed_cost': 100, 'var_cost': 2, 'capacity': 50}
        """
        try:
            # Création du modèle
            m = gp.Model("Transport_Network_Design")

            # Variables
            # x[i,j]: Flux continu sur l'arc (i,j)
            # y[i,j]: Variable binaire (1 si l'arc est construit, 0 sinon)
            x = {}
            y = {}

            arcs_indices = []

            for arc in arcs_data:
                u = arc["source"]
                v = arc["target"]
                arcs_indices.append((u, v))

                # Variable de décision de construction (Binaire)
                y[u, v] = m.addVar(vtype=GRB.BINARY, name=f"build_{u}_{v}")

                # Variable de flux (Continue)
                x[u, v] = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"flow_{u}_{v}")

            # Fonction Objectif : Minimiser (Coûts Fixes * y) + (Coûts Variables * x)
            m.setObjective(
                gp.quicksum(
                    arc["fixed_cost"] * y[arc["source"], arc["target"]]
                    for arc in arcs_data
                )
                + gp.quicksum(
                    arc["var_cost"] * x[arc["source"], arc["target"]]
                    for arc in arcs_data
                ),
                GRB.MINIMIZE,
            )

            # Contraintes

            # 1. Conservation du flux pour chaque nœud
            # Somme(flux_sortant) - Somme(flux_entrant) = Supply/Demand du noeud
            node_map = {n["id"]: n["demand"] for n in nodes_data}

            for node_id, demand in node_map.items():
                m.addConstr(
                    gp.quicksum(x[node_id, v] for u, v in arcs_indices if u == node_id)
                    - gp.quicksum(
                        x[u, node_id] for u, v in arcs_indices if v == node_id
                    )
                    == demand,
                    name=f"flow_bal_{node_id}",
                )

            # 2. Capacité et Liaison (Linking Constraints)
            # Flux <= Capacité * y (Si y=0, flux=0. Si y=1, flux <= Capacité)
            for arc in arcs_data:
                u, v = arc["source"], arc["target"]
                cap = arc["capacity"]
                m.addConstr(x[u, v] <= cap * y[u, v], name=f"cap_{u}_{v}")

            # Résolution
            m.optimize()

            if m.status == GRB.OPTIMAL:
                result_arcs = []
                for arc in arcs_data:
                    u, v = arc["source"], arc["target"]
                    if y[u, v].X > 0.5:  # Si construit
                        result_arcs.append(
                            {
                                "source": u,
                                "target": v,
                                "flow": x[u, v].X,
                                "capacity": arc["capacity"],
                                "fixed_cost": arc["fixed_cost"],
                            }
                        )
                return {
                    "status": "Optimal",
                    "obj_val": m.objVal,
                    "built_arcs": result_arcs,
                }
            else:
                return {
                    "status": "Infeasible/Unbounded",
                    "obj_val": 0,
                    "built_arcs": [],
                }

        except gp.GurobiError as e:
            return {"status": f"Error: {e}", "obj_val": 0, "built_arcs": []}
