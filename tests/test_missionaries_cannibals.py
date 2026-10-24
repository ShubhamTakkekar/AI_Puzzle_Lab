"""Unit tests for Missionaries and Cannibals river crossing problem."""

import pytest
from algorithms.bfs import breadth_first_search
from algorithms.dfs import depth_first_search
from puzzles.missionaries_cannibals import GOAL_STATE, INITIAL_STATE, MissionariesCannibals


def test_safety_constraints():
    # Initial state is safe: 3M, 3C on left; 0M, 0C on right
    assert MissionariesCannibals.is_safe(3, 3) is True

    # Safe states
    assert MissionariesCannibals.is_safe(2, 2) is True  # Left: 2M, 2C; Right: 1M, 1C
    assert MissionariesCannibals.is_safe(3, 2) is True  # Left: 3M, 2C; Right: 0M, 1C
    assert MissionariesCannibals.is_safe(0, 0) is True  # Left: 0M, 0C; Right: 3M, 3C (Goal)

    # Unsafe on Left Bank: Missionaries outnumbered
    assert MissionariesCannibals.is_safe(1, 2) is False  # Left: 1M, 2C -> eaten!
    assert MissionariesCannibals.is_safe(1, 3) is False  # Left: 1M, 3C -> eaten!

    # Unsafe on Right Bank: Right bank missionaries outnumbered
    # If Left has 2M, 1C -> Right has (3-2)=1M, (3-1)=2C -> Right bank eaten!
    assert MissionariesCannibals.is_safe(2, 1) is False


def test_bounds():
    assert MissionariesCannibals.is_safe(-1, 2) is False
    assert MissionariesCannibals.is_safe(4, 1) is False
    assert MissionariesCannibals.is_safe(2, 5) is False


def test_initial_neighbors():
    env = MissionariesCannibals()
    neighbors = env.get_neighbors(INITIAL_STATE)
    # From (3, 3, 0), moving 2M leaves (1M, 3C) on left -> eaten!
    # Moving 1M leaves (2M, 3C) on left -> eaten!
    # Safe moves: move 2C, move 1C, or move 1M & 1C
    actions = [action for action, _, _ in neighbors]
    next_states = [state for _, state, _ in neighbors]

    assert len(neighbors) == 3
    assert (3, 1, 1) in next_states  # Sent 2 Cannibals
    assert (3, 2, 1) in next_states  # Sent 1 Cannibal
    assert (2, 2, 1) in next_states  # Sent 1 M and 1 C


def test_bfs_solves_optimally():
    env = MissionariesCannibals()
    res = breadth_first_search(
        initial_state=INITIAL_STATE,
        get_neighbors_fn=env.get_neighbors,
        is_goal_fn=env.is_goal,
    )
    assert res.success is True
    # The classic 3M/3C problem has an optimal solution of 11 boat crossings
    assert res.solution_length == 11
    assert res.path[0] == INITIAL_STATE
    assert res.path[-1] == GOAL_STATE

    # Verify that every state along the path is strictly safe
    for state in res.path:
        m_left, c_left, _ = state
        assert env.is_safe(m_left, c_left) is True


def test_dfs_solves_with_depth_limit():
    env = MissionariesCannibals()
    res = depth_first_search(
        initial_state=INITIAL_STATE,
        get_neighbors_fn=env.get_neighbors,
        is_goal_fn=env.is_goal,
        max_depth=25,
    )
    assert res.success is True
    assert res.path[-1] == GOAL_STATE
    assert res.solution_length >= 11


def test_explain_crossing():
    env = MissionariesCannibals()
    # Left to right move: (3, 3, 0) -> (3, 1, 1) carrying 2 cannibals
    text = env.explain_crossing((3, 3, 0), (3, 1, 1))
    assert "Left Bank to Right Bank" in text
    assert "2 Cannibals" in text
    assert "Right Bank (0M, 2C)" in text

    # Right to left return: (3, 1, 1) -> (3, 2, 0) carrying 1 cannibal back
    text_return = env.explain_crossing((3, 1, 1), (3, 2, 0))
    assert "Right Bank to Left Bank" in text_return
    assert "1 Cannibal" in text_return


def test_custom_boat_capacity():
    # 4 missionaries, 4 cannibals with boat capacity 3
    env = MissionariesCannibals(total_m=4, total_c=4, boat_cap=3)
    neighbors = env.get_neighbors((4, 4, 0))
    # Check that moves with up to 3 passengers are generated
    actions = [action for action, _, _ in neighbors]
    assert any("3 Cannibals" in act or "2 Cannibals" in act for act in actions)
    # Validate is_safe bounds with 4
    assert env.is_safe(4, 4, 4, 4) is True
    assert env.is_safe(3, 4, 4, 4) is False  # Left: 3M, 4C -> eaten!
