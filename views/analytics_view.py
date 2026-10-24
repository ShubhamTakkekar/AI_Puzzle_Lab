"""Data Analytics view: Statistical aggregation, Matplotlib charts, and CSV export."""

import datetime
from typing import List
import pandas as pd
import streamlit as st

from analytics.benchmark import (
    run_eight_puzzle_benchmark,
    run_missionaries_benchmark,
    run_sudoku_benchmark,
)
from analytics.data_analysis import (
    aggregate_by_algorithm,
    export_dataframe_to_csv,
    history_to_dataframe,
)
from analytics.visualizations import (
    plot_execution_time_bar,
    plot_nodes_explored_bar,
    plot_runtime_vs_nodes_scatter,
)
from puzzles.eight_puzzle import PRESET_PUZZLES
from puzzles.sudoku import SUDOKU_PRESETS
from ui.components import render_header


def run_standard_suite() -> None:
    """Execute a balanced standard benchmark suite to populate genuine session telemetry."""
    history = st.session_state.get("benchmark_history", [])

    # 1. 8-Puzzle Easy (4 Moves) with BFS & A*
    df1 = run_eight_puzzle_benchmark(
        initial_state=PRESET_PUZZLES["Easy (4 Moves)"],
        algorithms=["A* Search (Manhattan)", "Breadth-First Search (BFS)"],
    )
    for _, r in df1.iterrows():
        history.append(r.to_dict())

    # 2. 8-Puzzle Medium (8 Moves) with A*
    df2 = run_eight_puzzle_benchmark(
        initial_state=PRESET_PUZZLES["Medium (8 Moves)"],
        algorithms=["A* Search (Manhattan)"],
    )
    for _, r in df2.iterrows():
        history.append(r.to_dict())

    # 3. Missionaries & Cannibals with BFS
    df3 = run_missionaries_benchmark(algorithms=["Breadth-First Search (BFS)"])
    for _, r in df3.iterrows():
        history.append(r.to_dict())

    # 4. Sudoku Easy with MRV Backtracking
    df4 = run_sudoku_benchmark(
        grid=SUDOKU_PRESETS["Easy (35 Clues)"],
        algorithms=["Backtracking (MRV)", "Backtracking (Standard)"],
    )
    for _, r in df4.iterrows():
        history.append(r.to_dict())

    st.session_state["benchmark_history"] = history


def render_analytics_view() -> None:
    """Render the Data Analytics telemetry dashboard."""
    render_header(
        title="Search Telemetry Analytics",
        subtitle="Empirical statistical analysis, distributions, and CSV telemetry export",
        category="Data Science & Telemetry",
    )

    history = st.session_state.get("benchmark_history", [])
    df = history_to_dataframe(history)

    if df.empty:
        st.markdown(
            """
            <div style="background: #111821; border: 1px solid #263341; border-radius: 8px; text-align: center; padding: 2rem 1.5rem; margin-bottom: 1.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #F3F6FA;">No Telemetry Data Recorded Yet</div>
                <p style="color: #A6B3C2; max-width: 600px; margin: 0.4rem auto 1.25rem auto; font-size: 0.9rem;">
                    Execute search algorithms in <strong>8-Puzzle Lab</strong>, <strong>Missionaries Lab</strong>,
                    <strong>Sudoku Lab</strong>, or <strong>Algorithm Arena</strong> to record real CPU performance metrics.
                    Alternatively, execute the standard benchmark suite below.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_left, col_mid, col_right = st.columns([1, 2, 1])
        with col_mid:
            if st.button("🚀 Run Standard Benchmark Suite Now", type="primary", use_container_width=True):
                with st.spinner("Executing live standard benchmark suite..."):
                    run_standard_suite()
                st.rerun()
        return

    # Top KPI Metrics Strip
    total_runs = len(df)
    total_nodes = int(df["nodes_explored"].sum())
    mean_time = df["execution_time_ms"].mean()
    success_rate = (df["success"].mean()) * 100

    st.markdown(
        f"""
        <div class="metric-strip">
            <div class="metric-cell">
                <div class="metric-cell-label">Benchmark Runs</div>
                <div class="metric-cell-value cyan">{total_runs}</div>
            </div>
            <div class="metric-cell">
                <div class="metric-cell-label">Total States Explored</div>
                <div class="metric-cell-value indigo">{total_nodes:,}</div>
            </div>
            <div class="metric-cell">
                <div class="metric-cell-label">Mean Runtime</div>
                <div class="metric-cell-value green">{mean_time:.2f} ms</div>
            </div>
            <div class="metric-cell">
                <div class="metric-cell-label">Success Rate</div>
                <div class="metric-cell-value amber">{success_rate:.1f}%</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Domain Filter
    available_domains = ["All Domains"] + sorted(df["puzzle_type"].dropna().unique().tolist())
    selected_domain = st.selectbox("Filter Telemetry by Puzzle Domain", options=available_domains, index=0)

    filtered_df = df if selected_domain == "All Domains" else df[df["puzzle_type"] == selected_domain]

    st.markdown("### 📈 Visual Performance Distributions")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig_time = plot_execution_time_bar(filtered_df)
        st.pyplot(fig_time, use_container_width=True)

    with chart_col2:
        fig_nodes = plot_nodes_explored_bar(filtered_df)
        st.pyplot(fig_nodes, use_container_width=True)

    fig_scatter = plot_runtime_vs_nodes_scatter(filtered_df)
    st.pyplot(fig_scatter, use_container_width=True)

    # Pandas Statistical Summary Table
    st.markdown("### 📋 Statistical Aggregation Summary")
    summary_df = aggregate_by_algorithm(filtered_df)
    if not summary_df.empty:
        st.dataframe(summary_df, use_container_width=True)

    # Raw Telemetry Log & CSV Export
    st.markdown("### 💾 Raw Telemetry & Dataset Export")
    col_export, col_clear = st.columns([2, 1])

    with col_export:
        csv_data = export_dataframe_to_csv(df)
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="📥 Download Telemetry as CSV",
            data=csv_data,
            file_name=f"ai_puzzle_telemetry_{timestamp_str}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary",
        )

    with col_clear:
        if st.button("🗑️ Clear Session Telemetry", use_container_width=True):
            st.session_state["benchmark_history"] = []
            st.rerun()

    st.markdown("##### Full Session Telemetry Log")
    st.dataframe(df, use_container_width=True)
