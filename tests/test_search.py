"""Unit tests for search algorithms (BFS and A*) on 8-puzzle problems."""

import pytest
from algorithms.bfs import breadth_first_search
from algorithms.astar import astar_search
from puzzles.eight_puzzle import EightPuzzle, PRESET_PUZZLES, DEFAULT_GOAL


def test_bfs_already_at_goal():
    env = EightPuzzle()
    res = breadth_first_search(
        initial_state=DEFAULT_GOAL,
        get_neighbors_fn=env.get_neighbors,
        is_goal_fn=env.is_goal,
    )
    assert res.success is True
    assert res.solution_length == 0
    assert len(res.path) == 1
    assert res.path[0] == DEFAULT_GOAL


def test_astar_already_at_goal():
    env = EightPuzzle()
    res = astar_search(
        initial_state=DEFAULT_GOAL,
        get_neighbors_fn=env.get_neighbors,
        is_goal_fn=env.is_goal,
        heuristic_fn=env.manhattan_distance,
    )
    assert res.success is True
    assert res.solution_length == 0
    assert len(res.path) == 1
    assert res.path[0] == DEFAULT_GOAL


def test_bfs_trivial_solution():
    env = EightPuzzle()
    start = PRESET_PUZZLES["Easy (2 Moves)"]
    res = breadth_first_search(
        initial_state=start,
        get_neighbors_fn=env.get_neighbors,
        is_goal_fn=env.is_goal,
    )
    assert res.success is True
    assert res.solution_length == 2
    assert res.path[0] == start
    assert res.path[-1] == DEFAULT_GOAL
    assert res.execution_time_sec >= 0


def test_astar_trivial_solution():
    env = EightPuzzle()
    start = PRESET_PUZZLES["Easy (2 Moves)"]
    res = astar_search(
        initial_state=start,
        get_neighbors_fn=env.get_neighbors,
        is_goal_fn=env.is_goal,
        heuristic_fn=env.manhattan_distance,
    )
    assert res.success is True
    assert res.solution_length == 2
    assert res.path[0] == start
    assert res.path[-1] == DEFAULT_GOAL


def test_bfs_and_astar_optimality():
    env = EightPuzzle()
    start = PRESET_PUZZLES["Easy (4 Moves)"]

    bfs_res = breadth_first_search(
        initial_state=start,
        get_neighbors_fn=env.get_neighbors,
        is_goal_fn=env.is_goal,
    )
    astar_res = astar_search(
        initial_state=start,
        get_neighbors_fn=env.get_neighbors,
        is_goal_fn=env.is_goal,
        heuristic_fn=env.manhattan_distance,
    )

    assert bfs_res.success is True
    assert astar_res.success is True
    # Both must find optimal path of identical length
    assert bfs_res.solution_length == astar_res.solution_length == 4
    # A* with Manhattan distance should explore fewer or equal nodes than unguided BFS
    assert astar_res.nodes_explored <= bfs_res.nodes_explored


def test_astar_medium_puzzle():
    env = EightPuzzle()
    start = PRESET_PUZZLES["Medium (8 Moves)"]

    res = astar_search(
        initial_state=start,
        get_neighbors_fn=env.get_neighbors,
        is_goal_fn=env.is_goal,
        heuristic_fn=env.manhattan_distance,
    )
    assert res.success is True
    assert res.solution_length == 8
    assert res.path[-1] == DEFAULT_GOAL


def test_search_node_limit():
    env = EightPuzzle()
    start = PRESET_PUZZLES["Challenging (16 Moves)"]

    res = breadth_first_search(
        initial_state=start,
        get_neighbors_fn=env.get_neighbors,
        is_goal_fn=env.is_goal,
        max_nodes=10,
    )
    assert res.success is False
    assert "limit" in res.error_message.lower()


def test_search_timeout():
    env = EightPuzzle()
    start = PRESET_PUZZLES["Challenging (16 Moves)"]

    res = breadth_first_search(
        initial_state=start,
        get_neighbors_fn=env.get_neighbors,
        is_goal_fn=env.is_goal,
        max_nodes=1000000,
        timeout_sec=0.0001,
    )
    assert res.success is False
    assert "timed out" in res.error_message.lower()


def test_dfs_finds_solution_with_depth_limit():
    from algorithms.dfs import depth_first_search

    env = EightPuzzle()
    start = PRESET_PUZZLES["Easy (2 Moves)"]

    res = depth_first_search(
        initial_state=start,
        get_neighbors_fn=env.get_neighbors,
        is_goal_fn=env.is_goal,
        max_depth=10,
    )
    assert res.success is True
    assert res.path[0] == start
    assert res.path[-1] == DEFAULT_GOAL


def test_dfs_respects_max_depth():
    from algorithms.dfs import depth_first_search

    env = EightPuzzle()
    # 4-move puzzle with max_depth=2 cannot reach goal
    start = PRESET_PUZZLES["Easy (4 Moves)"]

    res = depth_first_search(
        initial_state=start,
        get_neighbors_fn=env.get_neighbors,
        is_goal_fn=env.is_goal,
        max_depth=2,
    )
    assert res.success is False
    assert "depth" in res.error_message.lower()

