"""Unit tests for the 8-puzzle domain, validation, solvability, and heuristics."""

import pytest
from puzzles.eight_puzzle import EightPuzzle, PRESET_PUZZLES, DEFAULT_GOAL


def test_validate_state_valid():
    valid_state = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    is_valid, err = EightPuzzle.validate_state(valid_state)
    assert is_valid is True
    assert err is None


def test_validate_state_invalid_length():
    is_valid, err = EightPuzzle.validate_state((1, 2, 3))
    assert is_valid is False
    assert "9 tiles" in err


def test_validate_state_duplicates():
    dup_state = (1, 1, 2, 3, 4, 5, 6, 7, 8)
    is_valid, err = EightPuzzle.validate_state(dup_state)
    assert is_valid is False
    assert "permutation" in err


def test_count_inversions():
    # Goal state has 0 inversions
    assert EightPuzzle.count_inversions(DEFAULT_GOAL) == 0

    # Inversions in (1, 2, 3, 4, 5, 6, 8, 7, 0): only (8, 7) is inverted -> 1 inversion
    unsolvable = (1, 2, 3, 4, 5, 6, 8, 7, 0)
    assert EightPuzzle.count_inversions(unsolvable) == 1


def test_solvability():
    # Goal state is solvable
    assert EightPuzzle.is_solvable(DEFAULT_GOAL) is True

    # Presets that should be solvable
    assert EightPuzzle.is_solvable(PRESET_PUZZLES["Trivial (1 Move)"]) is True
    assert EightPuzzle.is_solvable(PRESET_PUZZLES["Easy (2 Moves)"]) is True
    assert EightPuzzle.is_solvable(PRESET_PUZZLES["Easy (4 Moves)"]) is True
    assert EightPuzzle.is_solvable(PRESET_PUZZLES["Medium (8 Moves)"]) is True

    # Unsolvable state detection
    assert EightPuzzle.is_solvable(PRESET_PUZZLES["Unsolvable (Odd Inversions)"]) is False


def test_get_neighbors_corner():
    # Blank at bottom-right corner (index 8): can only move Up or Left
    env = EightPuzzle()
    state = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    neighbors = env.get_neighbors(state)
    actions = [action for action, _, _ in neighbors]
    assert sorted(actions) == ["Left", "Up"]
    assert len(neighbors) == 2


def test_get_neighbors_center():
    # Blank at center (index 4): can move Up, Down, Left, Right
    env = EightPuzzle()
    state = (1, 2, 3, 4, 0, 5, 6, 7, 8)
    neighbors = env.get_neighbors(state)
    actions = [action for action, _, _ in neighbors]
    assert sorted(actions) == ["Down", "Left", "Right", "Up"]
    assert len(neighbors) == 4


def test_heuristics_goal():
    env = EightPuzzle()
    assert env.manhattan_distance(DEFAULT_GOAL) == 0.0
    assert env.misplaced_tiles(DEFAULT_GOAL) == 0.0


def test_heuristics_near_goal():
    env = EightPuzzle()
    # One move away: blank at (1, 2), tile 6 at (2, 2)
    # Goal has tile 6 at (1, 2) and blank at (2, 2)
    state = (1, 2, 3, 4, 5, 0, 7, 8, 6)
    assert env.misplaced_tiles(state) == 1.0
    assert env.manhattan_distance(state) == 1.0


def test_generate_random_solvable():
    for steps in [5, 10, 15]:
        state = EightPuzzle.generate_random_solvable(steps_from_goal=steps, seed=42 + steps)
        is_valid, _ = EightPuzzle.validate_state(state)
        assert is_valid is True
        assert EightPuzzle.is_solvable(state) is True


def test_explain_solvability():
    solv_text = EightPuzzle.explain_solvability(DEFAULT_GOAL)
    assert "Solvable" in solv_text
    assert "even" in solv_text

    unsolv_text = EightPuzzle.explain_solvability(PRESET_PUZZLES["Unsolvable (Odd Inversions)"])
    assert "Unsolvable" in unsolv_text
    assert "odd" in unsolv_text


def test_explain_transition():
    s1 = (1, 2, 3, 4, 5, 0, 7, 8, 6)
    s2 = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    desc = EightPuzzle.explain_transition(s1, s2)
    assert "Tile 6" in desc
    assert "Down" in desc or "moved" in desc


def test_parse_state_string():
    parsed, err = EightPuzzle.parse_state_string("1, 2, 3, 4, 5, 6, 7, 8, 0")
    assert err is None
    assert parsed == (1, 2, 3, 4, 5, 6, 7, 8, 0)

    # Invalid length
    _, err_len = EightPuzzle.parse_state_string("1 2 3")
    assert "9 numbers" in err_len

    # Duplicate numbers
    _, err_dup = EightPuzzle.parse_state_string("1 1 2 3 4 5 6 7 8")
    assert "permutation" in err_dup
