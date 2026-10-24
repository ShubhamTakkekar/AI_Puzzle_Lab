"""Data aggregation and statistical analysis of search performance telemetry."""

from typing import Any, Dict, List, Optional
import pandas as pd


def history_to_dataframe(history_records: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert raw session benchmark telemetry records into a structured DataFrame."""
    if not history_records:
        return pd.DataFrame(
            columns=[
                "timestamp",
                "puzzle_type",
                "algorithm",
                "execution_time_ms",
                "nodes_explored",
                "max_frontier_size",
                "solution_length",
                "success",
            ]
        )

    df = pd.DataFrame(history_records)
    # Ensure numeric columns are properly typed
    numeric_cols = ["execution_time_ms", "nodes_explored", "max_frontier_size", "solution_length"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def aggregate_by_algorithm(df: pd.DataFrame, puzzle_type: Optional[str] = None) -> pd.DataFrame:
    """Compute summary statistics grouped by algorithm."""
    if df.empty:
        return pd.DataFrame()

    filtered = df if puzzle_type is None else df[df["puzzle_type"] == puzzle_type]
    if filtered.empty:
        return pd.DataFrame()

    summary = (
        filtered.groupby("algorithm")
        .agg(
            Runs=("success", "count"),
            Success_Rate=("success", lambda x: f"{round(x.mean() * 100, 1)}%"),
            Mean_Time_ms=("execution_time_ms", "mean"),
            Median_Time_ms=("execution_time_ms", "median"),
            Min_Time_ms=("execution_time_ms", "min"),
            Max_Time_ms=("execution_time_ms", "max"),
            Mean_Nodes=("nodes_explored", "mean"),
            Median_Nodes=("nodes_explored", "median"),
        )
        .reset_index()
    )

    # Format floating numbers nicely
    summary["Mean_Time_ms"] = summary["Mean_Time_ms"].round(3)
    summary["Median_Time_ms"] = summary["Median_Time_ms"].round(3)
    summary["Min_Time_ms"] = summary["Min_Time_ms"].round(3)
    summary["Max_Time_ms"] = summary["Max_Time_ms"].round(3)
    summary["Mean_Nodes"] = summary["Mean_Nodes"].round(1)
    summary["Median_Nodes"] = summary["Median_Nodes"].round(1)

    return summary


def export_dataframe_to_csv(df: pd.DataFrame) -> str:
    """Export benchmark DataFrame to a UTF-8 CSV string."""
    return df.to_csv(index=False)
