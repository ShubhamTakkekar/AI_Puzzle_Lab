"""Home Dashboard: Executive entry point, puzzle launcher, and algorithmic learning hub."""

from typing import Dict, List
import streamlit as st


def render_home_view() -> None:
    """Render the executive Home Dashboard with product-grade Midnight Graphite UI."""
    # A. COMPACT HERO SECTION
    st.markdown(
        """
        <div style="padding: 0.5rem 0 1.25rem 0; border-bottom: 1px solid #263341; margin-bottom: 1.25rem;">
            <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: #45C6D9; letter-spacing: 0.08em; margin-bottom: 0.2rem;">
                Scientific Problem-Solving Environment
            </div>
            <h1 style="font-size: 2.1rem; font-weight: 800; color: #F3F6FA; margin: 0; letter-spacing: -0.02em;">
                AI PUZZLE <span style="color: #7C8CFF;">LAB</span>
            </h1>
            <p style="font-size: 1rem; color: #A6B3C2; margin-top: 0.35rem; max-width: 800px; line-height: 1.5;">
                Explore intelligent search, constraint solving, and algorithm performance through interactive puzzles.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c_btn1, c_btn2, _ = st.columns([1.2, 1.4, 4])
    with c_btn1:
        if st.button("🧩 Explore Puzzles", type="primary", use_container_width=True):
            st.session_state["current_page"] = "8-Puzzle Lab"
            st.rerun()

    with c_btn2:
        if st.button("⚔️ Compare Algorithms", use_container_width=True):
            st.session_state["current_page"] = "Algorithm Arena"
            st.rerun()

    # D. RECENT ACTIVITY OR SESSION SUMMARY
    history: List[Dict] = st.session_state.get("benchmark_history", [])
    if history:
        total_runs = len(history)
        total_nodes = sum(r.get("nodes_explored", 0) for r in history)
        avg_ms = sum(r.get("execution_time_ms", 0.0) for r in history) / max(total_runs, 1)
        last_run = history[-1]

        st.markdown(
            f"""
            <div style="background: #111821; border: 1px solid #263341; border-radius: 8px; padding: 0.75rem 1rem; margin: 1.25rem 0 1.5rem 0;">
                <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: #7C8CFF; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                    Active Session Activity Telemetry
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.75rem;">
                    <div>
                        <div style="font-size: 0.68rem; color: #6C7D93; text-transform: uppercase;">Total Runs</div>
                        <div style="font-size: 1.25rem; font-weight: 700; color: #F3F6FA; font-family: monospace;">{total_runs}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.68rem; color: #6C7D93; text-transform: uppercase;">States Explored</div>
                        <div style="font-size: 1.25rem; font-weight: 700; color: #45C6D9; font-family: monospace;">{total_nodes:,}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.68rem; color: #6C7D93; text-transform: uppercase;">Avg Latency</div>
                        <div style="font-size: 1.25rem; font-weight: 700; color: #48D597; font-family: monospace;">{avg_ms:.2f} ms</div>
                    </div>
                    <div>
                        <div style="font-size: 0.68rem; color: #6C7D93; text-transform: uppercase;">Last Puzzle Solved</div>
                        <div style="font-size: 0.95rem; font-weight: 600; color: #F4B860; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                            {last_run.get('puzzle_type', 'N/A')} ({last_run.get('algorithm', '')})
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # B. INTERACTIVE PUZZLE LAUNCHER
    st.markdown("### 🚀 Interactive Puzzle Environments")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div style="background: #111821; border: 1px solid #263341; border-radius: 8px; padding: 1rem; margin-bottom: 0.6rem; min-height: 175px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                    <span style="font-size: 1.1rem; font-weight: 700; color: #F3F6FA;">8-Puzzle Lab</span>
                    <span style="font-size: 1.2rem;">🧩</span>
                </div>
                <div style="font-size: 0.72rem; color: #7C8CFF; font-weight: 600; text-transform: uppercase; margin-bottom: 0.4rem;">
                    Search Families: BFS · A* (Manhattan) · DFS
                </div>
                <p style="font-size: 0.85rem; color: #A6B3C2; margin: 0; line-height: 1.45;">
                    Permutation sliding-tile search. Test mathematical inversion parity, manual tile moves, and step-by-step playback.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch 8-Puzzle Lab", key="home_nav_8puzzle", use_container_width=True, type="primary"):
            st.session_state["current_page"] = "8-Puzzle Lab"
            st.rerun()

    with col2:
        st.markdown(
            """
            <div style="background: #111821; border: 1px solid #263341; border-radius: 8px; padding: 1rem; margin-bottom: 0.6rem; min-height: 175px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                    <span style="font-size: 1.1rem; font-weight: 700; color: #F3F6FA;">River Crossing</span>
                    <span style="font-size: 1.2rem;">🌊</span>
                </div>
                <div style="font-size: 0.72rem; color: #45C6D9; font-weight: 600; text-transform: uppercase; margin-bottom: 0.4rem;">
                    Search Families: BFS (11 Crossings) · DFS
                </div>
                <p style="font-size: 0.85rem; color: #A6B3C2; margin: 0; line-height: 1.45;">
                    The classic Missionaries & Cannibals riddle. Enforce safety invariants to prevent outnumbered missionaries.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch River Crossing", key="home_nav_mc", use_container_width=True):
            st.session_state["current_page"] = "Missionaries & Cannibals"
            st.rerun()

    with col3:
        st.markdown(
            """
            <div style="background: #111821; border: 1px solid #263341; border-radius: 8px; padding: 1rem; margin-bottom: 0.6rem; min-height: 175px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                    <span style="font-size: 1.1rem; font-weight: 700; color: #F3F6FA;">Sudoku Lab</span>
                    <span style="font-size: 1.2rem;">🔢</span>
                </div>
                <div style="font-size: 0.72rem; color: #48D597; font-weight: 600; text-transform: uppercase; margin-bottom: 0.4rem;">
                    Search Families: CSP Backtracking · MRV
                </div>
                <p style="font-size: 0.85rem; color: #A6B3C2; margin: 0; line-height: 1.45;">
                    Constraint satisfaction on 9x9 grids with editable cells, conflict detection, and decision-level trace playback.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch Sudoku Lab", key="home_nav_sudoku", use_container_width=True):
            st.session_state["current_page"] = "Sudoku Lab"
            st.rerun()

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown(
            """
            <div style="background: #111821; border: 1px solid #263341; border-radius: 8px; padding: 1rem; margin-bottom: 0.6rem; min-height: 175px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                    <span style="font-size: 1.1rem; font-weight: 700; color: #F3F6FA;">Algorithm Arena</span>
                    <span style="font-size: 1.2rem;">⚔️</span>
                </div>
                <div style="font-size: 0.72rem; color: #F4B860; font-weight: 600; text-transform: uppercase; margin-bottom: 0.4rem;">
                    Empirical Benchmarking Console
                </div>
                <p style="font-size: 0.85rem; color: #A6B3C2; margin: 0; line-height: 1.45;">
                    Synchronous head-to-head testing on identical seeds with execution-time and explored-states comparison.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch Arena", key="home_nav_arena", use_container_width=True):
            st.session_state["current_page"] = "Algorithm Arena"
            st.rerun()

    with col5:
        st.markdown(
            """
            <div style="background: #111821; border: 1px solid #263341; border-radius: 8px; padding: 1rem; margin-bottom: 0.6rem; min-height: 175px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                    <span style="font-size: 1.1rem; font-weight: 700; color: #F3F6FA;">Data Analytics</span>
                    <span style="font-size: 1.2rem;">📈</span>
                </div>
                <div style="font-size: 0.72rem; color: #45C6D9; font-weight: 600; text-transform: uppercase; margin-bottom: 0.4rem;">
                    Pandas Aggregation & Matplotlib
                </div>
                <p style="font-size: 0.85rem; color: #A6B3C2; margin: 0; line-height: 1.45;">
                    Statistical performance distributions, complexity scatter plots, and one-click CSV export of session telemetry.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("View Analytics", key="home_nav_analytics", use_container_width=True):
            st.session_state["current_page"] = "Data Analytics"
            st.rerun()

    with col6:
        st.markdown(
            """
            <div style="background: #111821; border: 1px solid #263341; border-radius: 8px; padding: 1rem; margin-bottom: 0.6rem; min-height: 175px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                    <span style="font-size: 1.1rem; font-weight: 700; color: #F3F6FA;">Difficulty Predictor</span>
                    <span style="font-size: 1.2rem;">🤖</span>
                </div>
                <div style="font-size: 0.72rem; color: #7C8CFF; font-weight: 600; text-transform: uppercase; margin-bottom: 0.4rem;">
                    Scikit-Learn Random Forest
                </div>
                <p style="font-size: 0.85rem; color: #A6B3C2; margin: 0; line-height: 1.45;">
                    Predict state-space difficulty from mathematical geometric features with zero target leakage.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open ML Predictor", key="home_nav_predictor", use_container_width=True):
            st.session_state["current_page"] = "Puzzle Difficulty Predictor"
            st.rerun()

    # C. LEARNING OVERVIEW
    st.markdown("---")
    st.markdown("### 📚 Algorithmic Theory & Paradigms Implemented")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Uninformed Search",
        "Heuristic (Informed) Search",
        "Constraint Satisfaction (CSP)",
        "Empirical Complexity & Telemetry",
    ])

    with tab1:
        st.markdown(
            """
            **Uninformed Search** operates with zero domain knowledge about the distance to the goal.
            - **Breadth-First Search (BFS):** FIFO queue frontier. Systematically explores depth $d$ before $d + 1$. Guaranteed to find the optimal shortest path in unweighted graphs. Space complexity is $O(b^d)$, which causes memory exhaustion on deep puzzles.
            - **Depth-First Search (DFS):** LIFO stack frontier. Linear memory requirement $O(b \\cdot m)$. Not optimal, and vulnerable to runaway paths unless restricted by explicit depth limits and visited-state tracking.
            """
        )

    with tab2:
        st.markdown(
            """
            **Informed (Heuristic) Search** evaluates candidates using an estimation function $f(n) = g(n) + h(n)$.
            - **A* Search:** Expands the node minimizing $f(n)$.
            - **Admissibility:** $h(n) \\le h^*(n)$ (never overestimates). Admissibility guarantees optimality.
            - **Manhattan Distance:** Sum of horizontal and vertical steps each tile must take to reach its goal position. Admissible and consistent.
            - **Linear Conflicts:** Additional cost incurred when two tiles are in their goal line but in reversed relative order.
            """
        )

    with tab3:
        st.markdown(
            """
            **Constraint Satisfaction Problems (CSP)** represent state spaces as variables subject to explicit rules.
            - **Backtracking:** Depth-first assignment of values with incremental constraint validation.
            - **Minimum Remaining Values (MRV):** "Fail-first" heuristic picking variables with the fewest legal values to trigger dead-ends at the top of the search tree.
            """
        )

    with tab4:
        st.markdown(
            """
            **Empirical Measurement vs. Asymptotic Bounds:**
            - Big-O analysis ($O(b^d)$) provides theoretical worst-case scaling.
            - Real-world performance is governed by hardware instruction pipelining, cache locality, and branching factors.
            - The **Algorithm Arena** and **Data Analytics** modules measure wall-clock latency with Python's high-resolution `time.perf_counter()` on your exact CPU.
            """
        )
