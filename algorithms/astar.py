"""A* Search implementation with custom heuristics, tie-breaking, and resource limits."""

import heapq
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from algorithms.search_result import SearchResult


def astar_search(
    initial_state: Any,
    get_neighbors_fn: Callable[[Any], List[Tuple[str, Any, float]]],
    is_goal_fn: Callable[[Any], bool],
    heuristic_fn: Callable[[Any], float],
    max_nodes: int = 50000,
    timeout_sec: float = 10.0,
) -> SearchResult:
    """Perform A* search from an initial state to a goal state.

    Args:
        initial_state: Starting state (must be hashable).
        get_neighbors_fn: Function returning list of (action, next_state, cost).
        is_goal_fn: Predicate returning True if state satisfies goal.
        heuristic_fn: Heuristic function estimating cost from state to goal.
        max_nodes: Maximum nodes to pop/explore before terminating.
        timeout_sec: Maximum execution time in seconds.

    Returns:
        SearchResult containing the optimal path, actions, and performance metrics.
    """
    start_time = time.perf_counter()

    if is_goal_fn(initial_state):
        return SearchResult(
            success=True,
            path=[initial_state],
            actions=[],
            nodes_explored=0,
            max_frontier_size=1,
            execution_time_sec=time.perf_counter() - start_time,
            solution_length=0,
            algorithm_name="A* Search",
        )

    # Node storage: (state, parent_index, action, g_score)
    node_table: List[Tuple[Any, Optional[int], Optional[str], float]] = [
        (initial_state, None, None, 0.0)
    ]

    initial_h = heuristic_fn(initial_state)
    # Priority queue entry: (f_score, h_score, tie_breaker_id, node_idx)
    # Secondary h_score tie-break explores nodes closer to goal first
    counter = 0
    frontier: List[Tuple[float, float, int, int]] = [
        (initial_h, initial_h, counter, 0)
    ]
    heapq.heapify(frontier)

    # Best known g_score for each visited/opened state
    best_g: Dict[Any, float] = {initial_state: 0.0}
    closed_set = set()

    nodes_explored = 0
    max_frontier_size = 1
    goal_node_idx: Optional[int] = None

    while frontier:
        if nodes_explored >= max_nodes:
            return SearchResult(
                success=False,
                nodes_explored=nodes_explored,
                max_frontier_size=max_frontier_size,
                execution_time_sec=time.perf_counter() - start_time,
                error_message=f"Node limit reached ({max_nodes} nodes).",
                algorithm_name="A* Search",
            )

        if time.perf_counter() - start_time > timeout_sec:
            return SearchResult(
                success=False,
                nodes_explored=nodes_explored,
                max_frontier_size=max_frontier_size,
                execution_time_sec=time.perf_counter() - start_time,
                error_message=f"Search timed out after {timeout_sec:.2f} seconds.",
                algorithm_name="A* Search",
            )

        f_val, h_val, _, curr_idx = heapq.heappop(frontier)
        curr_state, parent_idx, action, curr_g = node_table[curr_idx]

        # In consistent heuristics, first expansion is optimal
        if curr_state in closed_set:
            continue
        closed_set.add(curr_state)
        nodes_explored += 1

        if is_goal_fn(curr_state):
            goal_node_idx = curr_idx
            break

        for action_name, next_state, step_cost in get_neighbors_fn(curr_state):
            tentative_g = curr_g + step_cost

            if next_state in closed_set and tentative_g >= best_g.get(next_state, float("inf")):
                continue

            if tentative_g < best_g.get(next_state, float("inf")):
                best_g[next_state] = tentative_g
                h = heuristic_fn(next_state)
                f = tentative_g + h
                next_idx = len(node_table)
                node_table.append((next_state, curr_idx, action_name, tentative_g))
                counter += 1
                heapq.heappush(frontier, (f, h, counter, next_idx))

        max_frontier_size = max(max_frontier_size, len(frontier))

    end_time = time.perf_counter()

    if goal_node_idx is None:
        return SearchResult(
            success=False,
            nodes_explored=nodes_explored,
            max_frontier_size=max_frontier_size,
            execution_time_sec=end_time - start_time,
            error_message="Frontier exhausted without finding goal.",
            algorithm_name="A* Search",
        )

    # Reconstruct path and actions
    path: List[Any] = []
    actions: List[str] = []
    curr = goal_node_idx
    while curr is not None:
        state, parent_idx, action_name, _ = node_table[curr]
        path.append(state)
        if action_name is not None:
            actions.append(action_name)
        curr = parent_idx

    path.reverse()
    actions.reverse()

    return SearchResult(
        success=True,
        path=path,
        actions=actions,
        nodes_explored=nodes_explored,
        max_frontier_size=max_frontier_size,
        execution_time_sec=end_time - start_time,
        solution_length=len(actions),
        algorithm_name="A* Search",
    )
