"""Breadth-First Search (BFS) implementation with resource limits and metric tracking."""

import time
from collections import deque
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from algorithms.search_result import SearchResult


def breadth_first_search(
    initial_state: Any,
    get_neighbors_fn: Callable[[Any], List[Tuple[str, Any, float]]],
    is_goal_fn: Callable[[Any], bool],
    max_nodes: int = 50000,
    timeout_sec: float = 10.0,
) -> SearchResult:
    """Perform Breadth-First Search from an initial state to a goal state.

    Args:
        initial_state: Starting state (must be hashable or provide hashable key).
        get_neighbors_fn: Function returning list of (action, next_state, cost).
        is_goal_fn: Predicate returning True if the state satisfies the goal condition.
        max_nodes: Maximum number of explored nodes before terminating search.
        timeout_sec: Maximum execution time in seconds.

    Returns:
        SearchResult containing the solution path, actions, and performance metrics.
    """
    start_time = time.perf_counter()

    # Immediate goal check
    if is_goal_fn(initial_state):
        return SearchResult(
            success=True,
            path=[initial_state],
            actions=[],
            nodes_explored=0,
            max_frontier_size=1,
            execution_time_sec=time.perf_counter() - start_time,
            solution_length=0,
            algorithm_name="Breadth-First Search (BFS)",
        )

    # Node representation: (state, parent_index, action)
    # Storing nodes in a flat list preserves path memory without copying full paths
    nodes_explored = 0
    max_frontier_size = 1

    # Frontier stores indices into a node table
    # node_table[i] = (state, parent_index, action)
    node_table: List[Tuple[Any, Optional[int], Optional[str]]] = [
        (initial_state, None, None)
    ]
    frontier = deque([0])
    visited: Set[Any] = {initial_state}

    goal_node_idx: Optional[int] = None

    while frontier:
        # Check resource limits
        if nodes_explored >= max_nodes:
            return SearchResult(
                success=False,
                nodes_explored=nodes_explored,
                max_frontier_size=max_frontier_size,
                execution_time_sec=time.perf_counter() - start_time,
                error_message=f"Node limit reached ({max_nodes} nodes).",
                algorithm_name="Breadth-First Search (BFS)",
            )

        if time.perf_counter() - start_time > timeout_sec:
            return SearchResult(
                success=False,
                nodes_explored=nodes_explored,
                max_frontier_size=max_frontier_size,
                execution_time_sec=time.perf_counter() - start_time,
                error_message=f"Search timed out after {timeout_sec:.2f} seconds.",
                algorithm_name="Breadth-First Search (BFS)",
            )

        curr_idx = frontier.popleft()
        curr_state = node_table[curr_idx][0]
        nodes_explored += 1

        for action, next_state, _cost in get_neighbors_fn(curr_state):
            if next_state not in visited:
                next_idx = len(node_table)
                node_table.append((next_state, curr_idx, action))
                visited.add(next_state)

                if is_goal_fn(next_state):
                    goal_node_idx = next_idx
                    break

                frontier.append(next_idx)

        if goal_node_idx is not None:
            break

        max_frontier_size = max(max_frontier_size, len(frontier))

    end_time = time.perf_counter()

    if goal_node_idx is None:
        return SearchResult(
            success=False,
            nodes_explored=nodes_explored,
            max_frontier_size=max_frontier_size,
            execution_time_sec=end_time - start_time,
            error_message="Entire reachable state space explored without finding goal.",
            algorithm_name="Breadth-First Search (BFS)",
        )

    # Reconstruct path and actions
    path: List[Any] = []
    actions: List[str] = []
    curr = goal_node_idx
    while curr is not None:
        state, parent_idx, action = node_table[curr]
        path.append(state)
        if action is not None:
            actions.append(action)
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
        algorithm_name="Breadth-First Search (BFS)",
    )
