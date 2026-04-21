"""
Dynamic Programming: Dijkstra and Floyd-Warshall Algorithms
Lab 4: Empirical Analysis on Sparse and Dense Graphs
"""

import time
import random
import heapq
import numpy as np
import matplotlib.pyplot as plt
from prettytable import PrettyTable
import sys


class GraphGenerator:
    """Generate sparse and dense graphs for testing"""
    
    def __init__(self, num_nodes, seed=42):
        self.num_nodes = num_nodes
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
    
    def generate_sparse_graph(self):
        """Generate a sparse graph with O(n) edges"""
        # Create adjacency matrix with INF for no edges
        graph = [[float('inf')] * self.num_nodes for _ in range(self.num_nodes)]
        
        # Diagonal is 0 (distance from node to itself)
        for i in range(self.num_nodes):
            graph[i][i] = 0
        
        # Add sparse edges: approximately 2*n edges
        num_edges = max(self.num_nodes - 1, 2 * self.num_nodes)
        edges_added = 0
        attempts = 0
        max_attempts = num_edges * 10
        
        while edges_added < num_edges and attempts < max_attempts:
            i = random.randint(0, self.num_nodes - 1)
            j = random.randint(0, self.num_nodes - 1)
            
            if i != j and graph[i][j] == float('inf'):
                weight = random.randint(1, 100)
                graph[i][j] = weight
                edges_added += 1
            
            attempts += 1
        
        return graph
    
    def generate_dense_graph(self):
        """Generate a dense graph with ~n^2/4 edges"""
        graph = [[float('inf')] * self.num_nodes for _ in range(self.num_nodes)]
        
        # Diagonal is 0
        for i in range(self.num_nodes):
            graph[i][i] = 0
        
        # Add edges with approximately 50% probability
        for i in range(self.num_nodes):
            for j in range(self.num_nodes):
                if i != j and random.random() < 0.5:
                    graph[i][j] = random.randint(1, 100)
        
        return graph


class DijkstraAlgorithm:
    """Dijkstra's algorithm implementation using dynamic programming"""
    
    @staticmethod
    def solve(graph, source=0):
        """
        Dijkstra's algorithm using a min-heap (Fibonacci heap simulation)
        Time Complexity: O((V + E) log V)
        """
        n = len(graph)
        
        # Initialize distances and visited set
        distances = [float('inf')] * n
        distances[source] = 0
        visited = [False] * n
        
        # Priority queue: (distance, node)
        pq = [(0, source)]
        
        while pq:
            current_dist, u = heapq.heappop(pq)
            
            if visited[u]:
                continue
            
            visited[u] = True
            
            # Relax edges (DP: optimal substructure)
            for v in range(n):
                if graph[u][v] != float('inf') and not visited[v]:
                    new_dist = current_dist + graph[u][v]
                    
                    if new_dist < distances[v]:
                        distances[v] = new_dist
                        heapq.heappush(pq, (new_dist, v))
        
        return distances


class FloydWarshallAlgorithm:
    """Floyd-Warshall algorithm: Pure dynamic programming"""
    
    @staticmethod
    def solve(graph):
        """
        Floyd-Warshall algorithm
        Time Complexity: O(V^3)
        Space Complexity: O(V^2)
        """
        n = len(graph)
        
        # Create a copy of the graph
        dist = [row[:] for row in graph]
        
        # DP: For each intermediate vertex k
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    # Update shortest path through vertex k
                    if dist[i][k] != float('inf') and dist[k][j] != float('inf'):
                        dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
        
        return dist


def run_empirical_analysis():
    """Run empirical analysis of both algorithms"""
    
    # Test configurations
    node_sizes = [10, 20, 50, 100, 150, 200]
    results = {
        'nodes': [],
        'dijkstra_sparse': [],
        'dijkstra_dense': [],
        'floyd_sparse': [],
        'floyd_dense': [],
        'dijkstra_sparse_std': [],
        'dijkstra_dense_std': [],
        'floyd_sparse_std': [],
        'floyd_dense_std': []
    }
    
    print("=" * 80)
    print("EMPIRICAL ANALYSIS: Dijkstra vs Floyd-Warshall")
    print("=" * 80)
    print()
    
    for n in node_sizes:
        print(f"Testing with {n} nodes...")
        
        # Run multiple trials for each configuration
        dijkstra_sparse_times = []
        dijkstra_dense_times = []
        floyd_sparse_times = []
        floyd_dense_times = []
        
        num_trials = 2 if n > 100 else 3
        
        for trial in range(num_trials):
            # Generate graphs
            gen = GraphGenerator(n, seed=42 + trial)
            sparse_graph = gen.generate_sparse_graph()
            dense_graph = gen.generate_dense_graph()
            
            # Test Dijkstra on sparse graph
            start = time.perf_counter()
            DijkstraAlgorithm.solve(sparse_graph, source=0)
            dijkstra_sparse_times.append(time.perf_counter() - start)
            
            # Test Dijkstra on dense graph
            start = time.perf_counter()
            DijkstraAlgorithm.solve(dense_graph, source=0)
            dijkstra_dense_times.append(time.perf_counter() - start)
            
            # Test Floyd-Warshall on sparse graph
            start = time.perf_counter()
            FloydWarshallAlgorithm.solve(sparse_graph)
            floyd_sparse_times.append(time.perf_counter() - start)
            
            # Test Floyd-Warshall on dense graph
            start = time.perf_counter()
            FloydWarshallAlgorithm.solve(dense_graph)
            floyd_dense_times.append(time.perf_counter() - start)
        
        # Calculate averages and standard deviations
        results['nodes'].append(n)
        results['dijkstra_sparse'].append(np.mean(dijkstra_sparse_times))
        results['dijkstra_dense'].append(np.mean(dijkstra_dense_times))
        results['floyd_sparse'].append(np.mean(floyd_sparse_times))
        results['floyd_dense'].append(np.mean(floyd_dense_times))
        results['dijkstra_sparse_std'].append(np.std(dijkstra_sparse_times))
        results['dijkstra_dense_std'].append(np.std(dijkstra_dense_times))
        results['floyd_sparse_std'].append(np.std(floyd_sparse_times))
        results['floyd_dense_std'].append(np.std(floyd_dense_times))
    
    return results


def display_results_table(results):
    """Display results in PrettyTable format"""
    
    print("\n" + "=" * 80)
    print("RESULTS TABLE: Execution Time (seconds)")
    print("=" * 80)
    print()
    
    # Create main results table
    table = PrettyTable()
    table.field_names = [
        "Nodes",
        "Dijkstra\n(Sparse)",
        "Dijkstra\n(Dense)",
        "Floyd-W\n(Sparse)",
        "Floyd-W\n(Dense)"
    ]
    
    for i, n in enumerate(results['nodes']):
        table.add_row([
            n,
            f"{results['dijkstra_sparse'][i]:.6f}",
            f"{results['dijkstra_dense'][i]:.6f}",
            f"{results['floyd_sparse'][i]:.6f}",
            f"{results['floyd_dense'][i]:.6f}"
        ])
    
    print(table)
    print()
    
    # Create standard deviation table
    table_std = PrettyTable()
    table_std.field_names = [
        "Nodes",
        "Dijkstra\n(Sparse) ±",
        "Dijkstra\n(Dense) ±",
        "Floyd-W\n(Sparse) ±",
        "Floyd-W\n(Dense) ±"
    ]
    
    for i, n in enumerate(results['nodes']):
        table_std.add_row([
            n,
            f"{results['dijkstra_sparse_std'][i]:.6f}",
            f"{results['dijkstra_dense_std'][i]:.6f}",
            f"{results['floyd_sparse_std'][i]:.6f}",
            f"{results['floyd_dense_std'][i]:.6f}"
        ])
    
    print("Standard Deviations:")
    print(table_std)
    print()
    
    # Create efficiency comparison table
    table_ratio = PrettyTable()
    table_ratio.field_names = [
        "Nodes",
        "Dijkstra better on\nSparse vs Dense",
        "Floyd-W better on\nSparse vs Dense",
        "Dijkstra vs Floyd-W\n(Sparse)",
        "Dijkstra vs Floyd-W\n(Dense)"
    ]
    
    for i, n in enumerate(results['nodes']):
        dijkstra_ratio = results['dijkstra_dense'][i] / max(results['dijkstra_sparse'][i], 1e-9)
        floyd_ratio = results['floyd_dense'][i] / max(results['floyd_sparse'][i], 1e-9)
        dijkstra_vs_floyd_sparse = results['dijkstra_sparse'][i] / max(results['floyd_sparse'][i], 1e-9)
        dijkstra_vs_floyd_dense = results['dijkstra_dense'][i] / max(results['floyd_dense'][i], 1e-9)
        
        table_ratio.add_row([
            n,
            f"{dijkstra_ratio:.2f}x",
            f"{floyd_ratio:.2f}x",
            f"{dijkstra_vs_floyd_sparse:.2f}x",
            f"{dijkstra_vs_floyd_dense:.2f}x"
        ])
    
    print("Performance Ratios:")
    print(table_ratio)
    print()


def plot_results(results):
    """Plot performance results"""
    
    nodes = results['nodes']
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Dynamic Programming Algorithm Analysis: Dijkstra vs Floyd-Warshall', 
                 fontsize=16, fontweight='bold')
    
    # Plot 1: Sparse Graph Performance
    ax = axes[0, 0]
    ax.plot(nodes, results['dijkstra_sparse'], marker='o', label='Dijkstra', linewidth=2)
    ax.plot(nodes, results['floyd_sparse'], marker='s', label='Floyd-Warshall', linewidth=2)
    ax.fill_between(nodes, 
                     np.array(results['dijkstra_sparse']) - np.array(results['dijkstra_sparse_std']),
                     np.array(results['dijkstra_sparse']) + np.array(results['dijkstra_sparse_std']),
                     alpha=0.2)
    ax.fill_between(nodes,
                     np.array(results['floyd_sparse']) - np.array(results['floyd_sparse_std']),
                     np.array(results['floyd_sparse']) + np.array(results['floyd_sparse_std']),
                     alpha=0.2)
    ax.set_xlabel('Number of Nodes', fontsize=11, fontweight='bold')
    ax.set_ylabel('Execution Time (seconds)', fontsize=11, fontweight='bold')
    ax.set_title('Sparse Graph Performance', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    
    # Plot 2: Dense Graph Performance
    ax = axes[0, 1]
    ax.plot(nodes, results['dijkstra_dense'], marker='o', label='Dijkstra', linewidth=2)
    ax.plot(nodes, results['floyd_dense'], marker='s', label='Floyd-Warshall', linewidth=2)
    ax.fill_between(nodes,
                     np.array(results['dijkstra_dense']) - np.array(results['dijkstra_dense_std']),
                     np.array(results['dijkstra_dense']) + np.array(results['dijkstra_dense_std']),
                     alpha=0.2)
    ax.fill_between(nodes,
                     np.array(results['floyd_dense']) - np.array(results['floyd_dense_std']),
                     np.array(results['floyd_dense']) + np.array(results['floyd_dense_std']),
                     alpha=0.2)
    ax.set_xlabel('Number of Nodes', fontsize=11, fontweight='bold')
    ax.set_ylabel('Execution Time (seconds)', fontsize=11, fontweight='bold')
    ax.set_title('Dense Graph Performance', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    
    # Plot 3: Dijkstra Comparison (Sparse vs Dense)
    ax = axes[1, 0]
    ax.plot(nodes, results['dijkstra_sparse'], marker='o', label='Sparse Graph', linewidth=2, color='green')
    ax.plot(nodes, results['dijkstra_dense'], marker='s', label='Dense Graph', linewidth=2, color='red')
    ax.fill_between(nodes,
                     np.array(results['dijkstra_sparse']) - np.array(results['dijkstra_sparse_std']),
                     np.array(results['dijkstra_sparse']) + np.array(results['dijkstra_sparse_std']),
                     alpha=0.2, color='green')
    ax.fill_between(nodes,
                     np.array(results['dijkstra_dense']) - np.array(results['dijkstra_dense_std']),
                     np.array(results['dijkstra_dense']) + np.array(results['dijkstra_dense_std']),
                     alpha=0.2, color='red')
    ax.set_xlabel('Number of Nodes', fontsize=11, fontweight='bold')
    ax.set_ylabel('Execution Time (seconds)', fontsize=11, fontweight='bold')
    ax.set_title('Dijkstra: Sparse vs Dense', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    
    # Plot 4: Floyd-Warshall Comparison (Sparse vs Dense)
    ax = axes[1, 1]
    ax.plot(nodes, results['floyd_sparse'], marker='o', label='Sparse Graph', linewidth=2, color='green')
    ax.plot(nodes, results['floyd_dense'], marker='s', label='Dense Graph', linewidth=2, color='red')
    ax.fill_between(nodes,
                     np.array(results['floyd_sparse']) - np.array(results['floyd_sparse_std']),
                     np.array(results['floyd_sparse']) + np.array(results['floyd_sparse_std']),
                     alpha=0.2, color='green')
    ax.fill_between(nodes,
                     np.array(results['floyd_dense']) - np.array(results['floyd_dense_std']),
                     np.array(results['floyd_dense']) + np.array(results['floyd_dense_std']),
                     alpha=0.2, color='red')
    ax.set_xlabel('Number of Nodes', fontsize=11, fontweight='bold')
    ax.set_ylabel('Execution Time (seconds)', fontsize=11, fontweight='bold')
    ax.set_title('Floyd-Warshall: Sparse vs Dense', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    
    plt.tight_layout()
    plt.savefig('algorithm_comparison.png', dpi=300, bbox_inches='tight')
    print("Saved plot as 'algorithm_comparison.png'")
    plt.show()


def main():
    """Main execution function"""
    
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "DYNAMIC PROGRAMMING: Dijkstra and Floyd-Warshall Algorithms".center(78) + "║")
    print("║" + "Empirical Analysis on Sparse and Dense Graphs".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    # Run analysis
    results = run_empirical_analysis()
    
    # Display results
    display_results_table(results)
    
    # Plot results
    plot_results(results)
    
    # Summary
    print("=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    print()
    print("Key Findings:")
    print()
    print("1. DIJKSTRA'S ALGORITHM:")
    print("   - Time Complexity: O((V + E) log V) with binary heap")
    print("   - More efficient for sparse graphs (fewer edges)")
    print("   - Uses dynamic programming through optimal substructure:")
    print("     If P is a shortest path from s to t, then any subpath of P is")
    print("     a shortest path between its endpoints.")
    print()
    print("2. FLOYD-WARSHALL ALGORITHM:")
    print("   - Time Complexity: O(V³) for all-pairs shortest paths")
    print("   - Pure dynamic programming: builds solution bottom-up")
    print("   - Less efficient for sparse graphs but computes all-pairs distances")
    print("   - Optimal substructure: shortest path through vertex k is determined")
    print("     by shortest paths through vertices in {1,...,k-1}")
    print()
    print("3. PERFORMANCE CHARACTERISTICS:")
    print(f"   - Dijkstra on sparse graphs: {results['dijkstra_sparse'][-1]:.6f}s (n={results['nodes'][-1]})")
    print(f"   - Dijkstra on dense graphs: {results['dijkstra_dense'][-1]:.6f}s (n={results['nodes'][-1]})")
    print(f"   - Floyd-Warshall on sparse: {results['floyd_sparse'][-1]:.6f}s (n={results['nodes'][-1]})")
    print(f"   - Floyd-Warshall on dense: {results['floyd_dense'][-1]:.6f}s (n={results['nodes'][-1]})")
    print()
    print("4. SCALABILITY:")
    print(f"   - When nodes grow from {results['nodes'][0]} to {results['nodes'][-1]} ({results['nodes'][-1]//results['nodes'][0]}x)")
    dijkstra_sparse_growth = results['dijkstra_sparse'][-1] / max(results['dijkstra_sparse'][0], 1e-9)
    dijkstra_dense_growth = results['dijkstra_dense'][-1] / max(results['dijkstra_dense'][0], 1e-9)
    floyd_sparse_growth = results['floyd_sparse'][-1] / max(results['floyd_sparse'][0], 1e-9)
    floyd_dense_growth = results['floyd_dense'][-1] / max(results['floyd_dense'][0], 1e-9)
    print(f"     Dijkstra sparse growth: {dijkstra_sparse_growth:.1f}x")
    print(f"     Dijkstra dense growth: {dijkstra_dense_growth:.1f}x")
    print(f"     Floyd-Warshall sparse growth: {floyd_sparse_growth:.1f}x")
    print(f"     Floyd-Warshall dense growth: {floyd_dense_growth:.1f}x")
    print()


if __name__ == "__main__":
    main()
