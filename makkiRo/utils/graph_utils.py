import networkx as nx
import matplotlib.pyplot as plt
import os
from datetime import datetime

def table_to_graph_data(table_widget):
    """Extrait les données du graphe depuis le QTableWidget"""
    rows = table_widget.rowCount()
    edges = []
    nodes = set()
    for r in range(rows):
        item_u = table_widget.item(r, 0)
        item_v = table_widget.item(r, 1)
        item_c = table_widget.item(r, 2)
        if not item_u or not item_v or not item_c:
            continue
        u = item_u.text().strip()
        v = item_v.text().strip()
        if not u or not v:
            continue
        try:
            c = float(item_c.text())
        except ValueError:
            continue
        edges.append((u, v, c))
        nodes.add(u)
        nodes.add(v)
    return list(nodes), edges

def draw_graph(edges, highlight_edges=None, source=None, target=None, checkpoints=None):
    """
    Dessine un graphe avec mise en évidence des différents types de nœuds.
    
    Args:
        edges: Liste des arêtes (u, v, cost)
        highlight_edges: Arêtes à mettre en évidence (solution)
        source: Nœud source (en vert)
        target: Nœud cible (en rouge)
        checkpoints: Liste des nœuds checkpoints (en jaune)
    
    Returns:
        Chemin vers l'image générée
    """
    G = nx.DiGraph()
    for u, v, c in edges:
        G.add_edge(u, v, weight=c)

    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Préparer les listes de nœuds par catégorie
    all_nodes = list(G.nodes())
    source_nodes = [source] if source and source in all_nodes else []
    target_nodes = [target] if target and target in all_nodes else []
    checkpoint_nodes = [cp for cp in (checkpoints or []) if cp in all_nodes]
    
    # Nœuds normaux (ni source, ni target, ni checkpoint)
    special = set(source_nodes + target_nodes + checkpoint_nodes)
    normal_nodes = [n for n in all_nodes if n not in special]
    
    # Dessiner les nœuds par catégorie
    if normal_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=normal_nodes, 
                              node_color='lightblue', node_size=800, 
                              label='Nœud normal', ax=ax)
    
    if source_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=source_nodes, 
                              node_color='#4CAF50', node_size=1000, 
                              label='Source', ax=ax)
    
    if target_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=target_nodes, 
                              node_color='#f44336', node_size=1000, 
                              label='Cible', ax=ax)
    
    if checkpoint_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=checkpoint_nodes, 
                              node_color='#FFC107', node_size=900, 
                              label='Checkpoint', ax=ax)
    
    # Labels des nœuds
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold', ax=ax)
    
    # Dessiner les arêtes
    edge_labels = {(u, v): f'{d["weight"]:.1f}' for u, v, d in G.edges(data=True)}
    
    if highlight_edges:
        # Arêtes non sélectionnées (grises)
        other_edges = [(u, v) for u, v, _ in edges if (u, v, _) not in highlight_edges]
        if other_edges:
            nx.draw_networkx_edges(G, pos, edgelist=other_edges, 
                                  edge_color='gray', width=1.5, 
                                  alpha=0.3, arrows=True, 
                                  arrowsize=15, ax=ax)
        
        # Arêtes sélectionnées (bleues, épaisses)
        highlight_edge_list = [(u, v) for u, v, _ in highlight_edges]
        if highlight_edge_list:
            nx.draw_networkx_edges(G, pos, edgelist=highlight_edge_list, 
                                  edge_color='#2196F3', width=4, 
                                  arrows=True, arrowsize=20, 
                                  label='Chemin optimal', ax=ax)
    else:
        # Toutes les arêtes normales
        nx.draw_networkx_edges(G, pos, edgelist=list(G.edges()), 
                              edge_color='gray', width=2, 
                              arrows=True, arrowsize=15, ax=ax)
    
    # Labels des arêtes
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, 
                                 font_size=10, ax=ax)
    
    # Légende
    ax.legend(loc='upper left', fontsize=10)
    
    # Titre
    if highlight_edges:
        total_cost = sum(c for _, _, c in highlight_edges)
        ax.set_title(f'Solution optimale - Coût total: {total_cost:.2f}', 
                    fontsize=14, fontweight='bold')
    else:
        ax.set_title('Graphe complet', fontsize=14, fontweight='bold')
    
    ax.axis('off')
    plt.tight_layout()
    
    # Sauvegarder dans data/graphs
    graphs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'graphs')
    os.makedirs(graphs_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if highlight_edges:
        filename = f'solution_{timestamp}.png'
    else:
        filename = f'graph_{timestamp}.png'
    
    filepath = os.path.join(graphs_dir, filename)
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    return filepath
