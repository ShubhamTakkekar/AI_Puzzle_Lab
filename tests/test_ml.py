"""Unit tests for machine learning dataset generation, feature extraction, and difficulty prediction."""

import pytest
from machine_learning.dataset_generator import (
    classify_difficulty,
    count_linear_conflicts,
    extract_board_features,
)
from machine_learning.predict_difficulty import predict_puzzle_difficulty
from machine_learning.train_model import FEATURE_NAMES, load_model_and_metrics
from puzzles.eight_puzzle import DEFAULT_GOAL, PRESET_PUZZLES


def test_classify_difficulty():
    assert classify_difficulty(0) == "Easy"
    assert classify_difficulty(6) == "Easy"
    assert classify_difficulty(7) == "Medium"
    assert classify_difficulty(12) == "Medium"
    assert classify_difficulty(13) == "Hard"
    assert classify_difficulty(22) == "Hard"


def test_linear_conflicts_goal():
    assert count_linear_conflicts(DEFAULT_GOAL) == 0


def test_linear_conflicts_inverted():
    # Swap tile 1 and tile 2 in first row: (2, 1, 3, 4, 5, 6, 7, 8, 0)
    # Both are in row 0, but reversed relative order -> 1 linear conflict
    state = (2, 1, 3, 4, 5, 6, 7, 8, 0)
    assert count_linear_conflicts(state) >= 1


def test_extract_board_features():
    features = extract_board_features(DEFAULT_GOAL)
    for name in FEATURE_NAMES:
        assert name in features
        assert isinstance(features[name], float)

    # Ensure no target leakage
    assert "optimal_depth" not in features
    assert "difficulty_label" not in features


def test_load_model_and_metrics():
    clf, metrics = load_model_and_metrics()
    assert clf is not None
    assert "accuracy" in metrics
    assert metrics["accuracy"] > 0.60
    assert "feature_importances" in metrics


def test_predict_solvable_easy():
    state = PRESET_PUZZLES["Trivial (1 Move)"]
    res = predict_puzzle_difficulty(state)
    assert res["valid"] is True
    assert res["solvable"] is True
    assert res["predicted_difficulty"] in ["Easy", "Medium", "Hard"]
    assert res["confidence_pct"] > 0
    assert sum(res["probabilities"].values()) == pytest.approx(1.0, abs=0.01)


def test_predict_unsolvable_board():
    unsolvable = PRESET_PUZZLES["Unsolvable (Odd Inversions)"]
    res = predict_puzzle_difficulty(unsolvable)
    assert res["valid"] is True
    assert res["solvable"] is False
    assert res["predicted_difficulty"] == "Unsolvable"
    assert "odd inversion parity" in res["error_message"].lower()
