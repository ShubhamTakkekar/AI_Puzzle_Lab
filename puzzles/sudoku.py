"""Sudoku 9x9 puzzle representation, constraint checking, and MRV backtracking solver."""

import copy
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

Grid = List[List[int]]


@dataclass
class SudokuTraceStep:
    """Represents a discrete decision step in the backtracking search."""

    row: int
    col: int
    val: int
    action_type: str  # "TRY", "CONFLICT", "BACKTRACK", "SUCCESS"
    explanation: str
    grid_snapshot: Grid


@dataclass
class SudokuSolution:
    """Telemetry and outcome of a Sudoku solving run."""

    success: bool
    solution_grid: Optional[Grid] = None
    original_grid: Grid = field(default_factory=list)
    attempted_assignments: int = 0
    backtracks_count: int = 0
    execution_time_sec: float = 0.0
    error_message: Optional[str] = None
    steps_history: List[Tuple[int, int, int]] = field(default_factory=list)
    trace: List[SudokuTraceStep] = field(default_factory=list)


# Verified presets
SUDOKU_PRESETS: Dict[str, Grid] = {
    "Easy (35 Clues)": [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ],
    "Medium (30 Clues)": [
        [0, 0, 0, 2, 6, 0, 7, 0, 1],
        [6, 8, 0, 0, 7, 0, 0, 9, 0],
        [1, 9, 0, 0, 0, 4, 5, 0, 0],
        [8, 2, 0, 1, 0, 0, 0, 4, 0],
        [0, 0, 4, 6, 0, 2, 9, 0, 0],
        [0, 5, 0, 0, 0, 3, 0, 2, 8],
        [0, 0, 9, 3, 0, 0, 0, 7, 4],
        [0, 4, 0, 0, 5, 0, 0, 3, 6],
        [7, 0, 3, 0, 1, 8, 0, 0, 0],
    ],
    "Hard (24 Clues)": [
        [0, 0, 0, 6, 0, 0, 4, 0, 0],
        [7, 0, 0, 0, 0, 3, 6, 0, 0],
        [0, 0, 0, 0, 9, 1, 0, 8, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 5, 0, 1, 8, 0, 0, 0, 3],
        [0, 0, 0, 3, 0, 6, 0, 4, 5],
        [0, 4, 0, 2, 0, 0, 0, 6, 0],
        [9, 0, 3, 0, 0, 0, 0, 0, 0],
        [0, 2, 0, 0, 0, 0, 1, 0, 0],
    ],
    "Invalid (Row Duplicate 5)": [
        [5, 3, 5, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ],
    "Unsolvable (No Valid Solution)": [
        # Valid initially (no duplicate in any row/col/box), but mathematically uncompletable
        [5, 1, 6, 8, 4, 9, 7, 3, 2],
        [3, 0, 7, 6, 0, 5, 0, 0, 0],
        [8, 0, 9, 7, 0, 0, 0, 6, 5],
        [1, 3, 5, 0, 6, 0, 9, 0, 7],
        [4, 7, 2, 5, 9, 1, 0, 0, 6],
        [9, 6, 8, 3, 7, 0, 0, 5, 0],
        [2, 5, 3, 1, 8, 6, 0, 7, 4],
        [6, 8, 4, 2, 0, 7, 5, 0, 0],
        [7, 9, 1, 0, 5, 0, 6, 0, 8],
    ],
}


class Sudoku:
    """Sudoku CSP problem modeling and backtracking solver."""

    @staticmethod
    def is_valid_grid_structure(grid: Grid) -> Tuple[bool, Optional[str]]:
        """Verify grid dimensions and value bounds (0-9)."""
        if not isinstance(grid, list) or len(grid) != 9:
            return False, "Grid must have exactly 9 rows."
        for r_idx, row in enumerate(grid):
            if not isinstance(row, list) or len(row) != 9:
                return False, f"Row {r_idx + 1} must contain exactly 9 cells."
            for val in row:
                if not isinstance(val, int) or val < 0 or val > 9:
                    return False, f"Invalid value '{val}'. Allowed values are integers 0-9."
        return True, None

    @staticmethod
    def validate_constraints(grid: Grid) -> Tuple[bool, Optional[str]]:
        """Validate that no initial duplicates exist in any row, column, or 3x3 box."""
        is_struct_valid, err = Sudoku.is_valid_grid_structure(grid)
        if not is_struct_valid:
            return False, err

        # Check rows
        for r in range(9):
            seen: Set[int] = set()
            for c in range(9):
                val = grid[r][c]
                if val != 0:
                    if val in seen:
                        return False, f"Duplicate value {val} found in Row {r + 1}."
                    seen.add(val)

        # Check columns
        for c in range(9):
            seen = set()
            for r in range(9):
                val = grid[r][c]
                if val != 0:
                    if val in seen:
                        return False, f"Duplicate value {val} found in Column {c + 1}."
                    seen.add(val)

        # Check 3x3 boxes
        for box_r in range(3):
            for box_c in range(3):
                seen = set()
                for r in range(box_r * 3, box_r * 3 + 3):
                    for c in range(box_c * 3, box_c * 3 + 3):
                        val = grid[r][c]
                        if val != 0:
                            if val in seen:
                                return False, f"Duplicate value {val} found in 3x3 block ({box_r + 1}, {box_c + 1})."
                            seen.add(val)

        return True, None

    @staticmethod
    def get_legal_values(grid: Grid, row: int, col: int) -> Set[int]:
        """Compute the set of numbers 1-9 that can be legally placed at (row, col)."""
        if grid[row][col] != 0:
            return set()

        used: Set[int] = set()

        # Row and Column values
        for i in range(9):
            if grid[row][i] != 0:
                used.add(grid[row][i])
            if grid[i][col] != 0:
                used.add(grid[i][col])

        # 3x3 Box values
        box_start_r = (row // 3) * 3
        box_start_c = (col // 3) * 3
        for r in range(box_start_r, box_start_r + 3):
            for c in range(box_start_c, box_start_c + 3):
                if grid[r][c] != 0:
                    used.add(grid[r][c])

        return set(range(1, 10)) - used

    @staticmethod
    def find_mrv_cell(grid: Grid) -> Optional[Tuple[int, int, Set[int]]]:
        """Find the empty cell with the Minimum Remaining Values (MRV heuristic).

        Returns:
            Tuple of (row, col, legal_candidates), or None if grid is completely filled.
        """
        best_cell = None
        min_candidates = 10

        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    candidates = Sudoku.get_legal_values(grid, r, c)
                    # Immediate dead end: 0 legal values
                    if len(candidates) == 0:
                        return (r, c, set())

                    if len(candidates) < min_candidates:
                        min_candidates = len(candidates)
                        best_cell = (r, c, candidates)
                        if min_candidates == 1:
                            return best_cell

        return best_cell

    @staticmethod
    def get_blank_grid() -> Grid:
        """Return an empty 9x9 Sudoku grid."""
        return [[0 for _ in range(9)] for _ in range(9)]

    @staticmethod
    def find_conflicts(grid: Grid) -> Set[Tuple[int, int]]:
        """Identify all grid cells currently involved in row, column, or 3x3 block conflicts."""
        conflicts: Set[Tuple[int, int]] = set()

        # Row conflicts
        for r in range(9):
            row_vals: Dict[int, List[int]] = {}
            for c in range(9):
                v = grid[r][c]
                if v != 0:
                    row_vals.setdefault(v, []).append(c)
            for v, cols in row_vals.items():
                if len(cols) > 1:
                    for c in cols:
                        conflicts.add((r, c))

        # Column conflicts
        for c in range(9):
            col_vals: Dict[int, List[int]] = {}
            for r in range(9):
                v = grid[r][c]
                if v != 0:
                    col_vals.setdefault(v, []).append(r)
            for v, rows in col_vals.items():
                if len(rows) > 1:
                    for r in rows:
                        conflicts.add((r, c))

        # 3x3 Block conflicts
        for box_r in range(3):
            for box_c in range(3):
                box_vals: Dict[int, List[Tuple[int, int]]] = {}
                for r in range(box_r * 3, box_r * 3 + 3):
                    for c in range(box_c * 3, box_c * 3 + 3):
                        v = grid[r][c]
                        if v != 0:
                            box_vals.setdefault(v, []).append((r, c))
                for v, coords in box_vals.items():
                    if len(coords) > 1:
                        for coord in coords:
                            conflicts.add(coord)

        return conflicts

    @staticmethod
    def solve(
        grid: Grid,
        use_mrv: bool = True,
        max_assignments: int = 100000,
        timeout_sec: float = 10.0,
        record_trace: bool = False,
    ) -> SudokuSolution:
        """Solve a Sudoku puzzle using constraint-aware backtracking with MRV.

        Never modifies the input grid.
        """
        start_time = time.perf_counter()

        # Validate initial puzzle for conflicts
        is_valid, err_msg = Sudoku.validate_constraints(grid)
        if not is_valid:
            return SudokuSolution(
                success=False,
                original_grid=copy.deepcopy(grid),
                execution_time_sec=time.perf_counter() - start_time,
                error_message=f"Initial grid violates constraints: {err_msg}",
            )

        # Work on a detached deep copy to preserve the original grid
        working_grid = copy.deepcopy(grid)
        original_copy = copy.deepcopy(grid)

        attempted_assignments = 0
        backtracks_count = 0
        steps_history: List[Tuple[int, int, int]] = []
        trace: List[SudokuTraceStep] = []

        def backtrack() -> bool:
            nonlocal attempted_assignments, backtracks_count

            if attempted_assignments >= max_assignments:
                return False

            if time.perf_counter() - start_time > timeout_sec:
                return False

            if use_mrv:
                mrv_res = Sudoku.find_mrv_cell(working_grid)
                if mrv_res is None:
                    return True  # All cells filled!
                r, c, candidates = mrv_res
                if not candidates:
                    if record_trace and len(trace) < 600:
                        trace.append(SudokuTraceStep(
                            row=r, col=c, val=0, action_type="CONFLICT",
                            explanation=f"Domain wipeout at Row {r + 1}, Col {c + 1}: 0 legal candidates remaining. Backtracking.",
                            grid_snapshot=copy.deepcopy(working_grid),
                        ))
                    return False  # Dead end reached
            else:
                found = False
                for row_idx in range(9):
                    for col_idx in range(9):
                        if working_grid[row_idx][col_idx] == 0:
                            r, c = row_idx, col_idx
                            candidates = Sudoku.get_legal_values(working_grid, r, c)
                            found = True
                            break
                    if found:
                        break
                if not found:
                    return True
                if not candidates:
                    return False

            for val in sorted(candidates):
                attempted_assignments += 1
                working_grid[r][c] = val
                if len(steps_history) < 500:
                    steps_history.append((r, c, val))

                if record_trace and len(trace) < 600:
                    trace.append(SudokuTraceStep(
                        row=r, col=c, val=val, action_type="TRY",
                        explanation=f"Assigning {val} to Row {r + 1}, Col {c + 1} ({len(candidates)} legal candidates).",
                        grid_snapshot=copy.deepcopy(working_grid),
                    ))

                if backtrack():
                    return True

                # Backtrack
                working_grid[r][c] = 0
                backtracks_count += 1

                if record_trace and len(trace) < 600:
                    trace.append(SudokuTraceStep(
                        row=r, col=c, val=0, action_type="BACKTRACK",
                        explanation=f"Backtracking: Choice {val} at Row {r + 1}, Col {c + 1} failed. Resetting cell.",
                        grid_snapshot=copy.deepcopy(working_grid),
                    ))

            return False

        solved = backtrack()
        total_time = time.perf_counter() - start_time

        if solved and record_trace:
            trace.append(SudokuTraceStep(
                row=8, col=8, val=working_grid[8][8], action_type="SUCCESS",
                explanation="All 81 cells successfully assigned without constraint conflicts!",
                grid_snapshot=copy.deepcopy(working_grid),
            ))

        if attempted_assignments >= max_assignments:
            err = f"Assignment limit ({max_assignments}) exceeded."
        elif total_time > timeout_sec:
            err = f"Search timed out after {timeout_sec:.2f} seconds."
        elif not solved:
            err = "Puzzle is mathematically unsolvable with the given clues."
        else:
            err = None

        return SudokuSolution(
            success=solved,
            solution_grid=working_grid if solved else None,
            original_grid=original_copy,
            attempted_assignments=attempted_assignments,
            backtracks_count=backtracks_count,
            execution_time_sec=total_time,
            error_message=err,
            steps_history=steps_history,
            trace=trace,
        )
