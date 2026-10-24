"""Missionaries and Cannibals interactive river crossing laboratory."""

import time
from typing import List, Optional, Tuple
import streamlit as st

from algorithms.bfs import breadth_first_search
from algorithms.dfs import depth_first_search
from algorithms.search_result import SearchResult
from puzzles.missionaries_cannibals import (
    INITIAL_STATE,
    MissionariesCannibals,
)
from ui.components import render_header, render_search_metrics


def init_missionaries_state() -> None:
    """Initialize session state for Missionaries and Cannibals."""
    if "mc_total_m" not in st.session_state:
        st.session_state["mc_total_m"] = 3
    if "mc_total_c" not in st.session_state:
        st.session_state["mc_total_c"] = 3
    if "mc_boat_cap" not in st.session_state:
        st.session_state["mc_boat_cap"] = 2
    if "mc_current_state" not in st.session_state:
        st.session_state["mc_current_state"] = (3, 3, 0)
    if "mc_solution_path" not in st.session_state:
        st.session_state["mc_solution_path"] = []
    if "mc_actions" not in st.session_state:
        st.session_state["mc_actions"] = []
    if "mc_step_idx" not in st.session_state:
        st.session_state["mc_step_idx"] = 0
    if "mc_is_playing" not in st.session_state:
        st.session_state["mc_is_playing"] = False
    if "mc_playback_speed" not in st.session_state:
        st.session_state["mc_playback_speed"] = 0.6
    if "mc_last_result" not in st.session_state:
        st.session_state["mc_last_result"] = None
    if "mc_manual_warning" not in st.session_state:
        st.session_state["mc_manual_warning"] = None


def render_scene(state: Tuple[int, int, int], total_m: int, total_c: int, in_transit: Optional[Tuple[int, int]] = None) -> None:
    """Render a clean, responsive vector-style visual diagram of both riverbanks and river channel."""
    m_left, c_left, boat_pos = state
    m_right = total_m - m_left
    c_right = total_c - c_left

    boat_on_left = (boat_pos == 0)

    # Render character chips
    left_m_chips = "".join([f'<span style="background: rgba(124, 140, 255, 0.2); color: #7C8CFF; border: 1px solid #7C8CFF; border-radius: 4px; padding: 2px 6px; font-weight: 700; margin: 2px;">M</span>' for _ in range(m_left)]) or '<span style="color: #6C7D93; font-size: 0.8rem;">None</span>'
    left_c_chips = "".join([f'<span style="background: rgba(255, 107, 120, 0.2); color: #FF6B78; border: 1px solid #FF6B78; border-radius: 4px; padding: 2px 6px; font-weight: 700; margin: 2px;">C</span>' for _ in range(c_left)]) or '<span style="color: #6C7D93; font-size: 0.8rem;">None</span>'

    right_m_chips = "".join([f'<span style="background: rgba(124, 140, 255, 0.2); color: #7C8CFF; border: 1px solid #7C8CFF; border-radius: 4px; padding: 2px 6px; font-weight: 700; margin: 2px;">M</span>' for _ in range(m_right)]) or '<span style="color: #6C7D93; font-size: 0.8rem;">None</span>'
    right_c_chips = "".join([f'<span style="background: rgba(255, 107, 120, 0.2); color: #FF6B78; border: 1px solid #FF6B78; border-radius: 4px; padding: 2px 6px; font-weight: 700; margin: 2px;">C</span>' for _ in range(c_right)]) or '<span style="color: #6C7D93; font-size: 0.8rem;">None</span>'

    # Transit chips
    transit_info = ""
    if in_transit and (in_transit[0] > 0 or in_transit[1] > 0):
        transit_info = f'<div style="font-size: 0.72rem; color: #45C6D9; margin-top: 4px;">Carrying {in_transit[0]}M, {in_transit[1]}C</div>'

    st.markdown(
        f"""
        <div style="background: #080C10; border: 1px solid #263341; border-radius: 8px; padding: 1.2rem; margin: 0.75rem 0;">
            <div style="display: grid; grid-template-columns: 1fr 180px 1fr; gap: 0.75rem; align-items: stretch; text-align: center;">
                <!-- Left Bank -->
                <div style="background: #111821; border: 1px solid #263341; border-radius: 6px; padding: 0.85rem;">
                    <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: #7C8CFF; letter-spacing: 0.05em; margin-bottom: 0.5rem;">Left Riverbank</div>
                    <div style="margin-bottom: 0.4rem;">
                        <span style="font-size: 0.85rem; color: #A6B3C2;">Missionaries ({m_left}):</span><br>
                        <div style="margin-top: 3px;">{left_m_chips}</div>
                    </div>
                    <div>
                        <span style="font-size: 0.85rem; color: #A6B3C2;">Cannibals ({c_left}):</span><br>
                        <div style="margin-top: 3px;">{left_c_chips}</div>
                    </div>
                </div>

                <!-- River Waterway & Boat -->
                <div style="background: linear-gradient(180deg, #09131F 0%, #060E18 100%); border: 1px solid #18334E; border-radius: 6px; padding: 0.75rem; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                    <div style="font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #45C6D9; margin-bottom: 0.6rem;">River Channel</div>
                    <div style="background: {'#172B44' if boat_on_left else 'transparent'}; border: 1px {'solid #45C6D9' if boat_on_left else 'dashed #18334E'}; border-radius: 6px; padding: 6px 12px; width: 100%; margin-bottom: 8px;">
                        <span style="color: {'#45C6D9' if boat_on_left else '#3D4F63'}; font-size: 0.8rem; font-weight: 700;">⛵ Left Dock {'(Docked)' if boat_on_left else ''}</span>
                        {transit_info if boat_on_left else ''}
                    </div>
                    <div style="background: {'#172B44' if not boat_on_left else 'transparent'}; border: 1px {'solid #45C6D9' if not boat_on_left else 'dashed #18334E'}; border-radius: 6px; padding: 6px 12px; width: 100%;">
                        <span style="color: {'#45C6D9' if not boat_on_left else '#3D4F63'}; font-size: 0.8rem; font-weight: 700;">⛵ Right Dock {'(Docked)' if not boat_on_left else ''}</span>
                        {transit_info if not boat_on_left else ''}
                    </div>
                </div>

                <!-- Right Bank -->
                <div style="background: #111821; border: 1px solid #263341; border-radius: 6px; padding: 0.85rem;">
                    <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: #48D597; letter-spacing: 0.05em; margin-bottom: 0.5rem;">Right Bank (Goal)</div>
                    <div style="margin-bottom: 0.4rem;">
                        <span style="font-size: 0.85rem; color: #A6B3C2;">Missionaries ({m_right}):</span><br>
                        <div style="margin-top: 3px;">{right_m_chips}</div>
                    </div>
                    <div>
                        <span style="font-size: 0.85rem; color: #A6B3C2;">Cannibals ({c_right}):</span><br>
                        <div style="margin-top: 3px;">{right_c_chips}</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_missionaries_view() -> None:
    """Render the complete Missionaries and Cannibals interactive laboratory."""
    init_missionaries_state()

    total_m = st.session_state["mc_total_m"]
    total_c = st.session_state["mc_total_c"]
    boat_cap = st.session_state["mc_boat_cap"]

    env = MissionariesCannibals(total_m=total_m, total_c=total_c, boat_cap=boat_cap)

    render_header(
        title="Missionaries & Cannibals",
        subtitle="Graph exploration under safety invariants: missionaries must never be outnumbered",
        category="Constraint-Enforced Search",
    )

    # Playback animation loop
    sol_path = st.session_state["mc_solution_path"]
    step_idx = st.session_state["mc_step_idx"]
    is_playing = st.session_state["mc_is_playing"]

    if is_playing and sol_path:
        if step_idx < len(sol_path) - 1:
            time.sleep(st.session_state["mc_playback_speed"])
            st.session_state["mc_step_idx"] += 1
            st.rerun()
        else:
            st.session_state["mc_is_playing"] = False

    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.markdown("#### ⚙️ Problem Configuration & Search")

        with st.expander("🔧 Problem Parameters", expanded=False):
            c_m, c_c, c_b = st.columns(3)
            with c_m:
                new_m = st.number_input("Total Missionaries", min_value=1, max_value=5, value=total_m)
            with c_c:
                new_c = st.number_input("Total Cannibals", min_value=1, max_value=5, value=total_c)
            with c_b:
                new_cap = st.number_input("Boat Capacity", min_value=2, max_value=4, value=boat_cap)

            if st.button("Apply Parameters & Reset", use_container_width=True):
                st.session_state["mc_total_m"] = new_m
                st.session_state["mc_total_c"] = new_c
                st.session_state["mc_boat_cap"] = new_cap
                st.session_state["mc_current_state"] = (new_m, new_c, 0)
                st.session_state["mc_solution_path"] = []
                st.session_state["mc_actions"] = []
                st.session_state["mc_step_idx"] = 0
                st.session_state["mc_is_playing"] = False
                st.session_state["mc_last_result"] = None
                st.rerun()

        algo_choice = st.selectbox(
            "Search Algorithm",
            options=[
                "Breadth-First Search (BFS) [Optimal Path]",
                "Depth-First Search (DFS) [Depth-Bounded]",
            ],
            help="BFS guarantees shortest 11-step solution. DFS explores deeply.",
        )

        dfs_depth_limit = 30
        if "DFS" in algo_choice:
            dfs_depth_limit = st.slider("DFS Maximum Depth Limit", min_value=11, max_value=45, value=25)

        col_solve, col_reset = st.columns([2, 1])

        with col_solve:
            if st.button("⚡ Find Crossing Sequence", type="primary", use_container_width=True):
                with st.spinner("Searching safe state-space transitions..."):
                    init_st = (total_m, total_c, 0)
                    if "BFS" in algo_choice:
                        result = breadth_first_search(
                            initial_state=init_st,
                            get_neighbors_fn=env.get_neighbors,
                            is_goal_fn=env.is_goal,
                        )
                    else:
                        result = depth_first_search(
                            initial_state=init_st,
                            get_neighbors_fn=env.get_neighbors,
                            is_goal_fn=env.is_goal,
                            max_depth=dfs_depth_limit,
                        )

                    st.session_state["mc_last_result"] = result
                    if result.success:
                        st.session_state["mc_solution_path"] = result.path
                        st.session_state["mc_actions"] = result.actions
                        st.session_state["mc_step_idx"] = 0
                        st.session_state["mc_is_playing"] = False

                        st.session_state["benchmark_history"].append({
                            "puzzle_type": "Missionaries & Cannibals",
                            "algorithm": result.algorithm_name,
                            "execution_time_ms": round(result.execution_time_sec * 1000, 3),
                            "nodes_explored": result.nodes_explored,
                            "max_frontier_size": result.max_frontier_size,
                            "solution_length": result.solution_length,
                            "success": True,
                        })
                    st.rerun()

        with col_reset:
            if st.button("Reset State", use_container_width=True):
                st.session_state["mc_current_state"] = (total_m, total_c, 0)
                st.session_state["mc_solution_path"] = []
                st.session_state["mc_actions"] = []
                st.session_state["mc_step_idx"] = 0
                st.session_state["mc_is_playing"] = False
                st.session_state["mc_last_result"] = None
                st.session_state["mc_manual_warning"] = None
                st.rerun()

        # -------------------------------------------------------------
        # MANUAL CROSSING CONTROLS
        # -------------------------------------------------------------
        st.markdown("#### ⛵ Manual River Crossing")
        cur_st = st.session_state["mc_current_state"]
        m_l, c_l, b_pos = cur_st
        dep_m = m_l if b_pos == 0 else (total_m - m_l)
        dep_c = c_l if b_pos == 0 else (total_c - c_l)

        dep_bank = "Left Bank" if b_pos == 0 else "Right Bank"
        st.caption(f"Boat is currently at **{dep_bank}**. Select passengers to load:")

        col_pass_m, col_pass_c, col_pass_go = st.columns([1, 1, 1])
        with col_pass_m:
            load_m = st.number_input("Missionaries", min_value=0, max_value=min(dep_m, boat_cap), value=0)
        with col_pass_c:
            load_c = st.number_input("Cannibals", min_value=0, max_value=min(dep_c, boat_cap), value=0)

        with col_pass_go:
            st.write("")
            st.write("")
            if st.button("Cross ⛵", use_container_width=True):
                passengers = load_m + load_c
                if passengers < 1:
                    st.session_state["mc_manual_warning"] = "The boat cannot cross empty! Load at least 1 person."
                    st.rerun()
                elif passengers > boat_cap:
                    st.session_state["mc_manual_warning"] = f"Boat capacity exceeded! Maximum {boat_cap} persons allowed."
                    st.rerun()
                else:
                    new_m_l = (m_l - load_m) if b_pos == 0 else (m_l + load_m)
                    new_c_l = (c_l - load_c) if b_pos == 0 else (c_l + load_c)
                    new_b = 1 if b_pos == 0 else 0

                    if not env.is_safe(new_m_l, new_c_l, total_m, total_c):
                        st.session_state["mc_manual_warning"] = MissionariesCannibals.explain_state_safety(new_m_l, new_c_l, total_m, total_c)
                    else:
                        st.session_state["mc_manual_warning"] = None
                        st.session_state["mc_current_state"] = (new_m_l, new_c_l, new_b)
                        st.session_state["mc_solution_path"] = []
                        st.session_state["mc_actions"] = []
                        st.session_state["mc_step_idx"] = 0
                    st.rerun()

        if st.session_state["mc_manual_warning"]:
            st.markdown(
                f"""
                <div style="background: rgba(255, 107, 120, 0.08); border: 1px solid #FF6B78; border-radius: 6px; padding: 0.65rem 0.85rem; font-size: 0.83rem; color: #FFB3BA; margin-top: 0.5rem;">
                    <strong>Illegal Crossing:</strong> {st.session_state['mc_manual_warning']}
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right_col:
        st.markdown("#### 🌊 Interactive River Scene")

        has_sol = bool(sol_path and len(sol_path) > 1)
        if has_sol:
            active_st = sol_path[step_idx]
            in_transit_load = None
            if step_idx > 0:
                p_st = sol_path[step_idx - 1]
                in_transit_load = (abs(p_st[0] - active_st[0]), abs(p_st[1] - active_st[1]))
        else:
            active_st = st.session_state["mc_current_state"]
            in_transit_load = None

        # Render vector-style river diagram
        render_scene(active_st, total_m, total_c, in_transit_load)

        if env.is_goal(active_st):
            st.markdown(
                """
                <div style="text-align: center; margin: 0.4rem 0;">
                    <span class="status-tag success">✨ Success: All Missionaries & Cannibals Safely Crossed!</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # -------------------------------------------------------------
        # STEP-BY-STEP PLAYBACK CONTROLS
        # -------------------------------------------------------------
        if has_sol:
            total_crossings = len(sol_path) - 1
            cur_s = st.session_state["mc_step_idx"]

            # Dynamic Action Narrative
            if cur_s == 0:
                crossing_desc = "Initial state on left bank."
            else:
                p_st = sol_path[cur_s - 1]
                crossing_desc = env.explain_crossing(p_st, active_st)

            st.markdown(
                f"""
                <div style="background: #111821; border: 1px solid #263341; border-radius: 6px; padding: 0.6rem 0.85rem; margin-top: 0.5rem; font-size: 0.85rem;">
                    <span style="color: #45C6D9; font-weight: 700;">Crossing {cur_s} of {total_crossings}:</span>
                    <span style="color: #F3F6FA; margin-left: 0.4rem;">{crossing_desc}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            c_f, c_p, c_pl, c_n, c_l, c_g = st.columns(6)

            with c_f:
                if st.button("⏮ Start", key="mc_f", disabled=(cur_s == 0), use_container_width=True):
                    st.session_state["mc_step_idx"] = 0
                    st.session_state["mc_is_playing"] = False
                    st.rerun()

            with c_p:
                if st.button("◀ Prev", key="mc_p", disabled=(cur_s == 0), use_container_width=True):
                    st.session_state["mc_step_idx"] = max(0, cur_s - 1)
                    st.session_state["mc_is_playing"] = False
                    st.rerun()

            with c_pl:
                if is_playing:
                    if st.button("⏸ Pause", key="mc_pause", use_container_width=True):
                        st.session_state["mc_is_playing"] = False
                        st.rerun()
                else:
                    if st.button("▶ Play", key="mc_play", disabled=(cur_s == total_crossings), use_container_width=True):
                        st.session_state["mc_is_playing"] = True
                        st.rerun()

            with c_n:
                if st.button("Next ▶", key="mc_n", disabled=(cur_s == total_crossings), use_container_width=True):
                    st.session_state["mc_step_idx"] = min(total_crossings, cur_s + 1)
                    st.session_state["mc_is_playing"] = False
                    st.rerun()

            with c_l:
                if st.button("⏭ End", key="mc_l", disabled=(cur_s == total_crossings), use_container_width=True):
                    st.session_state["mc_step_idx"] = total_crossings
                    st.session_state["mc_is_playing"] = False
                    st.rerun()

            with c_g:
                if st.button("Goal 🎯", key="mc_g", disabled=(cur_s == total_crossings), use_container_width=True):
                    st.session_state["mc_step_idx"] = total_crossings
                    st.session_state["mc_is_playing"] = False
                    st.rerun()

            # Speed Selector and Scrubbing Slider
            c_sp, c_sl = st.columns([1, 3])
            with c_sp:
                sp_choice = st.selectbox(
                    "Speed",
                    options=[0.3, 0.6, 1.0, 1.5],
                    index=1,
                    format_func=lambda x: f"{x}s/step",
                    label_visibility="collapsed",
                    key="mc_speed_select",
                )
                st.session_state["mc_playback_speed"] = sp_choice

            with c_sl:
                scrub_c = st.slider(
                    "Crossing Scrubber",
                    min_value=0,
                    max_value=total_crossings,
                    value=cur_s,
                    label_visibility="collapsed",
                    key="mc_slider",
                )
                if scrub_c != cur_s:
                    st.session_state["mc_step_idx"] = scrub_c
                    st.session_state["mc_is_playing"] = False
                    st.rerun()

            if st.button("✏️ Exit Solution & Manual Mode", use_container_width=True):
                st.session_state["mc_solution_path"] = []
                st.session_state["mc_actions"] = []
                st.session_state["mc_step_idx"] = 0
                st.session_state["mc_is_playing"] = False
                st.rerun()

    # Search Telemetry
    last_res: Optional[SearchResult] = st.session_state.get("mc_last_result")
    if last_res is not None:
        st.markdown("---")
        st.markdown("### 📊 Measured Search Telemetry")
        render_search_metrics(last_res)

    # Invariant Inspector & State Space Theory
    st.markdown("---")
    with st.expander("📘 Formal Safety Invariant Analysis & Graph Complexity", expanded=False):
        st.markdown(
            f"""
            - **Unconstrained State Space:** $(M + 1) \\times (C + 1) \\times 2 = 4 \\times 4 \\times 2 = 32$ configurations.
            - **Safety Invariant:**
              $$(M_{{left}} = 0 \\lor M_{{left}} \\ge C_{{left}}) \\land ((M_{{total}} - M_{{left}}) = 0 \\lor (M_{{total}} - M_{{left}}) \\ge (C_{{total}} - C_{{left}}))$$
            - **Legal Subgraph:** Prunes state space to only **16 valid nodes** for the classic 3M/3C problem.
            - **Cycle Detection:** Because crossing moves can immediately reverse (e.g. crossing right and immediately crossing left),
              graph-search visited tracking is mandatory to guarantee termination and discover the optimal **11-crossing solution**.
            """
        )
