"""Unit tests for Sudoku CSP validation and MRV backtracking solver."""

import copy
import pytest
from puzzles.sudoku import SUDOKU_PRESETS, Sudoku


def test_sudoku_validation_valid():
    grid = SUDOKU_PRESETS["Easy (35 Clues)"]
    is_valid, err = Sudoku.validate_constraints(grid)
    assert is_valid is True
    assert err is None


def test_sudoku_validation_row_conflict():
    grid = SUDOKU_PRESETS["Invalid (Row Duplicate 5)"]
    is_valid, err = Sudoku.validate_constraints(grid)
    assert is_valid is False
    assert "Duplicate value 5 found in Row 1" in err


def test_sudoku_validation_col_conflict():
    grid = copy.deepcopy(SUDOKU_PRESETS["Easy (35 Clues)"])
    # Row 3 currently has [8, 0, 0, 0, 6, 0, 0, 0, 3] (no 5). Setting grid[3][0] = 5 duplicates 5 in col 0.
    grid[3][0] = 5
    is_valid, err = Sudoku.validate_constraints(grid)
    assert is_valid is False
    assert "Column 1" in err


def test_sudoku_validation_box_conflict():
    grid = copy.deepcopy(SUDOKU_PRESETS["Easy (35 Clues)"])
    # Neither row 0 nor row 2 contains 2. Place 2 at (0, 2) and (2, 0) inside the same top-left 3x3 box.
    grid[0][2] = 2
    grid[2][0] = 2
    is_valid, err = Sudoku.validate_constraints(grid)
    assert is_valid is False
    assert "3x3 block" in err


def test_sudoku_legal_values():
    grid = copy.deepcopy(SUDOKU_PRESETS["Easy (35 Clues)"])
    # Inspect empty cell (0, 2): row 0 has {5,3,7}, col 2 has {8}, box has {5,3,6,9,8}
    legal = Sudoku.get_legal_values(grid, 0, 2)
    assert isinstance(legal, set)
    assert 5 not in legal
    assert 3 not in legal
    assert 9 not in legal


def test_sudoku_solve_easy_preserves_original():
    original = copy.deepcopy(SUDOKU_PRESETS["Easy (35 Clues)"])
    solution = Sudoku.solve(original, use_mrv=True)

    assert solution.success is True
    assert solution.solution_grid is not None
    assert solution.attempted_assignments > 0
    assert solution.execution_time_sec >= 0

    # Ensure original grid was untouched
    assert original == SUDOKU_PRESETS["Easy (35 Clues)"]

    # Verify solution grid is fully completed and valid
    sol = solution.solution_grid
    for r in range(9):
        assert sorted(sol[r]) == list(range(1, 10))
    for c in range(9):
        col_vals = [sol[r][c] for r in range(9)]
        assert sorted(col_vals) == list(range(1, 10))


def test_sudoku_solve_medium():
    grid = SUDOKU_PRESETS["Medium (30 Clues)"]
    solution = Sudoku.solve(grid, use_mrv=True)
    assert solution.success is True
    assert solution.solution_grid is not None


def test_sudoku_unsolvable_board():
    grid = SUDOKU_PRESETS["Unsolvable (No Valid Solution)"]
    solution = Sudoku.solve(grid, use_mrv=True)
    assert solution.success is False
    assert solution.solution_grid is None
    assert "unsolvable" in solution.error_message.lower()


def test_sudoku_invalid_initial_input():
    grid = SUDOKU_PRESETS["Invalid (Row Duplicate 5)"]
    solution = Sudoku.solve(grid)
    assert solution.success is False
    assert "violates constraints" in solution.error_message


def test_sudoku_get_blank_grid():
    blank = Sudoku.get_blank_grid()
    assert len(blank) == 9
    assert all(len(row) == 9 for row in blank)
    assert all(cell == 0 for row in blank for cell in row)


def test_sudoku_find_conflicts():
    blank = Sudoku.get_blank_grid()
    assert Sudoku.find_conflicts(blank) == set()

    # Create row conflict in row 2
    blank[2][1] = 7
    blank[2][6] = 7
    conflicts = Sudoku.find_conflicts(blank)
    assert (2, 1) in conflicts
    assert (2, 6) in conflicts

    # Create col conflict in col 8
    blank[0][8] = 4
    blank[5][8] = 4
    conflicts_col = Sudoku.find_conflicts(blank)
    assert (0, 8) in conflicts_col
    assert (5, 8) in conflicts_col


def test_sudoku_solve_with_trace():
    grid = SUDOKU_PRESETS["Easy (35 Clues)"]
    solution = Sudoku.solve(grid, use_mrv=True, record_trace=True)
    assert solution.success is True
    assert solution.trace is not None
    assert len(solution.trace) > 0

    first_step = solution.trace[0]
    assert hasattr(first_step, "row")
    assert hasattr(first_step, "col")
    assert hasattr(first_step, "val")
    assert hasattr(first_step, "action_type")
    assert hasattr(first_step, "explanation")
    assert first_step.action_type in ("TRY", "BACKTRACK", "SUCCESS")
