"""Eight-Puzzle representation, rules, heuristics, and solvability validation."""

import random
from typing import Dict, List, Optional, Tuple

# Standard goal state: 1 to 8 in order with 0 (blank) in the bottom-right
DEFAULT_GOAL: Tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7, 8, 0)

# Predefined benchmark presets with known optimal solution lengths
PRESET_PUZZLES: Dict[str, Tuple[int, ...]] = {
    "Goal State (0 Moves)": (1, 2, 3, 4, 5, 6, 7, 8, 0),
    "Trivial (1 Move)": (1, 2, 3, 4, 5, 0, 7, 8, 6),
    "Easy (2 Moves)": (1, 2, 0, 4, 5, 3, 7, 8, 6),
    "Easy (4 Moves)": (1, 5, 2, 4, 0, 3, 7, 8, 6),
    "Medium (6 Moves)": (1, 5, 2, 4, 8, 3, 0, 7, 6),
    "Medium (8 Moves)": (0, 5, 2, 1, 8, 3, 4, 7, 6),
    "Intermediate (12 Moves)": (5, 8, 2, 1, 7, 3, 0, 4, 6),
    "Challenging (16 Moves)": (8, 7, 2, 5, 0, 3, 1, 4, 6),
    "Unsolvable (Odd Inversions)": (1, 2, 3, 4, 5, 6, 8, 7, 0),
}


class EightPuzzle:
    """Class representing an 8-puzzle board and transition logic."""

    def __init__(self, goal_state: Tuple[int, ...] = DEFAULT_GOAL) -> None:
        """Initialize the 8-puzzle environment with a specified goal state."""
        self.goal_state = goal_state
        self._goal_positions = {
            val: (idx // 3, idx % 3) for idx, val in enumerate(self.goal_state)
        }

    @staticmethod
    def validate_state(state: Tuple[int, ...]) -> Tuple[bool, Optional[str]]:
        """Verify that state is a valid 3x3 permutation of digits 0 through 8."""
        if not isinstance(state, tuple):
            return False, "Puzzle state must be a tuple of integers."
        if len(state) != 9:
            return False, f"Puzzle state must contain 9 tiles, got {len(state)}."
        if set(state) != set(range(9)):
            missing = set(range(9)) - set(state)
            return False, f"Puzzle state must be a permutation of 0-8. Missing: {missing}."
        return True, None

    @staticmethod
    def count_inversions(state: Tuple[int, ...]) -> int:
        """Count the number of inversions in the state, ignoring the blank tile (0).

        An inversion occurs when a tile with a greater number appears before a
        tile with a smaller number in row-major order.
        """
        tiles = [t for t in state if t != 0]
        inversions = 0
        n = len(tiles)
        for i in range(n):
            for j in range(i + 1, n):
                if tiles[i] > tiles[j]:
                    inversions += 1
        return inversions

    @staticmethod
    def is_solvable(
        initial_state: Tuple[int, ...], goal_state: Tuple[int, ...] = DEFAULT_GOAL
    ) -> bool:
        """Determine if initial_state can reach goal_state.

        For a 3x3 grid (odd width), every legal move preserves the parity of
        inversions. Therefore, a state is solvable if and only if its inversion
        parity matches the goal state's inversion parity.
        """
        init_inv = EightPuzzle.count_inversions(initial_state)
        goal_inv = EightPuzzle.count_inversions(goal_state)
        return (init_inv % 2) == (goal_inv % 2)

    @staticmethod
    def explain_solvability(state: Tuple[int, ...], goal_state: Tuple[int, ...] = DEFAULT_GOAL) -> str:
        """Provide detailed mathematical explanation of state solvability."""
        inversions = EightPuzzle.count_inversions(state)
        parity = "even" if inversions % 2 == 0 else "odd"
        if inversions % 2 == 0:
            return (
                f"Solvable (Inversion count: {inversions}, parity: {parity}). "
                "Matches goal state even parity. A valid sequence of sliding moves exists."
            )
        else:
            return (
                f"Mathematically Unsolvable (Inversion count: {inversions}, parity: {parity}). "
                "Sliding tile moves can only alter the inversion count by 0, +2, or -2, strictly preserving parity. "
                "Because the goal state has 0 inversions (even), this board cannot reach the goal through any legal moves."
            )

    @staticmethod
    def explain_transition(from_state: Tuple[int, ...], to_state: Tuple[int, ...]) -> str:
        """Explain the exact physical move between two consecutive board states."""
        b1 = from_state.index(0)
        b2 = to_state.index(0)
        r1, c1 = b1 // 3, b1 % 3
        r2, c2 = b2 // 3, b2 % 3

        moved_tile = from_state[b2]

        if r2 < r1:
            return f"Empty slot moved Up (row {r1 + 1} → {r2 + 1}). Tile {moved_tile} slid Down into row {r1 + 1}, col {c1 + 1}."
        elif r2 > r1:
            return f"Empty slot moved Down (row {r1 + 1} → {r2 + 1}). Tile {moved_tile} slid Up into row {r1 + 1}, col {c1 + 1}."
        elif c2 < c1:
            return f"Empty slot moved Left (col {c1 + 1} → {c2 + 1}). Tile {moved_tile} slid Right into row {r1 + 1}, col {c1 + 1}."
        elif c2 > c1:
            return f"Empty slot moved Right (col {c1 + 1} → {c2 + 1}). Tile {moved_tile} slid Left into row {r1 + 1}, col {c1 + 1}."
        else:
            return "No tile movement occurred."

    @staticmethod
    def parse_state_string(text: str) -> Tuple[Optional[Tuple[int, ...]], Optional[str]]:
        """Parse 9 integers from a string representation (e.g. '1, 2, 3, 4, 5, 6, 7, 8, 0')."""
        import re
        tokens = re.findall(r"\d+", text)
        if len(tokens) != 9:
            return None, f"Expected exactly 9 numbers (0 through 8), found {len(tokens)}."
        try:
            ints = tuple(int(x) for x in tokens)
        except ValueError:
            return None, "All entries must be valid integers."
        is_valid, err = EightPuzzle.validate_state(ints)
        if not is_valid:
            return None, err
        return ints, None

    def is_goal(self, state: Tuple[int, ...]) -> bool:
        """Check if the given state matches the goal state."""
        return state == self.goal_state

    def get_neighbors(
        self, state: Tuple[int, ...]
    ) -> List[Tuple[str, Tuple[int, ...], float]]:
        """Generate valid successor states by sliding the blank tile.

        Returns:
            List of tuples: (action_name, next_state, step_cost).
            Step cost is 1.0 for all sliding moves.
        """
        blank_idx = state.index(0)
        row = blank_idx // 3
        col = blank_idx % 3

        neighbors: List[Tuple[str, Tuple[int, ...], float]] = []

        # Move directions for the blank tile: (delta_row, delta_col, action_name)
        moves = [
            (-1, 0, "Up"),
            (1, 0, "Down"),
            (0, -1, "Left"),
            (0, 1, "Right"),
        ]

        state_list = list(state)
        for dr, dc, action in moves:
            new_r, new_c = row + dr, col + dc
            if 0 <= new_r < 3 and 0 <= new_c < 3:
                target_idx = new_r * 3 + new_c
                # Swap blank tile with adjacent tile
                next_state_list = state_list[:]
                next_state_list[blank_idx], next_state_list[target_idx] = (
                    next_state_list[target_idx],
                    next_state_list[blank_idx],
                )
                neighbors.append((action, tuple(next_state_list), 1.0))

        return neighbors

    def manhattan_distance(self, state: Tuple[int, ...]) -> float:
        """Calculate the sum of Manhattan distances of all non-blank tiles to their goal positions.

        This heuristic is admissible (never overestimates) and consistent.
        """
        distance = 0
        for idx, val in enumerate(state):
            if val != 0:
                cur_r, cur_c = idx // 3, idx % 3
                goal_r, goal_c = self._goal_positions[val]
                distance += abs(cur_r - goal_r) + abs(cur_c - goal_c)
        return float(distance)

    def misplaced_tiles(self, state: Tuple[int, ...]) -> float:
        """Calculate the number of misplaced non-blank tiles.

        Admissible but less informed than Manhattan distance.
        """
        misplaced = 0
        for idx, val in enumerate(state):
            if val != 0 and val != self.goal_state[idx]:
                misplaced += 1
        return float(misplaced)

    @staticmethod
    def generate_random_solvable(
        steps_from_goal: int = 20, seed: Optional[int] = None
    ) -> Tuple[int, ...]:
        """Generate a guaranteed-solvable puzzle by performing random moves from the goal.

        Args:
            steps_from_goal: Number of random sliding moves applied from the goal.
            seed: Optional random seed for reproducibility.

        Returns:
            Solvable state tuple.
        """
        rng = random.Random(seed)
        env = EightPuzzle()
        curr_state = env.goal_state
        last_action = None

        opposite = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}

        for _ in range(steps_from_goal):
            neighbors = env.get_neighbors(curr_state)
            # Avoid immediate reversal to get more interesting states
            valid_moves = [
                n for n in neighbors if opposite.get(n[0]) != last_action
            ]
            if not valid_moves:
                valid_moves = neighbors

            action, next_state, _ = rng.choice(valid_moves)
            last_action = action
            curr_state = next_state

        return curr_state
