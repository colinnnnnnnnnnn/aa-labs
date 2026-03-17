from collections import deque
from time import perf_counter_ns
import random
from prettytable import PrettyTable
import matplotlib.pyplot as plt
import numpy as np


def bfs(graph, start, target):
	visited = {start}
	queue = deque([start])
	peak_frontier = 1
	expanded = 0

	while queue:
		node = queue.popleft()
		expanded += 1

		if node == target:
			return True, expanded, peak_frontier

		for neighbor in graph.get(node, []):
			if neighbor not in visited:
				visited.add(neighbor)
				queue.append(neighbor)

		if len(queue) > peak_frontier:
			peak_frontier = len(queue)

	return False, expanded, peak_frontier


def dfs(graph, start, target):
	visited = set()
	stack = [start]
	peak_frontier = 1
	expanded = 0

	while stack:
		node = stack.pop()

		if node in visited:
			continue

		visited.add(node)
		expanded += 1

		if node == target:
			return True, expanded, peak_frontier

		neighbors = graph.get(node, [])
		for neighbor in reversed(neighbors):
			if neighbor not in visited:
				stack.append(neighbor)

		if len(stack) > peak_frontier:
			peak_frontier = len(stack)

	return False, expanded, peak_frontier


def path_graph(n):
	graph = {i: [] for i in range(n)}
	for i in range(n - 1):
		graph[i].append(i + 1)
		graph[i + 1].append(i)
	return graph


def balanced_tree(levels, branching_factor):
	if levels <= 0:
		return {0: []}

	graph = {0: []}
	current_level = [0]
	next_node_id = 1

	for _ in range(1, levels):
		next_level = []
		for parent in current_level:
			for _ in range(branching_factor):
				child = next_node_id
				next_node_id += 1
				graph.setdefault(parent, []).append(child)
				graph[child] = [parent]
				next_level.append(child)
		current_level = next_level

	return graph


def complete_graph(n):
	graph = {}
	for i in range(n):
		graph[i] = [j for j in range(n) if j != i]
	return graph


def grid_graph(rows, cols):
	def node_id(r, c):
		return r * cols + c

	graph = {node_id(r, c): [] for r in range(rows) for c in range(cols)}

	for r in range(rows):
		for c in range(cols):
			node = node_id(r, c)
			if r > 0:
				graph[node].append(node_id(r - 1, c))
			if r < rows - 1:
				graph[node].append(node_id(r + 1, c))
			if c > 0:
				graph[node].append(node_id(r, c - 1))
			if c < cols - 1:
				graph[node].append(node_id(r, c + 1))

	return graph


def random_graph(n, edge_probability, seed=42):
	rnd = random.Random(seed)
	graph = {i: [] for i in range(n)}

	for i in range(n):
		for j in range(i + 1, n):
			if rnd.random() < edge_probability:
				graph[i].append(j)
				graph[j].append(i)

	return graph


def disconnected_graph(component_a_size, component_b_size):
	total = component_a_size + component_b_size
	graph = {i: [] for i in range(total)}

	for i in range(component_a_size - 1):
		graph[i].append(i + 1)
		graph[i + 1].append(i)

	offset = component_a_size
	for i in range(offset, offset + component_b_size - 1):
		graph[i].append(i + 1)
		graph[i + 1].append(i)

	return graph


def count_undirected_edges(graph):
	return sum(len(neighbors) for neighbors in graph.values()) // 2


def benchmark_search(search_fn, graph, start, target, repeats=5):
	timings_ms = []
	found = False
	expanded = 0
	peak_frontier = 0

	for _ in range(repeats):
		t0 = perf_counter_ns()
		found, expanded, peak_frontier = search_fn(graph, start, target)
		t1 = perf_counter_ns()
		timings_ms.append((t1 - t0) / 1_000_000)

	return {
		"found": found,
		"avg_ms": sum(timings_ms) / len(timings_ms),
		"min_ms": min(timings_ms),
		"expanded": expanded,
		"peak_frontier": peak_frontier,
	}


def run_scenarios():
	scenarios = []

	chain = path_graph(20_000)
	scenarios.append(("Chain/Path", chain, 0, 19_999, "deep target"))

	tree = balanced_tree(levels=9, branching_factor=3)
	scenarios.append(("Balanced Tree", tree, 0, max(tree), "deep leaf"))

	complete = complete_graph(2_000)
	scenarios.append(("Dense/Complete", complete, 0, 1_999, "any neighbor"))

	grid = grid_graph(120, 120)
	scenarios.append(("Grid", grid, 0, 120 * 120 - 1, "opposite corner"))

	deep_shallow_tree = balanced_tree(levels=10, branching_factor=2)
	scenarios.append(("Deep vs Shallow", deep_shallow_tree, 0, 1, "shallow"))
	scenarios.append(("Deep vs Shallow", deep_shallow_tree, 0, max(deep_shallow_tree), "deep"))

	rnd = random_graph(n=4_500, edge_probability=0.0015, seed=7)
	scenarios.append(("Large Random", rnd, 0, 4_499, "random target"))

	disconnected = disconnected_graph(component_a_size=4_000, component_b_size=4_000)
	scenarios.append(("Disconnected", disconnected, 0, 7_999, "unreachable"))

	table = PrettyTable()
	table.field_names = [
		"Scenario",
		"Algorithm",
		"Nodes",
		"Edges",
		"Target Type",
		"Found",
		"Avg Time (ms)",
	]

	results = []

	for scenario_name, graph, start, target, target_type in scenarios:
		nodes = len(graph)
		edges = count_undirected_edges(graph)

		bfs_result = benchmark_search(bfs, graph, start, target)
		dfs_result = benchmark_search(dfs, graph, start, target)

		table.add_row([
			scenario_name, "BFS", nodes, edges, target_type,
			bfs_result["found"], f"{bfs_result['avg_ms']:.4f}",
		])
		table.add_row([
			scenario_name, "DFS", nodes, edges, target_type,
			dfs_result["found"], f"{dfs_result['avg_ms']:.4f}",
		])

		results.append({
			"label": f"{scenario_name}\n({target_type})",
			"bfs_ms": bfs_result["avg_ms"],
			"dfs_ms": dfs_result["avg_ms"],
		})

	print(table)
	return results


def plot_results(results):
	labels = [r["label"] for r in results]
	bfs_times = [r["bfs_ms"] for r in results]
	dfs_times = [r["dfs_ms"] for r in results]

	x = np.arange(len(labels))
	bar_width = 0.35

	fig, ax = plt.subplots(figsize=(14, 6))

	bars_bfs = ax.bar(x - bar_width / 2, bfs_times, bar_width, label="BFS", color="#4C72B0", zorder=3)
	bars_dfs = ax.bar(x + bar_width / 2, dfs_times, bar_width, label="DFS", color="#DD8452", zorder=3)

	ax.set_xlabel("Scenario", fontsize=12)
	ax.set_ylabel("Avg Time (ms)", fontsize=12)
	ax.set_title("BFS vs DFS — Average Time to Reach Target", fontsize=14, fontweight="bold")
	ax.set_xticks(x)
	ax.set_xticklabels(labels, fontsize=9)
	ax.legend(fontsize=11)
	ax.grid(axis="y", linestyle="--", alpha=0.6, zorder=0)

	for bar in bars_bfs:
		height = bar.get_height()
		ax.annotate(
			f"{height:.2f}",
			xy=(bar.get_x() + bar.get_width() / 2, height),
			xytext=(0, 4), textcoords="offset points",
			ha="center", va="bottom", fontsize=7,
		)
	for bar in bars_dfs:
		height = bar.get_height()
		ax.annotate(
			f"{height:.2f}",
			xy=(bar.get_x() + bar.get_width() / 2, height),
			xytext=(0, 4), textcoords="offset points",
			ha="center", va="bottom", fontsize=7,
		)

	plt.tight_layout()
	plt.savefig("bfs_vs_dfs.png", dpi=150)
	print("\nChart saved to bfs_vs_dfs.png")
	plt.show()


if __name__ == "__main__":
	results = run_scenarios()
	plot_results(results)
