from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import networkx as nx
import matplotlib.pyplot as plt

class NetworkCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        plt.style.use('dark_background')
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#2D2D2D')
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('#2D2D2D')
        super().__init__(self.fig)
        self.setParent(parent)

        # Set modern matplotlib parameters
        plt.rcParams['font.family'] = 'Segoe UI'
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.labelcolor'] = 'white'
        plt.rcParams['xtick.color'] = 'white'
        plt.rcParams['ytick.color'] = 'white'

    def plot_solution(self, nodes_data, results):
        self.axes.clear()
        self.axes.set_facecolor('#2D2D2D')

        G = nx.DiGraph()

        # 1. Add nodes safely (handling duplicates)
        unique_nodes = {n['id']: n for n in nodes_data if n['id']}

        colors = []
        labels = {}
        node_sizes = []

        for nid, n in unique_nodes.items():
            G.add_node(nid)
            demand = n['demand']
            labels[nid] = f"{nid}\n({demand:+.0f})"

            # Enhanced color scheme
            if demand > 0:
                colors.append('#4CAF50')  # Green for supply
                node_sizes.append(800)
            elif demand < 0:
                colors.append('#f44336')  # Red for demand
                node_sizes.append(800)
            else:
                colors.append('#9E9E9E')  # Gray for neutral
                node_sizes.append(600)

        if len(G.nodes) == 0:
            self.axes.text(0.5, 0.5, 'No nodes to display', ha='center', va='center',
                          transform=self.axes.transAxes, color='white', fontsize=12)
            self.axes.set_title("Network Architecture", color='white', fontsize=14, fontweight='bold')
            self.axes.axis('off')
            self.draw()
            return

        # 2. Enhanced layout
        pos = nx.spring_layout(G, seed=42, k=2, iterations=50)

        # 3. Draw Nodes with enhanced styling
        node_list = list(G.nodes())
        ordered_colors = []
        ordered_sizes = []
        for nid in node_list:
            demand = unique_nodes[nid]['demand']
            if demand > 0:
                ordered_colors.append('#4CAF50')
                ordered_sizes.append(800)
            elif demand < 0:
                ordered_colors.append('#f44336')
                ordered_sizes.append(800)
            else:
                ordered_colors.append('#9E9E9E')
                ordered_sizes.append(600)

        nx.draw_networkx_nodes(G, pos, ax=self.axes, nodelist=node_list,
                              node_color=ordered_colors, node_size=ordered_sizes,
                              edgecolors='white', linewidths=2)

        # Enhanced labels
        nx.draw_networkx_labels(G, pos, labels, ax=self.axes, font_size=9,
                               font_color='white', font_weight='bold')

        # 4. Draw Arcs with modern styling
        if results and results.get('status') == 'Optimal' and 'built_arcs' in results:
            for arc in results['built_arcs']:
                u, v = arc['source'], arc['target']

                if u in G.nodes and v in G.nodes:
                    flow = arc['flow']
                    cap = arc['capacity']
                    utilization = flow / cap if cap > 0 else 0

                    # Dynamic edge styling based on utilization
                    if utilization < 0.8:
                        edge_color = '#4CAF50'  # Green for good utilization
                        width = 2 + utilization * 3
                    elif utilization < 1.0:
                        edge_color = '#FF9800'  # Orange for high utilization
                        width = 3 + utilization * 2
                    else:
                        edge_color = '#f44336'  # Red for over capacity
                        width = 5

                    # Draw the edge
                    nx.draw_networkx_edges(
                        G, pos,
                        edgelist=[(u, v)],
                        ax=self.axes,
                        width=width,
                        edge_color=edge_color,
                        arrowstyle='->',
                        arrowsize=20,
                        alpha=0.8
                    )

                    # Add flow/capacity label
                    mid_x = (pos[u][0] + pos[v][0]) / 2
                    mid_y = (pos[u][1] + pos[v][1]) / 2
                    self.axes.text(mid_x, mid_y, f"{flow:.0f}/{cap:.0f}",
                                  color='white', fontweight='bold', fontsize=8,
                                  ha='center', va='center',
                                  bbox=dict(boxstyle="round,pad=0.3",
                                           facecolor=edge_color, alpha=0.7))

        # Enhanced title and styling
        title_color = '#2196F3' if (results and results.get('status') == 'Optimal') else '#FF9800'
        self.axes.set_title("Network Architecture", color=title_color,
                           fontsize=14, fontweight='bold', pad=20)
        self.axes.axis('off')

        # Add legend
        self.add_legend()

        self.draw()

    def add_legend(self):
        # Add a small legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4CAF50',
                      markersize=10, label='Supply Node'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#f44336',
                      markersize=10, label='Demand Node'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#9E9E9E',
                      markersize=8, label='Neutral Node'),
        ]

        if hasattr(self, 'legend'):
            self.legend.remove()

        self.legend = self.axes.legend(handles=legend_elements, loc='upper right',
                                     fontsize=8, facecolor='#424242', edgecolor='white',
                                     labelcolor='white')
        self.legend.get_frame().set_alpha(0.8)
