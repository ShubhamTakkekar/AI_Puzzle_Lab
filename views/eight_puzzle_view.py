"""8-Puzzle Lab: Interactive problem-solving simulator with step playback and dynamic explanations."""

import time
from typing import Optional, Tuple
import streamlit as st

from algorithms.astar import astar_search
from algorithms.bfs import breadth_first_search
from algorithms.dfs import depth_first_search
from algorithms.search_result import SearchResult
from puzzles.eight_puzzle import (
    DEFAULT_GOAL,
    PRESET_PUZZLES,
    EightPuzzle,
)
from ui.components import (
    render_algorithm_explanation,
    render_header,
    render_interactive_board,
    render_puzzle_html,
    render_search_metrics,
)


def init_eight_puzzle_state() -> None:
    """Initialize session state variables for 8-puzzle."""
    default_start = PRESET_PUZZLES["Easy (4 Moves)"]
    if "puzzle_initial_state" not in st.session_state:
        st.session_state["puzzle_initial_state"] = default_start
    if "puzzle_current_state" not in st.session_state:
        st.session_state["puzzle_current_state"] = default_start
    if "puzzle_solution_path" not in st.session_state:
        st.session_state["puzzle_solution_path"] = []
    if "puzzle_actions" not in st.session_state:
        st.session_state["puzzle_actions"] = []
    if "puzzle_step_idx" not in st.session_state:
        st.session_state["puzzle_step_idx"] = 0
    if "puzzle_is_playing" not in st.session_state:
        st.session_state["puzzle_is_playing"] = False
    if "puzzle_playback_speed" not in st.session_state:
        st.session_state["puzzle_playback_speed"] = 0.5
    if "puzzle_last_result" not in st.session_state:
        st.session_state["puzzle_last_result"] = None
    if "benchmark_history" not in st.session_state:
        st.session_state["benchmark_history"] = []


def on_manual_tile_move(new_state: Tuple[int, ...]) -> None:
    """Handle manual tile sliding in edit/play mode."""
    st.session_state["puzzle_current_state"] = new_state
    # Clear active solution path because board configuration has diverged
    st.session_state["puzzle_solution_path"] = []
    st.session_state["puzzle_actions"] = []
    st.session_state["puzzle_step_idx"] = 0
    st.session_state["puzzle_is_playing"] = False
    st.session_state["puzzle_last_result"] = None
    st.rerun()


def render_eight_puzzle_view() -> None:
    """Render the 8-Puzzle Lab interface with responsive interactive controls."""
    init_eight_puzzle_state()
    env = EightPuzzle()

    render_header(
        title="8-Puzzle Lab",
        subtitle="Explore state-space permutations, mathematical solvability, and step-by-step heuristic search",
        category="State-Space Search Simulator",
    )

    # Check auto-play execution loop
    solution_path = st.session_state["puzzle_solution_path"]
    step_idx = st.session_state["puzzle_step_idx"]
    is_playing = st.session_state["puzzle_is_playing"]

    if is_playing and solution_path:
        if step_idx < len(solution_path) - 1:
            time.sleep(st.session_state["puzzle_playback_speed"])
            st.session_state["puzzle_step_idx"] += 1
            st.rerun()
        else:
            st.session_state["puzzle_is_playing"] = False

    # Layout: Controls Column (Left) | Interactive Board & Playback (Right)
    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.markdown("#### ⚙️ Puzzle Setup & Algorithm Configuration")

        preset_choice = st.selectbox(
            "Select Initial Configuration Preset",
            options=list(PRESET_PUZZLES.keys()),
            index=3,  # Easy (4 Moves)
            help="Choose from pre-verified initial states with known optimal solution lengths.",
        )

        col_preset_btn, col_rnd_btn, col_reset_btn = st.columns(3)

        with col_preset_btn:
            if st.button("Load Preset", use_container_width=True):
                chosen = PRESET_PUZZLES[preset_choice]
                st.session_state["puzzle_initial_state"] = chosen
                st.session_state["puzzle_current_state"] = chosen
                st.session_state["puzzle_solution_path"] = []
                st.session_state["puzzle_actions"] = []
                st.session_state["puzzle_step_idx"] = 0
                st.session_state["puzzle_is_playing"] = False
                st.session_state["puzzle_last_result"] = None
                st.rerun()

        with col_rnd_btn:
            if st.button("Random Solvable", use_container_width=True, help="Generate a guaranteed solvable configuration"):
                shuffled = EightPuzzle.generate_random_solvable(steps_from_goal=16)
                st.session_state["puzzle_initial_state"] = shuffled
                st.session_state["puzzle_current_state"] = shuffled
                st.session_state["puzzle_solution_path"] = []
                st.session_state["puzzle_actions"] = []
                st.session_state["puzzle_step_idx"] = 0
                st.session_state["puzzle_is_playing"] = False
                st.session_state["puzzle_last_result"] = None
                st.rerun()

        with col_reset_btn:
            if st.button("Reset to Start", use_container_width=True):
                init_state = st.session_state["puzzle_initial_state"]
                st.session_state["puzzle_current_state"] = init_state
                st.session_state["puzzle_step_idx"] = 0
                st.session_state["puzzle_is_playing"] = False
                st.rerun()

        # Custom board string entry
        with st.expander("✏️ Custom State Editor", expanded=False):
            st.caption("Enter 9 space- or comma-separated numbers (0-8) where 0 denotes the empty slot:")
            curr_str = ", ".join(str(x) for x in st.session_state["puzzle_current_state"])
            custom_input = st.text_input("Board Permutation", value=curr_str, label_visibility="collapsed")
            if st.button("Apply Custom Configuration", use_container_width=True):
                parsed, err = EightPuzzle.parse_state_string(custom_input)
                if err:
                    st.error(err)
                else:
                    st.session_state["puzzle_initial_state"] = parsed
                    st.session_state["puzzle_current_state"] = parsed
                    st.session_state["puzzle_solution_path"] = []
                    st.session_state["puzzle_actions"] = []
                    st.session_state["puzzle_step_idx"] = 0
                    st.session_state["puzzle_is_playing"] = False
                    st.session_state["puzzle_last_result"] = None
                    st.rerun()

        st.markdown("#### 🔍 Search Algorithm")
        selected_algo = st.selectbox(
            "Algorithm Selection",
            options=[
                "A* Search (Manhattan Distance)",
                "Breadth-First Search (BFS)",
                "Depth-First Search (DFS) [Bounded]",
            ],
            help="A* uses Manhattan distance heuristic; BFS searches level-by-level; DFS explores along single branches with depth limit.",
        )

        dfs_depth_limit = 20
        if "DFS" in selected_algo:
            dfs_depth_limit = st.slider("DFS Maximum Depth Limit", min_value=5, max_value=35, value=20)

        # Mathematical Solvability Validation
        active_board = st.session_state["puzzle_current_state"]
        is_solvable = EightPuzzle.is_solvable(active_board)
        solvability_text = EightPuzzle.explain_solvability(active_board)

        if not is_solvable:
            st.markdown(
                f"""
                <div style="background: rgba(255, 107, 120, 0.08); border: 1px solid #FF6B78; border-radius: 6px; padding: 0.75rem; margin: 0.75rem 0; font-size: 0.85rem; color: #FFB3BA;">
                    <strong>Mathematical Invariant Rejection:</strong><br>{solvability_text}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Search Execution Action
        solve_disabled = not is_solvable or env.is_goal(active_board)
        if st.button(
            "⚡ Find Solution",
            type="primary",
            use_container_width=True,
            disabled=solve_disabled,
        ):
            with st.spinner(f"Computing solution with {selected_algo}..."):
                if "A*" in selected_algo:
                    result = astar_search(
                        initial_state=active_board,
                        get_neighbors_fn=env.get_neighbors,
                        is_goal_fn=env.is_goal,
                        heuristic_fn=env.manhattan_distance,
                        max_nodes=50000,
                        timeout_sec=10.0,
                    )
                elif "BFS" in selected_algo:
                    result = breadth_first_search(
                        initial_state=active_board,
                        get_neighbors_fn=env.get_neighbors,
                        is_goal_fn=env.is_goal,
                        max_nodes=50000,
                        timeout_sec=10.0,
                    )
                else:
                    result = depth_first_search(
                        initial_state=active_board,
                        get_neighbors_fn=env.get_neighbors,
                        is_goal_fn=env.is_goal,
                        max_depth=dfs_depth_limit,
                        max_nodes=50000,
                        timeout_sec=10.0,
                    )

                st.session_state["puzzle_last_result"] = result
                if result.success:
                    st.session_state["puzzle_solution_path"] = result.path
                    st.session_state["puzzle_actions"] = result.actions
                    st.session_state["puzzle_step_idx"] = 0
                    st.session_state["puzzle_is_playing"] = False

                    # Record in session telemetry
                    st.session_state["benchmark_history"].append({
                        "puzzle_type": "8-Puzzle",
                        "algorithm": result.algorithm_name,
                        "execution_time_ms": round(result.execution_time_sec * 1000, 3),
                        "nodes_explored": result.nodes_explored,
                        "max_frontier_size": result.max_frontier_size,
                        "solution_length": result.solution_length,
                        "success": True,
                    })
                st.rerun()

    with right_col:
        st.markdown("#### 🎯 Interactive 3×3 Board")

        # Determine state to display: if viewing solution path, display that step
        has_solution = bool(solution_path and len(solution_path) > 1)

        if has_solution:
            current_display_state = solution_path[st.session_state["puzzle_step_idx"]]
        else:
            current_display_state = st.session_state["puzzle_current_state"]

        # Render styled visual board
        render_puzzle_html(current_display_state)

        # Interactive manual tile slider (available when not currently in an active solution walkthrough)
        if not has_solution:
            st.caption("Manual Mode: Click any highlighted adjacent tile to slide it into the empty slot.")
            render_interactive_board(
                state=current_display_state,
                on_move_callback=on_manual_tile_move,
            )

        if env.is_goal(current_display_state):
            st.markdown(
                """
                <div style="text-align: center; margin: 0.4rem 0;">
                    <span class="status-tag success">✨ Solved: Board is in Goal State!</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # -------------------------------------------------------------
        # STEP-BY-STEP PLAYBACK CONTROLS
        # -------------------------------------------------------------
        if has_solution:
            total_moves = len(solution_path) - 1
            cur_step = st.session_state["puzzle_step_idx"]

            # Dynamic Move Explanation
            if cur_step == 0:
                step_desc = "Initial starting state."
            else:
                prev_st = solution_path[cur_step - 1]
                curr_st = solution_path[cur_step]
                step_desc = EightPuzzle.explain_transition(prev_st, curr_st)

            st.markdown(
                f"""
                <div style="background: #111821; border: 1px solid #263341; border-radius: 6px; padding: 0.6rem 0.85rem; margin-top: 0.5rem; font-size: 0.85rem;">
                    <span style="color: #45C6D9; font-weight: 700;">Step {cur_step} of {total_moves}:</span>
                    <span style="color: #F3F6FA; margin-left: 0.4rem;">{step_desc}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Playback Toolbar: First, Prev, Play/Pause, Next, Last, Goal
            c_first, c_prev, c_play, c_next, c_last, c_goal = st.columns(6)

            with c_first:
                if st.button("⏮ First", disabled=(cur_step == 0), use_container_width=True):
                    st.session_state["puzzle_step_idx"] = 0
                    st.session_state["puzzle_is_playing"] = False
                    st.rerun()

            with c_prev:
                if st.button("◀ Prev", disabled=(cur_step == 0), use_container_width=True):
                    st.session_state["puzzle_step_idx"] = max(0, cur_step - 1)
                    st.session_state["puzzle_is_playing"] = False
                    st.rerun()

            with c_play:
                if is_playing:
                    if st.button("⏸ Pause", use_container_width=True):
                        st.session_state["puzzle_is_playing"] = False
                        st.rerun()
                else:
                    if st.button("▶ Play", disabled=(cur_step == total_moves), use_container_width=True):
                        st.session_state["puzzle_is_playing"] = True
                        st.rerun()

            with c_next:
                if st.button("Next ▶", disabled=(cur_step == total_moves), use_container_width=True):
                    st.session_state["puzzle_step_idx"] = min(total_moves, cur_step + 1)
                    st.session_state["puzzle_is_playing"] = False
                    st.rerun()

            with c_last:
                if st.button("⏭ Last", disabled=(cur_step == total_moves), use_container_width=True):
                    st.session_state["puzzle_step_idx"] = total_moves
                    st.session_state["puzzle_is_playing"] = False
                    st.rerun()

            with c_goal:
                if st.button("Goal 🎯", disabled=(cur_step == total_moves), use_container_width=True, help="Jump directly to final state"):
                    st.session_state["puzzle_step_idx"] = total_moves
                    st.session_state["puzzle_is_playing"] = False
                    st.rerun()

            # Speed Selector and Scrubbing Slider
            col_speed, col_slider = st.columns([1, 3])
            with col_speed:
                speed_choice = st.selectbox(
                    "Speed",
                    options=[0.2, 0.4, 0.8, 1.2],
                    index=1,
                    format_func=lambda x: f"{x}s/step",
                    label_visibility="collapsed",
                )
                st.session_state["puzzle_playback_speed"] = speed_choice

            with col_slider:
                scrub_idx = st.slider(
                    "Scrubber",
                    min_value=0,
                    max_value=total_moves,
                    value=cur_step,
                    label_visibility="collapsed",
                )
                if scrub_idx != cur_step:
                    st.session_state["puzzle_step_idx"] = scrub_idx
                    st.session_state["puzzle_is_playing"] = False
                    st.rerun()

            # Exit Solution / Clear Solution button
            if st.button("✏️ Exit Solution & Edit Board", use_container_width=True):
                st.session_state["puzzle_solution_path"] = []
                st.session_state["puzzle_actions"] = []
                st.session_state["puzzle_step_idx"] = 0
                st.session_state["puzzle_is_playing"] = False
                st.rerun()

    # Telemetry Panel
    last_res: Optional[SearchResult] = st.session_state.get("puzzle_last_result")
    if last_res is not None:
        st.markdown("---")
        st.markdown("### 📊 Measured Performance Telemetry")
        render_search_metrics(last_res)

    # Collapsible Algorithm Insight Drawer
    st.markdown("---")
    render_algorithm_explanation(selected_algo)
