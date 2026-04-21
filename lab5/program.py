"""
Greedy Algorithms Lab: Prim and Kruskal
Empirical analysis on sparse and dense graphs with increasing node counts.
"""

import argparse
import heapq
import random
import time
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from prettytable import PrettyTable


@dataclass
class Edge:
    """Undirected weighted edge."""

    u: int
    v: int
    w: int


class GraphGenerator:
    """Generate connected undirected weighted graphs for benchmarking."""

    def __init__(self, n: int, seed: int = 42):
        self.n = n
        self.rng = random.Random(seed)

    def _base_connected_tree(self) -> list[tuple[int, int, int]]:
        """Create a random tree to guarantee graph connectivity."""
        edges = []
        for node in range(1, self.n):
            parent = self.rng.randint(0, node - 1)
            weight = self.rng.randint(1, 100)
            u, v = sorted((node, parent))
            edges.append((u, v, weight))
        return edges

    def _to_edge_objects_and_adj(
        self, edge_tuples: list[tuple[int, int, int]]
    ) -> tuple[list[Edge], list[list[tuple[int, int]]]]:
        edges = [Edge(u, v, w) for u, v, w in edge_tuples]
        adjacency = [[] for _ in range(self.n)]

        for edge in edges:
            adjacency[edge.u].append((edge.v, edge.w))
            adjacency[edge.v].append((edge.u, edge.w))

        return edges, adjacency

    def generate_sparse_graph(self) -> tuple[list[Edge], list[list[tuple[int, int]]]]:
        """Generate a sparse graph with approximately 2N edges."""
        if self.n <= 1:
            return [], [[] for _ in range(self.n)]

        edges = self._base_connected_tree()
        existing = {(u, v) for u, v, _ in edges}

        target_edges = max(self.n - 1, 2 * self.n)
        max_edges = self.n * (self.n - 1) // 2
        target_edges = min(target_edges, max_edges)

        while len(edges) < target_edges:
            u = self.rng.randint(0, self.n - 1)
            v = self.rng.randint(0, self.n - 1)
            if u == v:
                continue
            a, b = sorted((u, v))
            if (a, b) in existing:
                continue
            existing.add((a, b))
            edges.append((a, b, self.rng.randint(1, 100)))

        return self._to_edge_objects_and_adj(edges)

    def generate_dense_graph(self) -> tuple[list[Edge], list[list[tuple[int, int]]]]:
        """Generate a dense graph with around 50% of all possible edges."""
        if self.n <= 1:
            return [], [[] for _ in range(self.n)]

        edges = self._base_connected_tree()
        existing = {(u, v) for u, v, _ in edges}

        for u in range(self.n):
            for v in range(u + 1, self.n):
                if (u, v) in existing:
                    continue
                if self.rng.random() < 0.5:
                    existing.add((u, v))
                    edges.append((u, v, self.rng.randint(1, 100)))

        return self._to_edge_objects_and_adj(edges)


class UnionFind:
    """Disjoint set union with path compression and union by rank."""

    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a: int, b: int) -> bool:
        root_a = self.find(a)
        root_b = self.find(b)

        if root_a == root_b:
            return False

        if self.rank[root_a] < self.rank[root_b]:
            root_a, root_b = root_b, root_a

        self.parent[root_b] = root_a
        if self.rank[root_a] == self.rank[root_b]:
            self.rank[root_a] += 1

        return True


class PrimAlgorithm:
    """Prim's algorithm for minimum spanning tree."""

    @staticmethod
    def solve(adjacency: list[list[tuple[int, int]]]) -> tuple[int, list[tuple[int, int, int]]]:
        n = len(adjacency)
        if n <= 1:
            return 0, []

        visited = [False] * n
        min_heap = [(0, -1, 0)]  # (weight, parent, node)

        mst_weight = 0
        mst_edges = []

        while min_heap and len(mst_edges) < n - 1:
            w, parent, u = heapq.heappop(min_heap)

            if visited[u]:
                continue

            visited[u] = True
            mst_weight += w
            if parent != -1:
                mst_edges.append((parent, u, w))

            for v, weight in adjacency[u]:
                if not visited[v]:
                    heapq.heappush(min_heap, (weight, u, v))

        if len(mst_edges) != n - 1:
            raise ValueError("Graph is not connected; Prim failed to build MST.")

        return mst_weight, mst_edges


class KruskalAlgorithm:
    """Kruskal's algorithm for minimum spanning tree."""

    @staticmethod
    def solve(edges: list[Edge], n: int) -> tuple[int, list[tuple[int, int, int]]]:
        if n <= 1:
            return 0, []

        uf = UnionFind(n)
        mst_weight = 0
        mst_edges = []

        for edge in sorted(edges, key=lambda e: e.w):
            if uf.union(edge.u, edge.v):
                mst_weight += edge.w
                mst_edges.append((edge.u, edge.v, edge.w))
                if len(mst_edges) == n - 1:
                    break

        if len(mst_edges) != n - 1:
            raise ValueError("Graph is not connected; Kruskal failed to build MST.")

        return mst_weight, mst_edges


def run_empirical_analysis() -> dict[str, list[float]]:
    """Run timing experiments for Prim and Kruskal on sparse and dense graphs."""
    node_sizes = [20, 50, 100, 150, 200, 300]

    results: dict[str, list[float]] = {
        "nodes": [],
        "prim_sparse": [],
        "prim_dense": [],
        "kruskal_sparse": [],
        "kruskal_dense": [],
        "prim_sparse_std": [],
        "prim_dense_std": [],
        "kruskal_sparse_std": [],
        "kruskal_dense_std": [],
    }

    print("=" * 80)
    print("EMPIRICAL ANALYSIS: Prim vs Kruskal")
    print("=" * 80)
    print()

    for n in node_sizes:
        print(f"Testing with {n} nodes...")

        prim_sparse_times = []
        prim_dense_times = []
        kruskal_sparse_times = []
        kruskal_dense_times = []

        num_trials = 3 if n <= 150 else 2

        for trial in range(num_trials):
            generator = GraphGenerator(n, seed=42 + trial)
            sparse_edges, sparse_adj = generator.generate_sparse_graph()
            dense_edges, dense_adj = generator.generate_dense_graph()

            start = time.perf_counter()
            prim_sparse_weight, _ = PrimAlgorithm.solve(sparse_adj)
            prim_sparse_times.append(time.perf_counter() - start)

            start = time.perf_counter()
            prim_dense_weight, _ = PrimAlgorithm.solve(dense_adj)
            prim_dense_times.append(time.perf_counter() - start)

            start = time.perf_counter()
            kruskal_sparse_weight, _ = KruskalAlgorithm.solve(sparse_edges, n)
            kruskal_sparse_times.append(time.perf_counter() - start)

            start = time.perf_counter()
            kruskal_dense_weight, _ = KruskalAlgorithm.solve(dense_edges, n)
            kruskal_dense_times.append(time.perf_counter() - start)

            if prim_sparse_weight != kruskal_sparse_weight:
                raise ValueError("MST mismatch on sparse graph")
            if prim_dense_weight != kruskal_dense_weight:
                raise ValueError("MST mismatch on dense graph")

        results["nodes"].append(n)
        results["prim_sparse"].append(float(np.mean(prim_sparse_times)))
        results["prim_dense"].append(float(np.mean(prim_dense_times)))
        results["kruskal_sparse"].append(float(np.mean(kruskal_sparse_times)))
        results["kruskal_dense"].append(float(np.mean(kruskal_dense_times)))
        results["prim_sparse_std"].append(float(np.std(prim_sparse_times)))
        results["prim_dense_std"].append(float(np.std(prim_dense_times)))
        results["kruskal_sparse_std"].append(float(np.std(kruskal_sparse_times)))
        results["kruskal_dense_std"].append(float(np.std(kruskal_dense_times)))

    return results


def display_results_tables(results: dict[str, list[float]]) -> None:
    """Print execution time, standard deviation, and ratio tables using PrettyTable."""
    print("\n" + "=" * 80)
    print("RESULTS TABLE: Execution Time (seconds)")
    print("=" * 80)
    print()

    table = PrettyTable()
    table.field_names = [
        "Nodes",
        "Prim (Sparse)",
        "Prim (Dense)",
        "Kruskal (Sparse)",
        "Kruskal (Dense)",
    ]

    for i, n in enumerate(results["nodes"]):
        table.add_row(
            [
                int(n),
                f"{results['prim_sparse'][i]:.6f}",
                f"{results['prim_dense'][i]:.6f}",
                f"{results['kruskal_sparse'][i]:.6f}",
                f"{results['kruskal_dense'][i]:.6f}",
            ]
        )

    print(table)
    print()

    std_table = PrettyTable()
    std_table.field_names = [
        "Nodes",
        "Prim (Sparse)",
        "Prim (Dense)",
        "Kruskal (Sparse)",
        "Kruskal (Dense)",
    ]

    for i, n in enumerate(results["nodes"]):
        std_table.add_row(
            [
                int(n),
                f"{results['prim_sparse_std'][i]:.6f}",
                f"{results['prim_dense_std'][i]:.6f}",
                f"{results['kruskal_sparse_std'][i]:.6f}",
                f"{results['kruskal_dense_std'][i]:.6f}",
            ]
        )

    print("Standard Deviations:")
    print(std_table)
    print()

    ratio_table = PrettyTable()
    ratio_table.field_names = [
        "Nodes",
        "Prim Dense/Sparse",
        "Kruskal Dense/Sparse",
        "Prim/Kruskal (Sparse)",
        "Prim/Kruskal (Dense)",
    ]

    for i, n in enumerate(results["nodes"]):
        prim_ds = results["prim_dense"][i] / max(results["prim_sparse"][i], 1e-12)
        kruskal_ds = results["kruskal_dense"][i] / max(results["kruskal_sparse"][i], 1e-12)
        prim_over_kruskal_sparse = results["prim_sparse"][i] / max(results["kruskal_sparse"][i], 1e-12)
        prim_over_kruskal_dense = results["prim_dense"][i] / max(results["kruskal_dense"][i], 1e-12)

        ratio_table.add_row(
            [
                int(n),
                f"{prim_ds:.2f}x",
                f"{kruskal_ds:.2f}x",
                f"{prim_over_kruskal_sparse:.2f}x",
                f"{prim_over_kruskal_dense:.2f}x",
            ]
        )

    print("Performance Ratios:")
    print(ratio_table)
    print()


def save_plots(results: dict[str, list[float]], output_dir: Path, show: bool = False) -> None:
    """Create and save plots used for analysis/reporting."""
    output_dir.mkdir(parents=True, exist_ok=True)
    nodes = results["nodes"]

    plt.figure(figsize=(11, 6))
    plt.plot(nodes, results["prim_sparse"], marker="o", linewidth=2, label="Prim (Sparse)")
    plt.plot(nodes, results["prim_dense"], marker="o", linewidth=2, label="Prim (Dense)")
    plt.plot(nodes, results["kruskal_sparse"], marker="s", linewidth=2, label="Kruskal (Sparse)")
    plt.plot(nodes, results["kruskal_dense"], marker="s", linewidth=2, label="Kruskal (Dense)")
    plt.yscale("log")
    plt.grid(alpha=0.3)
    plt.xlabel("Number of Nodes", fontweight="bold")
    plt.ylabel("Execution Time (seconds, log scale)", fontweight="bold")
    plt.title("Prim vs Kruskal on Sparse and Dense Graphs", fontweight="bold")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "exec_time.png", dpi=300)

    plt.figure(figsize=(11, 6))
    plt.plot(nodes, results["prim_sparse_std"], marker="o", linewidth=2, label="Prim (Sparse) std")
    plt.plot(nodes, results["prim_dense_std"], marker="o", linewidth=2, label="Prim (Dense) std")
    plt.plot(nodes, results["kruskal_sparse_std"], marker="s", linewidth=2, label="Kruskal (Sparse) std")
    plt.plot(nodes, results["kruskal_dense_std"], marker="s", linewidth=2, label="Kruskal (Dense) std")
    plt.grid(alpha=0.3)
    plt.xlabel("Number of Nodes", fontweight="bold")
    plt.ylabel("Standard Deviation (seconds)", fontweight="bold")
    plt.title("Timing Variability by Algorithm and Density", fontweight="bold")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "std_deviations.png", dpi=300)

    prim_dense_sparse = [
        results["prim_dense"][i] / max(results["prim_sparse"][i], 1e-12)
        for i in range(len(nodes))
    ]
    kruskal_dense_sparse = [
        results["kruskal_dense"][i] / max(results["kruskal_sparse"][i], 1e-12)
        for i in range(len(nodes))
    ]
    prim_over_kruskal_sparse = [
        results["prim_sparse"][i] / max(results["kruskal_sparse"][i], 1e-12)
        for i in range(len(nodes))
    ]
    prim_over_kruskal_dense = [
        results["prim_dense"][i] / max(results["kruskal_dense"][i], 1e-12)
        for i in range(len(nodes))
    ]

    plt.figure(figsize=(11, 6))
    plt.plot(nodes, prim_dense_sparse, marker="o", linewidth=2, label="Prim Dense/Sparse")
    plt.plot(nodes, kruskal_dense_sparse, marker="o", linewidth=2, label="Kruskal Dense/Sparse")
    plt.plot(nodes, prim_over_kruskal_sparse, marker="s", linewidth=2, label="Prim/Kruskal (Sparse)")
    plt.plot(nodes, prim_over_kruskal_dense, marker="s", linewidth=2, label="Prim/Kruskal (Dense)")
    plt.grid(alpha=0.3)
    plt.xlabel("Number of Nodes", fontweight="bold")
    plt.ylabel("Ratio", fontweight="bold")
    plt.title("Performance Ratios", fontweight="bold")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "performance.png", dpi=300)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Greedy Algorithms Analysis: Prim vs Kruskal", fontsize=16, fontweight="bold")

    ax = axes[0, 0]
    ax.plot(nodes, results["prim_sparse"], marker="o", linewidth=2, label="Prim")
    ax.plot(nodes, results["kruskal_sparse"], marker="s", linewidth=2, label="Kruskal")
    ax.fill_between(
        nodes,
        np.array(results["prim_sparse"]) - np.array(results["prim_sparse_std"]),
        np.array(results["prim_sparse"]) + np.array(results["prim_sparse_std"]),
        alpha=0.2,
    )
    ax.fill_between(
        nodes,
        np.array(results["kruskal_sparse"]) - np.array(results["kruskal_sparse_std"]),
        np.array(results["kruskal_sparse"]) + np.array(results["kruskal_sparse_std"]),
        alpha=0.2,
    )
    ax.set_title("Sparse Graphs")
    ax.set_xlabel("Nodes")
    ax.set_ylabel("Time (s)")
    ax.set_yscale("log")
    ax.grid(alpha=0.3)
    ax.legend()

    ax = axes[0, 1]
    ax.plot(nodes, results["prim_dense"], marker="o", linewidth=2, label="Prim")
    ax.plot(nodes, results["kruskal_dense"], marker="s", linewidth=2, label="Kruskal")
    ax.fill_between(
        nodes,
        np.array(results["prim_dense"]) - np.array(results["prim_dense_std"]),
        np.array(results["prim_dense"]) + np.array(results["prim_dense_std"]),
        alpha=0.2,
    )
    ax.fill_between(
        nodes,
        np.array(results["kruskal_dense"]) - np.array(results["kruskal_dense_std"]),
        np.array(results["kruskal_dense"]) + np.array(results["kruskal_dense_std"]),
        alpha=0.2,
    )
    ax.set_title("Dense Graphs")
    ax.set_xlabel("Nodes")
    ax.set_ylabel("Time (s)")
    ax.set_yscale("log")
    ax.grid(alpha=0.3)
    ax.legend()

    ax = axes[1, 0]
    ax.plot(nodes, results["prim_sparse"], marker="o", linewidth=2, label="Sparse")
    ax.plot(nodes, results["prim_dense"], marker="s", linewidth=2, label="Dense")
    ax.set_title("Prim: Sparse vs Dense")
    ax.set_xlabel("Nodes")
    ax.set_ylabel("Time (s)")
    ax.set_yscale("log")
    ax.grid(alpha=0.3)
    ax.legend()

    ax = axes[1, 1]
    ax.plot(nodes, results["kruskal_sparse"], marker="o", linewidth=2, label="Sparse")
    ax.plot(nodes, results["kruskal_dense"], marker="s", linewidth=2, label="Dense")
    ax.set_title("Kruskal: Sparse vs Dense")
    ax.set_xlabel("Nodes")
    ax.set_ylabel("Time (s)")
    ax.set_yscale("log")
    ax.grid(alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_dir / "plot.png", dpi=300)

    i = len(nodes) - 1
    labels = ["Prim", "Kruskal"]
    sparse_vals = [results["prim_sparse"][i], results["kruskal_sparse"][i]]
    dense_vals = [results["prim_dense"][i], results["kruskal_dense"][i]]
    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(8, 5))
    plt.bar(x - width / 2, sparse_vals, width, label="Sparse")
    plt.bar(x + width / 2, dense_vals, width, label="Dense")
    plt.xticks(x, labels)
    plt.yscale("log")
    plt.ylabel("Execution Time (seconds, log scale)")
    plt.title(f"Algorithm Comparison at N={int(nodes[i])}")
    plt.grid(axis="y", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "results_graph.png", dpi=300)

    if show:
        plt.show()
    else:
        plt.close("all")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Greedy Algorithms Lab: Prim and Kruskal empirical analysis"
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display plots interactively in addition to saving files.",
    )
    args = parser.parse_args()

    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "GREEDY ALGORITHMS: Prim and Kruskal".center(78) + "║")
    print("║" + "Empirical Analysis on Sparse and Dense Graphs".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    results = run_empirical_analysis()
    display_results_tables(results)

    images_dir = Path(__file__).resolve().parent / "report" / "images"
    save_plots(results, images_dir, show=args.show)

    print("Saved plots in report/images:")
    print(" - exec_time.png")
    print(" - std_deviations.png")
    print(" - performance.png")
    print(" - plot.png")
    print(" - results_graph.png")


if __name__ == "__main__":
    main()
