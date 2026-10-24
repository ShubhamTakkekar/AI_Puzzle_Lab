"""Algorithm Arena: Empirical head-to-head benchmarking console."""

from typing import List, Optional, Tuple
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from analytics.benchmark import (
    run_eight_puzzle_benchmark,
    run_missionaries_benchmark,
    run_sudoku_benchmark,
)
from puzzles.eight_puzzle import PRESET_PUZZLES
from puzzles.sudoku import SUDOKU_PRESETS
from ui.components import render_header


def plot_arena_charts(df: pd.DataFrame) -> Tuple[plt.Figure, plt.Figure]:
    """Generate two clean dark-themed comparison bar charts for the Arena."""
    # Chart 1: Execution Time
    fig_time, ax_time = plt.subplots(figsize=(5.5, 3.2), dpi=100)
    fig_time.patch.set_facecolor("#0B0F14")
    ax_time.set_facecolor("#111821")

    algos = df["algorithm"]
    times = df["execution_time_ms"]
    colors = ["#45C6D9", "#7C8CFF", "#F4B860", "#48D597"][:len(algos)]

    bars1 = ax_time.bar(algos, times, color=colors, width=0.5, edgecolor="#263341")
    for bar in bars1:
        h = bar.get_height()
        ax_time.annotate(
            f"{h:.2f}ms",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center", va="bottom",
            color="#F3F6FA", fontsize=8, fontweight="bold",
        )

    ax_time.set_title("Execution Time (ms)", color="#F3F6FA", fontsize=10, fontweight="bold", pad=8)
    ax_time.set_ylabel("ms", color="#A6B3C2", fontsize=8.5)
    ax_time.tick_params(colors="#A6B3C2", labelsize=8)
    ax_time.set_xticks(range(len(algos)))
    ax_time.set_xticklabels(algos, rotation=12, ha="right")
    for spine in ax_time.spines.values():
        spine.set_color("#263341")
    ax_time.grid(True, linestyle="--", alpha=0.2, color="#263341")
    fig_time.tight_layout()

    # Chart 2: Explored Nodes
    fig_nodes, ax_nodes = plt.subplots(figsize=(5.5, 3.2), dpi=100)
    fig_nodes.patch.set_facecolor("#0B0F14")
    ax_nodes.set_facecolor("#111821")

    nodes = df["nodes_explored"]
    bars2 = ax_nodes.bar(algos, nodes, color=colors, width=0.5, edgecolor="#263341")
    for bar in bars2:
        h = bar.get_height()
        ax_nodes.annotate(
            f"{int(h):,}",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center", va="bottom",
            color="#F3F6FA", fontsize=8, fontweight="bold",
        )

    ax_nodes.set_title("Explored States / Nodes", color="#F3F6FA", fontsize=10, fontweight="bold", pad=8)
    ax_nodes.set_ylabel("Count", color="#A6B3C2", fontsize=8.5)
    ax_nodes.tick_params(colors="#A6B3C2", labelsize=8)
    ax_nodes.set_xticks(range(len(algos)))
    ax_nodes.set_xticklabels(algos, rotation=12, ha="right")
    for spine in ax_nodes.spines.values():
        spine.set_color("#263341")
    ax_nodes.grid(True, linestyle="--", alpha=0.2, color="#263341")
    fig_nodes.tight_layout()

    return fig_time, fig_nodes


def render_arena_view() -> None:
    """Render the product-grade Algorithm Arena benchmarking suite."""
    render_header(
        title="Algorithm Arena",
        subtitle="Empirical head-to-head comparisons on identical problem instances",
        category="Live Benchmarking Console",
    )

    # Top Status Bar
    last_df: Optional[pd.DataFrame] = st.session_state.get("last_arena_results")
    status_label = "Benchmark Completed" if last_df is not None else "Ready for Experiment"
    status_tag = "success" if last_df is not None else "info"

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; background: #111821; border: 1px solid #263341; border-radius: 6px; padding: 0.6rem 0.9rem; margin-bottom: 1rem;">
            <div style="font-size: 0.85rem; color: #A6B3C2;">
                Hardware: <strong>Local CPU</strong> · Timing: <strong>Wall-clock perf_counter</strong> · Target: <strong>Synchronous Execution</strong>
            </div>
            <span class="status-tag {status_tag}">{status_label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_cfg, col_res = st.columns([1, 1.4], gap="large")

    with col_cfg:
        st.markdown("#### ⚙️ Benchmark Configuration")

        domain = st.selectbox(
            "Select Problem Domain",
            options=["8-Puzzle", "Missionaries & Cannibals", "Sudoku"],
            index=0,
        )

        selected_algos: List[str] = []
        dfs_depth = 20

        if domain == "8-Puzzle":
            preset_name = st.selectbox(
                "8-Puzzle Instance",
                options=[k for k in PRESET_PUZZLES.keys() if "Unsolvable" not in k],
                index=3,  # Easy (4 Moves)
            )
            dfs_depth = st.slider("DFS Max Depth Limit", min_value=10, max_value=30, value=20)

            st.markdown("##### Select Compatible Strategies")
            if st.checkbox("A* Search (Manhattan Distance)", value=True):
                selected_algos.append("A* Search (Manhattan)")
            if st.checkbox("Breadth-First Search (BFS)", value=True):
                selected_algos.append("Breadth-First Search (BFS)")
            if st.checkbox("Depth-First Search (DFS - Bounded)", value=True):
                selected_algos.append("Depth-First Search (DFS)")

            if st.button("⚔️ Run 8-Puzzle Comparison", type="primary", use_container_width=True):
                if not selected_algos:
                    st.warning("Please check at least one algorithm.")
                else:
                    target_st = PRESET_PUZZLES[preset_name]
                    with st.spinner("Benchmarking algorithms against identical board..."):
                        res_df = run_eight_puzzle_benchmark(
                            initial_state=target_st,
                            algorithms=selected_algos,
                            dfs_max_depth=dfs_depth,
                        )
                        st.session_state["last_arena_results"] = res_df
                        for _, row in res_df.iterrows():
                            st.session_state["benchmark_history"].append(row.to_dict())
                    st.rerun()

        elif domain == "Missionaries & Cannibals":
            st.info("Classic 3 Missionaries, 3 Cannibals, 2-Person Boat river crossing.")
            dfs_depth = st.slider("DFS Max Depth Limit", min_value=11, max_value=40, value=25)

            st.markdown("##### Select Compatible Strategies")
            if st.checkbox("Breadth-First Search (BFS - Shortest Path)", value=True):
                selected_algos.append("Breadth-First Search (BFS)")
            if st.checkbox("Depth-First Search (DFS - Bounded)", value=True):
                selected_algos.append("Depth-First Search (DFS)")

            if st.button("⚔️ Run River Crossing Comparison", type="primary", use_container_width=True):
                if not selected_algos:
                    st.warning("Please check at least one algorithm.")
                else:
                    with st.spinner("Benchmarking river crossing search strategies..."):
                        res_df = run_missionaries_benchmark(
                            algorithms=selected_algos,
                            dfs_max_depth=dfs_depth,
                        )
                        st.session_state["last_arena_results"] = res_df
                        for _, row in res_df.iterrows():
                            st.session_state["benchmark_history"].append(row.to_dict())
                    st.rerun()

        else:  # Sudoku
            preset_name = st.selectbox(
                "Sudoku Instance",
                options=[k for k in SUDOKU_PRESETS.keys() if "Invalid" not in k and "Unsolvable" not in k],
                index=0,
            )

            st.markdown("##### Select Backtracking Variants")
            if st.checkbox("Backtracking with MRV Heuristic", value=True):
                selected_algos.append("Backtracking (MRV)")
            if st.checkbox("Backtracking (Standard Linear Scan)", value=True):
                selected_algos.append("Backtracking (Standard)")

            if st.button("⚔️ Run Sudoku Comparison", type="primary", use_container_width=True):
                if not selected_algos:
                    st.warning("Please select at least one algorithm.")
                else:
                    grid = SUDOKU_PRESETS[preset_name]
                    with st.spinner("Benchmarking backtracking variants..."):
                        res_df = run_sudoku_benchmark(grid=grid, algorithms=selected_algos)
                        st.session_state["last_arena_results"] = res_df
                        for _, row in res_df.iterrows():
                            st.session_state["benchmark_history"].append(row.to_dict())
                    st.rerun()

    with col_res:
        st.markdown("#### 📊 Head-to-Head Experimental Telemetry")

        if last_df is None or last_df.empty:
            st.markdown(
                """
                <div style="background: #111821; border: 1px solid #263341; border-radius: 8px; padding: 2.5rem 1.5rem; text-align: center; color: #6C7D93;">
                    <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">⚔️</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #F3F6FA;">No Comparison Run Yet</div>
                    <p style="font-size: 0.85rem; max-width: 400px; margin: 0.4rem auto 0 auto;">
                        Select a problem domain, configure compatible algorithms on the left, and click 
                        <strong>Run Comparison</strong> to profile real wall-clock performance.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            # Comparative Side-by-Side Metric Chips
            chip_cols = st.columns(len(last_df))
            for idx, (_, row) in enumerate(last_df.iterrows()):
                with chip_cols[idx]:
                    st.markdown(
                        f"""
                        <div style="background: #111821; border: 1px solid #263341; border-radius: 6px; padding: 0.75rem; margin-bottom: 0.5rem;">
                            <div style="font-size: 0.8rem; font-weight: 700; color: #45C6D9; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{row['algorithm']}</div>
                            <div style="font-size: 0.68rem; color: #A6B3C2; margin-top: 4px;">RUNTIME</div>
                            <div style="font-size: 1.2rem; font-weight: 700; font-family: monospace; color: #F3F6FA;">{row['execution_time_ms']:.2f} ms</div>
                            <div style="font-size: 0.68rem; color: #A6B3C2; margin-top: 4px;">EXPLORED</div>
                            <div style="font-size: 1.1rem; font-weight: 700; font-family: monospace; color: #7C8CFF;">{row['nodes_explored']:,}</div>
                            <div style="font-size: 0.68rem; color: #A6B3C2; margin-top: 4px;">DEPTH</div>
                            <div style="font-size: 1rem; font-weight: 700; font-family: monospace; color: #48D597;">{row['solution_length'] if pd.notna(row['solution_length']) else 'N/A'}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # Comparative Visual Charts
            f_time, f_nodes = plot_arena_charts(last_df)
            c_c1, c_c2 = st.columns(2)
            with c_c1:
                st.pyplot(f_time, use_container_width=True)
            with c_c2:
                st.pyplot(f_nodes, use_container_width=True)

            # Data Table
            st.markdown("##### Telemetry Data Table")
            display_tbl = last_df[["algorithm", "execution_time_ms", "nodes_explored", "max_frontier_size", "solution_length", "success"]].copy()
            display_tbl.columns = ["Algorithm", "Time (ms)", "Explored Nodes", "Peak Frontier", "Solution Length", "Success"]
            st.dataframe(display_tbl, use_container_width=True)

            # Scientific Interpretation
            if len(last_df) >= 2:
                fastest = last_df.loc[last_df["execution_time_ms"].idxmin()]
                min_nodes = last_df.loc[last_df["nodes_explored"].idxmin()]
                st.markdown(
                    f"""
                    <div style="background: #111821; border: 1px solid #263341; border-radius: 6px; padding: 0.75rem 1rem; font-size: 0.85rem; color: #A6B3C2; margin-top: 0.5rem;">
                        <strong>Empirical Observation:</strong><br>
                        • <strong>Lowest Latency:</strong> <code>{fastest['algorithm']}</code> ({fastest['execution_time_ms']:.2f} ms)<br>
                        • <strong>Least Explored Space:</strong> <code>{min_nodes['algorithm']}</code> ({min_nodes['nodes_explored']:,} states expanded)<br>
                        <em>Heuristic pruning and domain constraints directly govern state-space expansion rates.</em>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
