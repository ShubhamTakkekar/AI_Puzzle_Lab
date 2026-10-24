"""Reusable product-quality UI components for AI Puzzle Lab."""

from typing import Callable, Optional, Tuple
import streamlit as st

from algorithms.search_result import SearchResult
from puzzles.eight_puzzle import DEFAULT_GOAL


def render_header(title: str, subtitle: str, category: Optional[str] = None) -> None:
    """Render a compact developer-tool header banner."""
    cat_html = (
        f'<div class="tool-category">{category}</div>' if category else ""
    )
    st.markdown(
        f"""
        <div class="tool-header">
            <div class="tool-header-left">
                {cat_html}
                <h1 class="tool-title">{title}</h1>
                <p class="tool-subtitle">{subtitle}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_puzzle_html(
    state: Tuple[int, ...], goal_state: Tuple[int, ...] = DEFAULT_GOAL
) -> None:
    """Render a styled static HTML 3x3 puzzle board."""
    tiles_html = []
    for idx, val in enumerate(state):
        if val == 0:
            tiles_html.append('<div class="puzzle-tile-node puzzle-tile-blank"></div>')
        else:
            in_goal = " in-goal" if val == goal_state[idx] else ""
            tiles_html.append(f'<div class="puzzle-tile-node{in_goal}">{val}</div>')

    board_html = f"""
    <div class="puzzle-board-wrap">
        <div class="puzzle-grid-board">
            {''.join(tiles_html)}
        </div>
    </div>
    """
    st.markdown(board_html, unsafe_allow_html=True)


def render_interactive_board(
    state: Tuple[int, ...],
    on_move_callback: Callable[[Tuple[int, ...]], None],
    disabled: bool = False,
) -> None:
    """Render a 3x3 interactive button grid allowing the user to click any adjacent tile to slide it.

    Args:
        state: Current 9-tuple board state.
        on_move_callback: Function to call when a valid move is made with the new state.
        disabled: Whether user interaction is disabled.
    """
    blank_idx = state.index(0)
    blank_r, blank_c = blank_idx // 3, blank_idx % 3

    for r in range(3):
        cols = st.columns(3)
        for c in range(3):
            idx = r * 3 + c
            val = state[idx]
            is_blank = val == 0
            is_adjacent = (abs(r - blank_r) + abs(c - blank_c)) == 1

            with cols[c]:
                if is_blank:
                    st.button(
                        "·",
                        key=f"board_tile_{r}_{c}_{val}",
                        disabled=True,
                        use_container_width=True,
                    )
                else:
                    btn_label = f"**{val}**"
                    if st.button(
                        btn_label,
                        key=f"board_tile_{r}_{c}_{val}",
                        disabled=disabled or not is_adjacent,
                        use_container_width=True,
                        help="Slide tile into the empty slot" if is_adjacent else None,
                    ):
                        state_list = list(state)
                        state_list[blank_idx], state_list[idx] = (
                            state_list[idx],
                            state_list[blank_idx],
                        )
                        on_move_callback(tuple(state_list))


def render_search_metrics(result: SearchResult) -> None:
    """Display real measured performance telemetry in a compact scientific strip."""
    if not result.success:
        st.markdown(
            f"""
            <div style="margin: 0.5rem 0;">
                <span class="status-tag error">Search Terminated</span>
                <span style="color: #FF6B78; font-size: 0.85rem; margin-left: 0.5rem;">{result.error_message}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        time_ms = result.execution_time_sec * 1000
        st.markdown(
            f"""
            <div class="metric-strip">
                <div class="metric-cell">
                    <div class="metric-cell-label">Elapsed Time</div>
                    <div class="metric-cell-value cyan">{time_ms:.2f} ms</div>
                </div>
                <div class="metric-cell">
                    <div class="metric-cell-label">Nodes Explored</div>
                    <div class="metric-cell-value indigo">{result.nodes_explored:,}</div>
                </div>
                <div class="metric-cell">
                    <div class="metric-cell-label">Peak Frontier</div>
                    <div class="metric-cell-value">{result.max_frontier_size:,}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    time_ms = result.execution_time_sec * 1000
    moves = result.solution_length
    explored = result.nodes_explored
    peak_frontier = result.max_frontier_size
    eff = (explored / max(moves, 1)) if moves > 0 else 0.0

    st.markdown(
        f"""
        <div style="margin: 0.5rem 0;">
            <span class="status-tag success">Goal Reached</span>
            <span style="color: #A6B3C2; font-size: 0.82rem; margin-left: 0.5rem;">Verified shortest path via {result.algorithm_name}</span>
        </div>
        <div class="metric-strip">
            <div class="metric-cell">
                <div class="metric-cell-label">Execution Time</div>
                <div class="metric-cell-value cyan">{time_ms:.2f} ms</div>
            </div>
            <div class="metric-cell">
                <div class="metric-cell-label">Solution Depth</div>
                <div class="metric-cell-value green">{moves} moves</div>
            </div>
            <div class="metric-cell">
                <div class="metric-cell-label">Nodes Explored</div>
                <div class="metric-cell-value indigo">{explored:,}</div>
            </div>
            <div class="metric-cell">
                <div class="metric-cell-label">Peak Frontier</div>
                <div class="metric-cell-value">{peak_frontier:,}</div>
            </div>
            <div class="metric-cell">
                <div class="metric-cell-label">Nodes / Move</div>
                <div class="metric-cell-value amber">{eff:.1f}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_algorithm_explanation(algorithm_name: str) -> None:
    """Render concise, technically sound educational explanation."""
    with st.expander(f"📘 Algorithm Mechanics & Complexity: {algorithm_name}", expanded=False):
        if "Breadth-First" in algorithm_name or "BFS" in algorithm_name:
            st.markdown(
                """
                **Strategy:** Explores state space level-by-level using a FIFO queue.

                - **Optimality:** Optimal for unweighted graphs (guarantees minimum number of moves).
                - **Time Complexity:** $O(b^d)$ where $b$ is the effective branching factor and $d$ is solution depth.
                - **Space Complexity:** $O(b^d)$ — retains all generated states in memory, causing exponential frontier growth.
                - **Best Use Case:** Shallow target depths where shortest-path guarantee is critical and memory permits.
                """
            )
        elif "A*" in algorithm_name:
            st.markdown(
                """
                **Strategy:** Best-first search guided by an evaluation function $f(n) = g(n) + h(n)$.

                - **$g(n)$:** Path cost incurred from start state to node $n$.
                - **$h(n)$:** Admissible heuristic estimate from $n$ to goal (Manhattan distance: $\sum |\\Delta r| + |\\Delta c|$).
                - **Optimality:** Guaranteed optimal when $h(n)$ is admissible ($h(n) \\le h^*(n)$) and consistent ($h(n) \\le c(n, a, n') + h(n')$).
                - **Efficiency:** Prunes massive subtrees compared to blind BFS by focusing search along promising corridors.
                """
            )
        elif "Depth-First" in algorithm_name or "DFS" in algorithm_name:
            st.markdown(
                """
                **Strategy:** Explores as deeply as possible along each branch before backtracking, using a LIFO stack.

                - **Optimality:** Not optimal; can find deeply convoluted paths to shallow goals.
                - **Time Complexity:** $O(b^m)$ where $m$ is maximum search depth.
                - **Space Complexity:** $O(b \\cdot m)$ — linear memory footprint storing only the active path.
                - **Critical Requirement:** Depth bounding and cycle detection are required to prevent infinite loops in cyclic state spaces.
                """
            )
