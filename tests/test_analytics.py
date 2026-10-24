"""Unit tests for analytics, benchmarking, and telemetry processing."""

import pandas as pd
import pytest

from analytics.benchmark import run_eight_puzzle_benchmark
from analytics.data_analysis import (
    aggregate_by_algorithm,
    export_dataframe_to_csv,
    history_to_dataframe,
)
from puzzles.eight_puzzle import PRESET_PUZZLES


def test_history_to_dataframe_empty():
    df = history_to_dataframe([])
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    assert "execution_time_ms" in df.columns


def test_history_to_dataframe_populated():
    sample = [
        {
            "timestamp": "12:00:00",
            "puzzle_type": "8-Puzzle",
            "algorithm": "A*",
            "execution_time_ms": 1.5,
            "nodes_explored": 10,
            "max_frontier_size": 5,
            "solution_length": 4,
            "success": True,
        }
    ]
    df = history_to_dataframe(sample)
    assert len(df) == 1
    assert df["execution_time_ms"].iloc[0] == 1.5
    assert df["nodes_explored"].iloc[0] == 10


def test_aggregate_by_algorithm():
    records = [
        {
            "puzzle_type": "8-Puzzle",
            "algorithm": "BFS",
            "execution_time_ms": 10.0,
            "nodes_explored": 100,
            "max_frontier_size": 20,
            "solution_length": 4,
            "success": True,
        },
        {
            "puzzle_type": "8-Puzzle",
            "algorithm": "BFS",
            "execution_time_ms": 20.0,
            "nodes_explored": 200,
            "max_frontier_size": 40,
            "solution_length": 4,
            "success": True,
        },
    ]
    df = history_to_dataframe(records)
    summary = aggregate_by_algorithm(df)

    assert len(summary) == 1
    row = summary.iloc[0]
    assert row["algorithm"] == "BFS"
    assert row["Runs"] == 2
    assert row["Mean_Time_ms"] == 15.0
    assert row["Mean_Nodes"] == 150.0


def test_export_csv():
    records = [
        {
            "puzzle_type": "8-Puzzle",
            "algorithm": "A*",
            "execution_time_ms": 2.5,
            "nodes_explored": 8,
            "max_frontier_size": 3,
            "solution_length": 2,
            "success": True,
        }
    ]
    df = history_to_dataframe(records)
    csv_str = export_dataframe_to_csv(df)
    assert "algorithm" in csv_str
    assert "A*" in csv_str
    assert "2.5" in csv_str


def test_run_eight_puzzle_benchmark():
    state = PRESET_PUZZLES["Easy (2 Moves)"]
    df = run_eight_puzzle_benchmark(
        initial_state=state,
        algorithms=["A* Search (Manhattan)", "Breadth-First Search (BFS)"],
    )
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert set(df["algorithm"].tolist()) == {
        "A* Search (Manhattan)",
        "Breadth-First Search (BFS)",
    }
    assert all(df["success"] == True)
    assert all(df["solution_length"] == 2)
