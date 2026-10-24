"""Reproducible dataset generator for 8-puzzle difficulty classification."""

import random
from typing import Any, Dict, List, Tuple
import pandas as pd

from algorithms.astar import astar_search
from puzzles.eight_puzzle import DEFAULT_GOAL, EightPuzzle


def count_linear_conflicts(state: Tuple[int, ...]) -> int:
    """Count the number of linear conflicts in the 3x3 grid.

    A linear conflict occurs when two tiles are in their goal row (or column),
    but in reversed relative order, requiring at least one to move out of the line.
    """
    conflicts = 0

    # Row conflicts
    for r in range(3):
        row_tiles = [state[r * 3 + c] for c in range(3) if state[r * 3 + c] != 0]
        # Check if tiles belong in this row
        in_row = [t for t in row_tiles if (t - 1) // 3 == r]
        for i in range(len(in_row)):
            for j in range(i + 1, len(in_row)):
                if in_row[i] > in_row[j]:
                    conflicts += 1

    # Column conflicts
    for c in range(3):
        col_tiles = [state[r * 3 + c] for r in range(3) if state[r * 3 + c] != 0]
        in_col = [t for t in col_tiles if (t - 1) % 3 == c]
        for i in range(len(in_col)):
            for j in range(i + 1, len(in_col)):
                if in_col[i] > in_col[j]:
                    conflicts += 1

    return conflicts


def extract_board_features(state: Tuple[int, ...]) -> Dict[str, float]:
    """Extract strictly mathematical state features without target leakage."""
    env = EightPuzzle()
    blank_idx = state.index(0)
    blank_r = blank_idx // 3
    blank_c = blank_idx % 3

    correct_row_count = 0
    correct_col_count = 0
    for idx, val in enumerate(state):
        if val != 0:
            cur_r, cur_c = idx // 3, idx % 3
            goal_r, goal_c = (val - 1) // 3, (val - 1) % 3
            if cur_r == goal_r:
                correct_row_count += 1
            if cur_c == goal_c:
                correct_col_count += 1

    return {
        "manhattan_distance": env.manhattan_distance(state),
        "misplaced_tiles": env.misplaced_tiles(state),
        "inversions_count": float(EightPuzzle.count_inversions(state)),
        "linear_conflicts": float(count_linear_conflicts(state)),
        "blank_row": float(blank_r),
        "blank_col": float(blank_c),
        "correct_row_count": float(correct_row_count),
        "correct_col_count": float(correct_col_count),
    }


def classify_difficulty(optimal_depth: int) -> str:
    """Documented methodology for labeling difficulty:

    - Easy: 0 to 6 moves
    - Medium: 7 to 12 moves
    - Hard: 13+ moves
    """
    if optimal_depth <= 6:
        return "Easy"
    elif optimal_depth <= 12:
        return "Medium"
    else:
        return "Hard"


def generate_difficulty_dataset(num_samples: int = 240, seed: int = 42) -> pd.DataFrame:
    """Generate a reproducible dataset of valid 8-puzzle configurations with ground truth labels.

    Uses A* with Manhattan distance to compute exact optimal solution lengths.
    """
    rng = random.Random(seed)
    env = EightPuzzle()
    records: List[Dict[str, Any]] = []
    seen_states = set()

    # Step ranges tailored to generate a balanced distribution across Easy, Medium, Hard
    step_ranges = [
        (1, 6),    # Easy
        (7, 14),   # Medium
        (15, 24),  # Hard
    ]

    samples_per_bucket = num_samples // 3

    for bucket_min, bucket_max in step_ranges:
        count = 0
        attempts = 0
        while count < samples_per_bucket and attempts < samples_per_bucket * 10:
            attempts += 1
            random_steps = rng.randint(bucket_min, bucket_max)
            state = EightPuzzle.generate_random_solvable(
                steps_from_goal=random_steps, seed=rng.randint(1, 1000000)
            )

            if state in seen_states or state == DEFAULT_GOAL:
                continue
            seen_states.add(state)

            # Solve with A* to get ground truth optimal depth
            res = astar_search(
                initial_state=state,
                get_neighbors_fn=env.get_neighbors,
                is_goal_fn=env.is_goal,
                heuristic_fn=env.manhattan_distance,
                max_nodes=50000,
                timeout_sec=5.0,
            )

            if not res.success:
                continue

            optimal_depth = res.solution_length
            features = extract_board_features(state)
            features["optimal_depth"] = optimal_depth
            features["difficulty_label"] = classify_difficulty(optimal_depth)
            features["state_tuple"] = str(state)

            records.append(features)
            count += 1

    return pd.DataFrame(records)
