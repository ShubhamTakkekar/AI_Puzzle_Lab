"""Depth-First Search (DFS) implementation with depth and resource bounding."""

import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from algorithms.search_result import SearchResult


def depth_first_search(
    initial_state: Any,
    get_neighbors_fn: Callable[[Any], List[Tuple[str, Any, float]]],
    is_goal_fn: Callable[[Any], bool],
    max_depth: int = 50,
    max_nodes: int = 50000,
    timeout_sec: float = 10.0,
) -> SearchResult:
    """Perform Depth-First Search with depth and resource bounding.

    Uses an explicit stack and path-based cycle detection to explore
    deeply without falling into infinite cycles or consuming unbounded memory.

    Args:
        initial_state: Starting state (must be hashable).
        get_neighbors_fn: Function returning list of (action, next_state, cost).
        is_goal_fn: Predicate returning True if the state satisfies the goal condition.
        max_depth: Maximum tree depth to explore along any path.
        max_nodes: Maximum number of explored nodes before terminating.
        timeout_sec: Maximum execution time in seconds.

    Returns:
        SearchResult containing the path, actions, and performance metrics.
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
            algorithm_name="Depth-First Search (DFS)",
        )

    # Node storage: (state, parent_index, action, depth)
    node_table: List[Tuple[Any, Optional[int], Optional[str], int]] = [
        (initial_state, None, None, 0)
    ]

    # Stack stores node_index
    stack: List[int] = [0]
    # Keep track of states along current path or visited with depth to prune cycles
    visited_depth: Dict[Any, int] = {initial_state: 0}

    nodes_explored = 0
    max_frontier_size = 1
    goal_node_idx: Optional[int] = None

    while stack:
        if nodes_explored >= max_nodes:
            return SearchResult(
                success=False,
                nodes_explored=nodes_explored,
                max_frontier_size=max_frontier_size,
                execution_time_sec=time.perf_counter() - start_time,
                error_message=f"DFS node exploration limit reached ({max_nodes} nodes).",
                algorithm_name="Depth-First Search (DFS)",
            )

        if time.perf_counter() - start_time > timeout_sec:
            return SearchResult(
                success=False,
                nodes_explored=nodes_explored,
                max_frontier_size=max_frontier_size,
                execution_time_sec=time.perf_counter() - start_time,
                error_message=f"DFS search timed out after {timeout_sec:.2f} seconds.",
                algorithm_name="Depth-First Search (DFS)",
            )

        curr_idx = stack.pop()
        curr_state, parent_idx, action, curr_depth = node_table[curr_idx]
        nodes_explored += 1

        if is_goal_fn(curr_state):
            goal_node_idx = curr_idx
            break

        # Only expand children if below max_depth
        if curr_depth < max_depth:
            # Reverse neighbors so they are explored in natural left-to-right order on LIFO stack
            for action_name, next_state, _cost in reversed(get_neighbors_fn(curr_state)):
                next_depth = curr_depth + 1
                # Prune if already visited at a shallower or equal depth
                if next_state in visited_depth and visited_depth[next_state] <= next_depth:
                    continue

                visited_depth[next_state] = next_depth
                next_idx = len(node_table)
                node_table.append((next_state, curr_idx, action_name, next_depth))
                stack.append(next_idx)

        max_frontier_size = max(max_frontier_size, len(stack))

    end_time = time.perf_counter()

    if goal_node_idx is None:
        return SearchResult(
            success=False,
            nodes_explored=nodes_explored,
            max_frontier_size=max_frontier_size,
            execution_time_sec=end_time - start_time,
            error_message=f"DFS exhausted search space up to max depth {max_depth} without finding goal.",
            algorithm_name="Depth-First Search (DFS)",
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
        algorithm_name="Depth-First Search (DFS)",
    )
