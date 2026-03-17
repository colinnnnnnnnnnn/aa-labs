from collections import deque
import argparse

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Patch
import networkx as nx


GRAPH = {
    "A": ["B", "C"],
    "B": ["A", "D", "E"],
    "C": ["A", "F", "G"],
    "D": ["B", "H"],
    "E": ["B", "I"],
    "F": ["C"],
    "G": ["C", "J"],
    "H": ["D"],
    "I": ["E", "J"],
    "J": ["G", "I"],
}

START_NODE = "A"
TARGET_NODE = "J"


def bfs_states(graph, start, target):
    discovered = {start}
    visited = set()
    queue = deque([start])
    states = []

    while queue:
        current = queue.popleft()
        visited.add(current)

        for neighbor in graph[current]:
            if neighbor not in discovered:
                discovered.add(neighbor)
                queue.append(neighbor)

        found = current == target
        states.append(
            {
                "current": current,
                "visited": set(visited),
                "frontier": list(queue),
                "found": found,
                "structure_name": "Queue",
            }
        )

        if found:
            break

    return states


def dfs_states(graph, start, target):
    visited = set()
    stack = [start]
    states = []

    while stack:
        current = stack.pop()

        if current in visited:
            continue

        visited.add(current)

        for neighbor in reversed(graph[current]):
            if neighbor not in visited:
                stack.append(neighbor)

        found = current == target
        states.append(
            {
                "current": current,
                "visited": set(visited),
                "frontier": list(stack),
                "found": found,
                "structure_name": "Stack",
            }
        )

        if found:
            break

    return states


def build_nx_graph(graph):
    nx_graph = nx.Graph()
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            nx_graph.add_edge(node, neighbor)
    return nx_graph


def node_colors(nodes, state, start, target):
    color_map = []
    for node in nodes:
        if node == target and node in state["visited"]:
            color_map.append("#ffbe0b")
        elif node == target:
            color_map.append("#ffd166")
        elif node in state["visited"]:
            color_map.append("#59a14f")
        else:
            color_map.append("#d3d3d3")
    return color_map


def draw_state(ax, nx_graph, pos, state, nodes, algorithm_name, step, total_steps, start, target):
    ax.clear()
    ax.set_axis_off()

    colors = node_colors(nodes, state, start, target)

    nx.draw_networkx_edges(nx_graph, pos=pos, ax=ax, edge_color="#9e9e9e", width=1.8)
    nx.draw_networkx_nodes(
        nx_graph,
        pos=pos,
        ax=ax,
        node_color=colors,
        node_size=1050,
        edgecolors="#444444",
        linewidths=1.2,
    )

    nx.draw_networkx_nodes(
        nx_graph,
        pos=pos,
        ax=ax,
        nodelist=[state["current"]],
        node_color="none",
        node_size=1380,
        edgecolors="#f28e2b",
        linewidths=3.0,
    )

    nx.draw_networkx_labels(nx_graph, pos=pos, ax=ax, font_size=11, font_weight="bold")

    found_text = "FOUND" if state["found"] else "Searching..."
    title = f"{algorithm_name} | Step {step}/{total_steps} | {found_text}"
    ax.set_title(title, fontsize=12, fontweight="bold")

    structure = ", ".join(state["frontier"]) if state["frontier"] else "(empty)"
    info_text = (
        f"Current: {state['current']}\n"
        f"Visited: {len(state['visited'])}\n"
        f"{state['structure_name']}: [{structure}]"
    )
    ax.text(
        0.02,
        0.02,
        info_text,
        transform=ax.transAxes,
        fontsize=9,
        va="bottom",
        ha="left",
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.85},
    )


def animate_traversals(graph, start, target, interval_ms, save_path=None):
    bfs = bfs_states(graph, start, target)
    dfs = dfs_states(graph, start, target)

    nx_graph = build_nx_graph(graph)
    pos = nx.spring_layout(nx_graph, seed=7)
    nodes = sorted(nx_graph.nodes())

    fig, (ax_bfs, ax_dfs) = plt.subplots(1, 2, figsize=(14, 7))
    fig.suptitle(
        f"BFS vs DFS Traversal Animation (Start={start}, Target={target})",
        fontsize=14,
        fontweight="bold",
    )

    legend_handles = [
        Patch(facecolor="none", edgecolor="#f28e2b", label="Current Node (Ring)"),
        Patch(facecolor="#59a14f", edgecolor="#444444", label="Visited"),
        Patch(facecolor="#ffd166", edgecolor="#444444", label="Target"),
        Patch(facecolor="#d3d3d3", edgecolor="#444444", label="Not Visited"),
    ]
    fig.legend(handles=legend_handles, loc="lower center", ncol=4, frameon=False)

    total_frames = max(len(bfs), len(dfs))

    def update(frame):
        bfs_state = bfs[min(frame, len(bfs) - 1)]
        dfs_state = dfs[min(frame, len(dfs) - 1)]

        draw_state(
            ax_bfs,
            nx_graph,
            pos,
            bfs_state,
            nodes,
            "BFS",
            min(frame + 1, len(bfs)),
            len(bfs),
            start,
            target,
        )
        draw_state(
            ax_dfs,
            nx_graph,
            pos,
            dfs_state,
            nodes,
            "DFS",
            min(frame + 1, len(dfs)),
            len(dfs),
            start,
            target,
        )

        return []

    anim = FuncAnimation(
        fig,
        update,
        frames=total_frames,
        interval=interval_ms,
        repeat=False,
        blit=False,
    )

    plt.tight_layout(rect=[0, 0.08, 1, 0.95])

    if save_path:
        anim.save(save_path, dpi=150)
        print(f"Saved animation to {save_path}")

    plt.show()


def parse_args():
    parser = argparse.ArgumentParser(description="Animate BFS and DFS on a small graph.")
    parser.add_argument(
        "--interval",
        type=int,
        default=1200,
        help="Delay between frames in milliseconds (default: 1200)",
    )
    parser.add_argument(
        "--save",
        type=str,
        default=None,
        help="Optional output path (.gif or .mp4) to save the animation",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    animate_traversals(
        graph=GRAPH,
        start=START_NODE,
        target=TARGET_NODE,
        interval_ms=args.interval,
        save_path=args.save,
    )


if __name__ == "__main__":
    main()
