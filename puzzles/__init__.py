"""AI Puzzle environments package."""

from puzzles.eight_puzzle import DEFAULT_GOAL, PRESET_PUZZLES, EightPuzzle
from puzzles.missionaries_cannibals import (
    BOAT_CAPACITY,
    GOAL_STATE,
    INITIAL_STATE,
    MissionariesCannibals,
)
from puzzles.sudoku import SUDOKU_PRESETS, Sudoku, SudokuSolution

__all__ = [
    "EightPuzzle",
    "PRESET_PUZZLES",
    "DEFAULT_GOAL",
    "MissionariesCannibals",
    "INITIAL_STATE",
    "GOAL_STATE",
    "BOAT_CAPACITY",
    "Sudoku",
    "SudokuSolution",
    "SUDOKU_PRESETS",
]
