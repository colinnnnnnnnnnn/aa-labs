"""
Visual Representation of Dijkstra and Floyd-Warshall Algorithms
Shows step-by-step execution of both algorithms with graph visualization
"""

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation
import numpy as np
import time
import heapq
from collections import defaultdict


class AlgorithmVisualizer:
    """Visualize graph algorithms step by step"""
    
    def __init__(self, graph_data, title="Algorithm Visualization"):
        self.graph_data = graph_data  # (nodes, edges) where edges = [(u, v, weight), ...]
        self.title = title
        self.G = nx.DiGraph()
        self._build_graph()
    
    def _build_graph(self):
        """Build NetworkX graph from data"""
        nodes, edges = self.graph_data
        self.G.add_nodes_from(nodes)
        for u, v, w in edges:
            self.G.add_edge(u, v, weight=w)
    
    def visualize_dijkstra(self, source=0):
        """Visualize Dijkstra's algorithm step by step"""
        steps = self._dijkstra_steps(source)
        self._visualize_steps(steps, "Dijkstra's Algorithm", source)
    
    def visualize_floyd_warshall(self):
        """Visualize Floyd-Warshall algorithm"""
        steps = self._floyd_warshall_steps()
        self._visualize_floyd_warshall_steps(steps)
    
    def _dijkstra_steps(self, source):
        """Generate step-by-step execution of Dijkstra"""
        n = len(self.G.nodes())
        distances = {i: float('inf') for i in range(n)}
        distances[source] = 0
        visited = set()
        previous = {i: None for i in range(n)}
        pq = [(0, source)]
        
        steps = []
        edge_highlight = []
        
        # Initial state
        steps.append({
            'distances': distances.copy(),
            'visited': visited.copy(),
            'current': None,
            'pq': [(0, source)],
            'highlighted_edges': [],
            'description': f'Start: Source node {source}, all other distances = ∞'
        })
        
        while pq:
            current_dist, u = heapq.heappop(pq)
            
            if u in visited:
                continue
            
            visited.add(u)
            
            # Explore neighbors
            for v in self.G.neighbors(u):
                if v not in visited:
                    edge_weight = self.G[u][v]['weight']
                    new_dist = current_dist + edge_weight
                    
                    if new_dist < distances[v]:
                        distances[v] = new_dist
                        previous[v] = u
                        heapq.heappush(pq, (new_dist, v))
                        edge_highlight = [(u, v)]
                        
                        steps.append({
                            'distances': distances.copy(),
                            'visited': visited.copy(),
                            'current': u,
                            'pq': pq.copy(),
                            'highlighted_edges': edge_highlight,
                            'description': f'Relax edge ({u}→{v}): distance[{v}] = {new_dist}'
                        })
            
            steps.append({
                'distances': distances.copy(),
                'visited': visited.copy(),
                'current': u,
                'pq': pq.copy(),
                'highlighted_edges': [],
                'description': f'Mark node {u} as visited'
            })
        
        return steps
    
    def _floyd_warshall_steps(self):
        """Generate step-by-step execution of Floyd-Warshall"""
        nodes = sorted(list(self.G.nodes()))
        n = len(nodes)
        
        # Create distance matrix
        dist = {}
        for i in nodes:
            dist[i] = {}
            for j in nodes:
                if i == j:
                    dist[i][j] = 0
                elif self.G.has_edge(i, j):
                    dist[i][j] = self.G[i][j]['weight']
                else:
                    dist[i][j] = float('inf')
        
        steps = []
        
        # Initial state
        steps.append({
            'dist': {i: dist[i].copy() for i in dist},
            'k': -1,
            'i': -1,
            'j': -1,
            'description': 'Initialize: Distance matrix with direct edges'
        })
        
        # For each intermediate vertex
        for k in nodes:
            for i in nodes:
                for j in nodes:
                    if dist[i][k] != float('inf') and dist[k][j] != float('inf'):
                        old_dist = dist[i][j]
                        new_dist = dist[i][k] + dist[k][j]
                        
                        if new_dist < old_dist:
                            dist[i][j] = new_dist
                            
                            steps.append({
                                'dist': {ii: dist[ii].copy() for ii in dist},
                                'k': k,
                                'i': i,
                                'j': j,
                                'updated': True,
                                'description': f'Update dist[{i}][{j}] = {new_dist} (through {k})'
                            })
        
        # Final state
        steps.append({
            'dist': {i: dist[i].copy() for i in dist},
            'k': -1,
            'i': -1,
            'j': -1,
            'description': 'Complete: All shortest paths computed'
        })
        
        return steps
    
    def _visualize_steps(self, steps, title, source):
        """Visualize Dijkstra steps"""
        num_steps = len(steps)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle(f'{title} - Step-by-Step Visualization', fontsize=16, fontweight='bold')
        
        # Use spring layout for consistent positioning
        pos = nx.spring_layout(self.G, seed=42, k=2, iterations=50)
        
        def update(step_num):
            ax1.clear()
            ax2.clear()
            
            step = steps[step_num]
            
            # Draw graph on ax1
            ax1.set_title(f'Graph State (Step {step_num + 1}/{num_steps})', 
                         fontsize=12, fontweight='bold')
            
            # Node colors based on visited status
            node_colors = []
            for node in self.G.nodes():
                if node == source:
                    node_colors.append('#FFD700')  # Gold for source
                elif node in step['visited']:
                    node_colors.append('#90EE90')  # Light green for visited
                elif node == step.get('current'):
                    node_colors.append('#FF6B6B')  # Red for current
                else:
                    node_colors.append('#B0C4DE')  # Light blue for unvisited
            
            # Draw nodes
            nx.draw_networkx_nodes(self.G, pos, node_color=node_colors, 
                                  node_size=1000, ax=ax1)
            
            # Draw all edges
            nx.draw_networkx_edges(self.G, pos, edge_color='gray', 
                                  arrows=True, arrowsize=20, ax=ax1, width=1.5)
            
            # Highlight special edges
            if step.get('highlighted_edges'):
                nx.draw_networkx_edges(self.G, pos, edgelist=step['highlighted_edges'],
                                      edge_color='red', arrows=True, arrowsize=20, 
                                      ax=ax1, width=3)
            
            # Draw edge labels (weights)
            edge_labels = nx.get_edge_attributes(self.G, 'weight')
            nx.draw_networkx_edge_labels(self.G, pos, edge_labels, ax=ax1)
            
            # Draw node labels
            nx.draw_networkx_labels(self.G, pos, font_size=12, 
                                   font_weight='bold', ax=ax1)
            
            ax1.axis('off')
            
            # Draw distances table on ax2
            ax2.axis('off')
            ax2.set_title('Distances from Source', fontsize=12, fontweight='bold')
            
            # Create distance display
            distances_text = "Node | Distance\n"
            distances_text += "-----+-----------\n"
            
            for node in sorted(self.G.nodes()):
                dist = step['distances'][node]
                if dist == float('inf'):
                    distances_text += f"  {node}   | ∞\n"
                else:
                    distances_text += f"  {node}   | {dist}\n"
            
            # Add description
            description_text = f"\n{step['description']}\n"
            description_text += f"\nVisited: {sorted(step['visited'])}"
            
            full_text = distances_text + description_text
            
            ax2.text(0.1, 0.9, full_text, transform=ax2.transAxes,
                    fontsize=11, verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            # Legend
            legend_elements = [
                mpatches.Patch(facecolor='#FFD700', label='Source'),
                mpatches.Patch(facecolor='#90EE90', label='Visited'),
                mpatches.Patch(facecolor='#FF6B6B', label='Current'),
                mpatches.Patch(facecolor='#B0C4DE', label='Unvisited')
            ]
            ax2.legend(handles=legend_elements, loc='lower left', fontsize=10)
        
        # Create animation
        anim = FuncAnimation(fig, update, frames=num_steps, interval=1000, repeat=True)
        plt.tight_layout()
        plt.show()
    
    def _visualize_floyd_warshall_steps(self, steps):
        """Visualize Floyd-Warshall distance matrix evolution"""
        num_steps = len(steps)
        nodes = sorted(list(self.G.nodes()))
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('Floyd-Warshall Algorithm - Distance Matrix Evolution', 
                    fontsize=16, fontweight='bold')
        
        def format_value(val):
            if val == float('inf'):
                return '∞'
            elif val == 0:
                return '0'
            else:
                return str(int(val))
        
        def update(step_num):
            ax1.clear()
            ax2.clear()
            
            step = steps[step_num]
            dist = step['dist']
            
            # Create distance matrix display
            ax1.axis('off')
            ax1.set_title(f'Distance Matrix (Step {step_num + 1}/{num_steps})', 
                         fontsize=12, fontweight='bold')
            
            # Build matrix for display
            matrix_data = []
            row_labels = [str(i) for i in nodes]
            col_labels = [str(i) for i in nodes]
            
            for i in nodes:
                row = [format_value(dist[i][j]) for j in nodes]
                matrix_data.append(row)
            
            # Create table
            table = ax1.table(cellText=matrix_data, rowLabels=row_labels, 
                            colLabels=col_labels, cellLoc='center', loc='center',
                            colWidths=[0.08]*len(nodes), rowColours=['lightgray']*len(nodes))
            
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 2)
            
            # Highlight the current cell being updated
            if step.get('updated') and step['i'] >= 0:
                i_idx = nodes.index(step['i']) + 1  # +1 for row labels
                j_idx = nodes.index(step['j'])
                table[(i_idx, j_idx)].set_facecolor('#FFB6C1')
            
            # Highlight intermediate vertex column/row
            if step['k'] >= 0:
                k_idx = nodes.index(step['k'])
                # Highlight k column
                for i_idx, i in enumerate(nodes):
                    table[(i_idx + 1, k_idx)].set_facecolor('#FFFFCC')
                # Highlight k row
                for j_idx in range(len(nodes)):
                    table[(k_idx + 1, j_idx)].set_facecolor('#FFFFCC')
            
            # Information panel
            ax2.axis('off')
            ax2.set_title('Algorithm Progress', fontsize=12, fontweight='bold')
            
            info_text = step['description'] + "\n\n"
            
            if step['k'] >= 0:
                info_text += f"Intermediate Vertex (k): {step['k']}\n"
                if step['i'] >= 0:
                    info_text += f"Current Row (i): {step['i']}\n"
                    info_text += f"Current Column (j): {step['j']}\n"
            
            ax2.text(0.1, 0.9, info_text, transform=ax2.transAxes,
                    fontsize=11, verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        anim = FuncAnimation(fig, update, frames=num_steps, interval=500, repeat=True)
        plt.tight_layout()
        plt.show()
    
    def compare_final_results(self, source=0):
        """Show comparison of Dijkstra and Floyd-Warshall results"""
        
        # Dijkstra
        dijkstra_steps = self._dijkstra_steps(source)
        dijkstra_result = dijkstra_steps[-1]['distances']
        
        # Floyd-Warshall
        fw_steps = self._floyd_warshall_steps()
        fw_result = fw_steps[-1]['dist']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Algorithm Results Comparison', fontsize=14, fontweight='bold')
        
        # Dijkstra visualization
        pos = nx.spring_layout(self.G, seed=42, k=2, iterations=50)
        
        ax1.set_title(f'Dijkstra: Shortest Paths from Node {source}', fontweight='bold')
        nx.draw_networkx_nodes(self.G, pos, node_color='lightblue', 
                              node_size=1000, ax=ax1)
        nx.draw_networkx_edges(self.G, pos, edge_color='gray', 
                              arrows=True, arrowsize=15, ax=ax1, width=1.5)
        nx.draw_networkx_labels(self.G, pos, font_size=11, font_weight='bold', ax=ax1)
        
        # Draw edge labels
        edge_labels = nx.get_edge_attributes(self.G, 'weight')
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels, ax=ax1, font_size=9)
        
        # Add Dijkstra distances
        dijkstra_text = "Dijkstra Distances:\n"
        for node in sorted(self.G.nodes()):
            dist = dijkstra_result[node]
            if dist == float('inf'):
                dijkstra_text += f"  {node}: ∞\n"
            else:
                dijkstra_text += f"  {node}: {dist}\n"
        
        ax1.text(0.02, 0.98, dijkstra_text, transform=ax1.transAxes,
                fontsize=10, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        ax1.axis('off')
        
        # Floyd-Warshall results
        ax2.axis('off')
        ax2.set_title('Floyd-Warshall: All-Pairs Shortest Paths', fontweight='bold')
        
        nodes = sorted(list(self.G.nodes()))
        
        # Create matrix display
        matrix_data = []
        for i in nodes:
            row = []
            for j in nodes:
                val = fw_result[i][j]
                if val == float('inf'):
                    row.append('∞')
                else:
                    row.append(str(int(val)))
            matrix_data.append(row)
        
        row_labels = [f'From {i}' for i in nodes]
        col_labels = [f'To {j}' for j in nodes]
        
        table = ax2.table(cellText=matrix_data, rowLabels=row_labels, 
                         colLabels=col_labels, cellLoc='center', loc='center',
                         colWidths=[0.1]*len(nodes))
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        plt.tight_layout()
        plt.show()


def create_sample_graph_1():
    """Create a simple directed graph for demonstration"""
    nodes = [0, 1, 2, 3, 4]
    edges = [
        (0, 1, 4),
        (0, 2, 2),
        (1, 2, 1),
        (1, 3, 5),
        (2, 3, 8),
        (2, 4, 10),
        (3, 4, 2),
        (1, 4, 3),
    ]
    return nodes, edges


def create_sample_graph_2():
    """Create a medium-sized graph"""
    nodes = [0, 1, 2, 3, 4, 5]
    edges = [
        (0, 1, 7),
        (0, 2, 9),
        (0, 5, 14),
        (1, 2, 10),
        (1, 3, 15),
        (2, 3, 11),
        (2, 5, 2),
        (3, 4, 6),
        (4, 5, 9),
        (5, 4, 9),
    ]
    return nodes, edges


def main():
    """Main visualization program"""
    
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    print()
    
    # Create visualizer with single graph
    graph = create_sample_graph_1()
    visualizer = AlgorithmVisualizer(graph)

    print("Dijkstra's Algorithm - Step-by-Step Visualization")
    visualizer.visualize_dijkstra(source=0)

    print("Floyd-Warshall Algorithm - Distance Matrix Evolution")
    visualizer.visualize_floyd_warshall()


if __name__ == "__main__":
    main()
