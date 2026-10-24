"""Live benchmarking runner for comparing algorithms on identical puzzle instances."""

import datetime
from typing import Any, Dict, List, Tuple
import pandas as pd

from algorithms.astar import astar_search
from algorithms.bfs import breadth_first_search
from algorithms.dfs import depth_first_search
from puzzles.eight_puzzle import EightPuzzle
from puzzles.missionaries_cannibals import INITIAL_STATE, MissionariesCannibals
from puzzles.sudoku import Sudoku


def run_eight_puzzle_benchmark(
    initial_state: Tuple[int, ...],
    algorithms: List[str],
    dfs_max_depth: int = 25,
) -> pd.DataFrame:
    """Execute selected search algorithms on the exact same 8-puzzle board.

    Never invents data: runs live searches and profiles wall-clock execution time.
    """
    env = EightPuzzle()
    records: List[Dict[str, Any]] = []

    for algo in algorithms:
        if algo == "A* Search (Manhattan)":
            res = astar_search(
                initial_state=initial_state,
                get_neighbors_fn=env.get_neighbors,
                is_goal_fn=env.is_goal,
                heuristic_fn=env.manhattan_distance,
                max_nodes=50000,
                timeout_sec=10.0,
            )
        elif algo == "Breadth-First Search (BFS)":
            res = breadth_first_search(
                initial_state=initial_state,
                get_neighbors_fn=env.get_neighbors,
                is_goal_fn=env.is_goal,
                max_nodes=50000,
                timeout_sec=10.0,
            )
        elif algo == "Depth-First Search (DFS)":
            res = depth_first_search(
                initial_state=initial_state,
                get_neighbors_fn=env.get_neighbors,
                is_goal_fn=env.is_goal,
                max_depth=dfs_max_depth,
                max_nodes=50000,
                timeout_sec=10.0,
            )
        else:
            continue

        records.append({
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "puzzle_type": "8-Puzzle",
            "algorithm": algo,
            "execution_time_ms": round(res.execution_time_sec * 1000, 3),
            "nodes_explored": res.nodes_explored,
            "max_frontier_size": res.max_frontier_size,
            "solution_length": res.solution_length if res.success else None,
            "success": res.success,
            "error_message": res.error_message or "",
        })

    return pd.DataFrame(records)


def run_missionaries_benchmark(
    algorithms: List[str],
    dfs_max_depth: int = 30,
) -> pd.DataFrame:
    """Execute selected algorithms on the standard Missionaries and Cannibals problem."""
    env = MissionariesCannibals()
    records: List[Dict[str, Any]] = []

    for algo in algorithms:
        if algo == "Breadth-First Search (BFS)":
            res = breadth_first_search(
                initial_state=INITIAL_STATE,
                get_neighbors_fn=env.get_neighbors,
                is_goal_fn=env.is_goal,
            )
        elif algo == "Depth-First Search (DFS)":
            res = depth_first_search(
                initial_state=INITIAL_STATE,
                get_neighbors_fn=env.get_neighbors,
                is_goal_fn=env.is_goal,
                max_depth=dfs_max_depth,
            )
        else:
            continue

        records.append({
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "puzzle_type": "Missionaries & Cannibals",
            "algorithm": algo,
            "execution_time_ms": round(res.execution_time_sec * 1000, 3),
            "nodes_explored": res.nodes_explored,
            "max_frontier_size": res.max_frontier_size,
            "solution_length": res.solution_length if res.success else None,
            "success": res.success,
            "error_message": res.error_message or "",
        })

    return pd.DataFrame(records)


def run_sudoku_benchmark(
    grid: List[List[int]],
    algorithms: List[str],
) -> pd.DataFrame:
    """Execute Backtracking with vs without MRV on the same Sudoku instance."""
    records: List[Dict[str, Any]] = []

    for algo in algorithms:
        use_mrv = "MRV" in algo
        sol = Sudoku.solve(grid, use_mrv=use_mrv, max_assignments=50000, timeout_sec=10.0)

        records.append({
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "puzzle_type": "Sudoku",
            "algorithm": algo,
            "execution_time_ms": round(sol.execution_time_sec * 1000, 3),
            "nodes_explored": sol.attempted_assignments,
            "max_frontier_size": sol.backtracks_count,
            "solution_length": 81 - sum(row.count(0) for row in grid),
            "success": sol.success,
            "error_message": sol.error_message or "",
        })

    return pd.DataFrame(records)
