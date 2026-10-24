"""Sudoku Lab: Interactive 9x9 editable board and step-by-step constraint backtracking."""

import copy
import time
from typing import Dict, List, Optional, Set, Tuple
import streamlit as st

from puzzles.sudoku import SUDOKU_PRESETS, Grid, Sudoku, SudokuSolution, SudokuTraceStep
from ui.components import render_header


def init_sudoku_state() -> None:
    """Initialize session state for Sudoku Lab."""
    default_grid = copy.deepcopy(SUDOKU_PRESETS["Easy (35 Clues)"])
    if "sudoku_grid" not in st.session_state:
        st.session_state["sudoku_grid"] = copy.deepcopy(default_grid)
    if "sudoku_original_clues" not in st.session_state:
        st.session_state["sudoku_original_clues"] = copy.deepcopy(default_grid)
    if "sudoku_selected_cell" not in st.session_state:
        st.session_state["sudoku_selected_cell"] = (0, 0)
    if "sudoku_solution" not in st.session_state:
        st.session_state["sudoku_solution"] = None
    if "sudoku_trace_idx" not in st.session_state:
        st.session_state["sudoku_trace_idx"] = 0
    if "sudoku_is_playing" not in st.session_state:
        st.session_state["sudoku_is_playing"] = False
    if "sudoku_speed" not in st.session_state:
        st.session_state["sudoku_speed"] = 0.3
    if "sudoku_view_mode" not in st.session_state:
        st.session_state["sudoku_view_mode"] = "edit"  # "edit", "step_solve", "solved"


def render_sudoku_table(
    grid: Grid,
    clues_grid: Grid,
    selected_cell: Tuple[int, int],
    conflicts: Set[Tuple[int, int]],
    focused_cell: Optional[Tuple[int, int]] = None,
) -> None:
    """Render a styled 9x9 Sudoku board with subgrid boundaries and cell highlights."""
    sel_r, sel_c = selected_cell
    sel_val = grid[sel_r][sel_c] if (0 <= sel_r < 9 and 0 <= sel_c < 9) else 0

    html_rows = []
    for r in range(9):
        html_cells = []
        for c in range(9):
            val = grid[r][c]
            is_clue = clues_grid[r][c] != 0
            is_conflict = (r, c) in conflicts
            is_selected = (r == sel_r and c == sel_c)
            is_peer = (r == sel_r or c == sel_c)
            is_match = (val != 0 and val == sel_val and not is_selected)
            is_focused = (focused_cell is not None and focused_cell == (r, c))

            # CSS borders for 3x3 block separation
            border_top = "border-top: 2px solid #7C8CFF !important;" if (r % 3 == 0 and r != 0) else "border-top: 1px solid #263341;"
            border_bottom = "border-bottom: 2px solid #7C8CFF !important;" if (r == 8) else ""
            border_left = "border-left: 2px solid #7C8CFF !important;" if (c % 3 == 0 and c != 0) else "border-left: 1px solid #263341;"
            border_right = "border-right: 2px solid #7C8CFF !important;" if (c == 8) else ""

            # Base background and text color
            if is_conflict:
                bg = "rgba(255, 107, 120, 0.25)"
                text_color = "#FF6B78"
                border_focus = "border: 2px solid #FF6B78 !important;"
            elif is_focused:
                bg = "rgba(69, 198, 217, 0.35)"
                text_color = "#FFFFFF"
                border_focus = "border: 2px solid #45C6D9 !important;"
            elif is_selected:
                bg = "#1D2D44"
                text_color = "#FFFFFF"
                border_focus = "border: 2px solid #7C8CFF !important;"
            elif is_match:
                bg = "rgba(69, 198, 217, 0.15)"
                text_color = "#45C6D9"
                border_focus = ""
            elif is_peer:
                bg = "#131C27"
                text_color = "#F3F6FA" if is_clue else "#45C6D9"
                border_focus = ""
            else:
                bg = "#0E151F" if is_clue else "#080C10"
                text_color = "#F3F6FA" if is_clue else "#45C6D9"
                border_focus = ""

            font_weight = "800" if is_clue else "600"
            display_val = str(val) if val != 0 else ""

            cell_style = (
                f"background: {bg}; color: {text_color}; font-weight: {font_weight}; "
                f"{border_top} {border_bottom} {border_left} {border_right} {border_focus}"
            )

            html_cells.append(f'<td class="sdk-cell" style="{cell_style}">{display_val}</td>')
        html_rows.append(f"<tr>{''.join(html_cells)}</tr>")

    table_html = f"""
    <style>
    .sdk-wrap {{
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0.5rem 0;
    }}
    .sdk-table {{
        border-collapse: collapse;
        border: 2px solid #7C8CFF;
        background: #080C10;
        border-radius: 6px;
        overflow: hidden;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.5);
    }}
    .sdk-cell {{
        width: 38px;
        height: 38px;
        text-align: center;
        vertical-align: middle;
        font-family: "JetBrains Mono", monospace;
        font-size: 1.15rem;
        user-select: none;
    }}
    </style>
    <div class="sdk-wrap">
        <table class="sdk-table">
            {''.join(html_rows)}
        </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)


def render_sudoku_view() -> None:
    """Render the complete Sudoku interactive CSP laboratory."""
    init_sudoku_state()

    render_header(
        title="Sudoku Lab",
        subtitle="Constraint Satisfaction Problem (CSP) with editable grid and step-by-step backtracking",
        category="Constraint Satisfaction Problems",
    )

    grid = st.session_state["sudoku_grid"]
    clues_grid = st.session_state["sudoku_original_clues"]
    selected_cell = st.session_state["sudoku_selected_cell"]
    conflicts = Sudoku.find_conflicts(grid)

    # Auto-play loop for step-by-step solving
    sol = st.session_state["sudoku_solution"]
    is_playing = st.session_state["sudoku_is_playing"]
    trace_idx = st.session_state["sudoku_trace_idx"]

    if is_playing and sol and sol.trace:
        if trace_idx < len(sol.trace) - 1:
            time.sleep(st.session_state["sudoku_speed"])
            st.session_state["sudoku_trace_idx"] += 1
            st.rerun()
        else:
            st.session_state["sudoku_is_playing"] = False

    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.markdown("#### ⚙️ Puzzle Setup & Controls")

        preset_choice = st.selectbox(
            "Select Benchmark Instance",
            options=list(SUDOKU_PRESETS.keys()) + ["Blank Grid (Create Custom)"],
            index=0,
            help="Choose from pre-verified benchmark grids or create your own custom board.",
        )

        c_load, c_clear, c_reset = st.columns(3)
        with c_load:
            if st.button("Load Preset", use_container_width=True):
                if preset_choice == "Blank Grid (Create Custom)":
                    new_g = Sudoku.get_blank_grid()
                else:
                    new_g = copy.deepcopy(SUDOKU_PRESETS[preset_choice])
                st.session_state["sudoku_grid"] = copy.deepcopy(new_g)
                st.session_state["sudoku_original_clues"] = copy.deepcopy(new_g)
                st.session_state["sudoku_solution"] = None
                st.session_state["sudoku_view_mode"] = "edit"
                st.session_state["sudoku_is_playing"] = False
                st.rerun()

        with c_clear:
            if st.button("Clear Grid", use_container_width=True, help="Set all cells to 0"):
                empty_g = Sudoku.get_blank_grid()
                st.session_state["sudoku_grid"] = empty_g
                st.session_state["sudoku_original_clues"] = empty_g
                st.session_state["sudoku_solution"] = None
                st.session_state["sudoku_view_mode"] = "edit"
                st.session_state["sudoku_is_playing"] = False
                st.rerun()

        with c_reset:
            if st.button("Reset to Clues", use_container_width=True, help="Revert to original clues"):
                st.session_state["sudoku_grid"] = copy.deepcopy(st.session_state["sudoku_original_clues"])
                st.session_state["sudoku_solution"] = None
                st.session_state["sudoku_view_mode"] = "edit"
                st.session_state["sudoku_is_playing"] = False
                st.rerun()

        # -------------------------------------------------------------
        # EDIT CELL CONTROLS
        # -------------------------------------------------------------
        st.markdown("#### ✏️ Cell Editor")
        sel_r, sel_c = selected_cell

        c_r, c_c = st.columns(2)
        with c_r:
            new_r = st.number_input("Selected Row (1-9)", min_value=1, max_value=9, value=sel_r + 1)
        with c_c:
            new_c = st.number_input("Selected Column (1-9)", min_value=1, max_value=9, value=sel_c + 1)

        active_r, active_c = int(new_r) - 1, int(new_c) - 1
        if (active_r, active_c) != selected_cell:
            st.session_state["sudoku_selected_cell"] = (active_r, active_c)

        st.caption(f"Editing Cell at Row {active_r + 1}, Col {active_c + 1}. Current value: **{grid[active_r][active_c] or 'Empty'}**")

        # Number Keypad Palette
        pal_cols = st.columns(10)
        for num in range(1, 10):
            with pal_cols[num - 1]:
                if st.button(str(num), key=f"sdk_btn_num_{num}", use_container_width=True):
                    grid[active_r][active_c] = num
                    st.session_state["sudoku_solution"] = None
                    st.rerun()

        with pal_cols[9]:
            if st.button("✕", key="sdk_btn_clear_val", use_container_width=True, help="Clear this cell"):
                grid[active_r][active_c] = 0
                st.session_state["sudoku_solution"] = None
                st.rerun()

        # Constraint Conflict Status
        if conflicts:
            st.markdown(
                f"""
                <div style="background: rgba(255, 107, 120, 0.08); border: 1px solid #FF6B78; border-radius: 6px; padding: 0.65rem 0.85rem; font-size: 0.83rem; color: #FFB3BA; margin: 0.5rem 0;">
                    <strong>Constraint Conflict Detected:</strong> {len(conflicts)} cells violate AllDifferent rules.
                    Duplicate values are highlighted in coral red on the board.
                </div>
                """,
                unsafe_allow_html=True,
            )

        # -------------------------------------------------------------
        # SOLVER STRATEGY & TRIGGER
        # -------------------------------------------------------------
        st.markdown("#### 🧠 Backtracking Solver")
        use_mrv = st.checkbox(
            "Enable Minimum-Remaining-Values (MRV) Heuristic",
            value=True,
            help="Selects the cell with the fewest legal numbers remaining to fail fast and prune subtrees early.",
        )

        col_solve_inst, col_solve_step = st.columns(2)

        with col_solve_inst:
            if st.button("⚡ Solve Instantly", type="primary", use_container_width=True, disabled=bool(conflicts)):
                with st.spinner("Executing constraint backtracking..."):
                    solution = Sudoku.solve(grid=grid, use_mrv=use_mrv, record_trace=False)
                    st.session_state["sudoku_solution"] = solution
                    st.session_state["sudoku_view_mode"] = "solved"
                    st.session_state["sudoku_is_playing"] = False

                    if solution.success and solution.solution_grid:
                        st.session_state["sudoku_grid"] = copy.deepcopy(solution.solution_grid)

                        st.session_state["benchmark_history"].append({
                            "puzzle_type": "Sudoku",
                            "algorithm": "Backtracking (MRV)" if use_mrv else "Backtracking (Standard)",
                            "execution_time_ms": round(solution.execution_time_sec * 1000, 3),
                            "nodes_explored": solution.attempted_assignments,
                            "max_frontier_size": solution.backtracks_count,
                            "solution_length": 81 - sum(row.count(0) for row in clues_grid),
                            "success": True,
                        })
                    st.rerun()

        with col_solve_step:
            if st.button("🎬 Solve Step-by-Step", use_container_width=True, disabled=bool(conflicts)):
                with st.spinner("Recording backtracking decision trace..."):
                    solution = Sudoku.solve(grid=grid, use_mrv=use_mrv, record_trace=True)
                    st.session_state["sudoku_solution"] = solution
                    st.session_state["sudoku_trace_idx"] = 0
                    st.session_state["sudoku_view_mode"] = "step_solve"
                    st.session_state["sudoku_is_playing"] = False
                    st.rerun()

    with right_col:
        st.markdown("#### 🔢 9×9 Sudoku Grid")

        view_mode = st.session_state["sudoku_view_mode"]
        current_sol: Optional[SudokuSolution] = st.session_state.get("sudoku_solution")

        if view_mode == "step_solve" and current_sol and current_sol.trace:
            cur_trace_step: SudokuTraceStep = current_sol.trace[st.session_state["sudoku_trace_idx"]]
            display_grid = cur_trace_step.grid_snapshot
            focused_coord = (cur_trace_step.row, cur_trace_step.col)
        elif view_mode == "solved" and current_sol and current_sol.success:
            display_grid = current_sol.solution_grid or grid
            focused_coord = None
        else:
            display_grid = grid
            focused_coord = None

        # Render 9x9 board
        render_sudoku_table(
            grid=display_grid,
            clues_grid=clues_grid,
            selected_cell=selected_cell,
            conflicts=conflicts,
            focused_cell=focused_coord,
        )

        st.caption("Legend: Bold white numbers are original clues; cyan numbers are solver/user assignments; coral red indicates conflicts.")

        # -------------------------------------------------------------
        # STEP-BY-STEP PLAYBACK TOOLBAR
        # -------------------------------------------------------------
        if view_mode == "step_solve" and current_sol and current_sol.trace:
            total_trace = len(current_sol.trace) - 1
            cur_t = st.session_state["sudoku_trace_idx"]
            step_obj: SudokuTraceStep = current_sol.trace[cur_t]

            badge_type = "info"
            if step_obj.action_type == "SUCCESS":
                badge_type = "success"
            elif step_obj.action_type == "CONFLICT" or step_obj.action_type == "BACKTRACK":
                badge_type = "warning"

            st.markdown(
                f"""
                <div style="background: #111821; border: 1px solid #263341; border-radius: 6px; padding: 0.6rem 0.85rem; margin-top: 0.5rem; font-size: 0.85rem;">
                    <span class="status-tag {badge_type}">{step_obj.action_type}</span>
                    <span style="color: #45C6D9; font-weight: 700; margin-left: 0.4rem;">Step {cur_t + 1} of {total_trace + 1}:</span>
                    <span style="color: #F3F6FA; margin-left: 0.3rem;">{step_obj.explanation}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            c_f, c_p, c_pl, c_n, c_l, c_ans = st.columns(6)

            with c_f:
                if st.button("⏮ Start", key="sdk_trace_first", disabled=(cur_t == 0), use_container_width=True):
                    st.session_state["sudoku_trace_idx"] = 0
                    st.session_state["sudoku_is_playing"] = False
                    st.rerun()

            with c_p:
                if st.button("◀ Prev", key="sdk_trace_prev", disabled=(cur_t == 0), use_container_width=True):
                    st.session_state["sudoku_trace_idx"] = max(0, cur_t - 1)
                    st.session_state["sudoku_is_playing"] = False
                    st.rerun()

            with c_pl:
                if is_playing:
                    if st.button("⏸ Pause", key="sdk_trace_pause", use_container_width=True):
                        st.session_state["sudoku_is_playing"] = False
                        st.rerun()
                else:
                    if st.button("▶ Play", key="sdk_trace_play", disabled=(cur_t == total_trace), use_container_width=True):
                        st.session_state["sudoku_is_playing"] = True
                        st.rerun()

            with c_n:
                if st.button("Next ▶", key="sdk_trace_next", disabled=(cur_t == total_trace), use_container_width=True):
                    st.session_state["sudoku_trace_idx"] = min(total_trace, cur_t + 1)
                    st.session_state["sudoku_is_playing"] = False
                    st.rerun()

            with c_l:
                if st.button("⏭ End", key="sdk_trace_end", disabled=(cur_t == total_trace), use_container_width=True):
                    st.session_state["sudoku_trace_idx"] = total_trace
                    st.session_state["sudoku_is_playing"] = False
                    st.rerun()

            with c_ans:
                if st.button("Final 🎯", key="sdk_trace_ans", disabled=(cur_t == total_trace), use_container_width=True):
                    st.session_state["sudoku_trace_idx"] = total_trace
                    st.session_state["sudoku_is_playing"] = False
                    st.rerun()

            c_spd, c_sld = st.columns([1, 3])
            with c_spd:
                spd_choice = st.selectbox(
                    "Speed",
                    options=[0.1, 0.25, 0.5, 1.0],
                    index=1,
                    format_func=lambda x: f"{x}s/step",
                    label_visibility="collapsed",
                    key="sdk_spd_select",
                )
                st.session_state["sudoku_speed"] = spd_choice

            with c_sld:
                sc_trace = st.slider(
                    "Trace Slider",
                    min_value=0,
                    max_value=total_trace,
                    value=cur_t,
                    label_visibility="collapsed",
                    key="sdk_trace_slider",
                )
                if sc_trace != cur_t:
                    st.session_state["sudoku_trace_idx"] = sc_trace
                    st.session_state["sudoku_is_playing"] = False
                    st.rerun()

            if st.button("✏️ Return to Edit Grid Mode", use_container_width=True):
                st.session_state["sudoku_view_mode"] = "edit"
                st.session_state["sudoku_solution"] = None
                st.session_state["sudoku_is_playing"] = False
                st.rerun()

        elif view_mode == "solved" and current_sol:
            if not current_sol.success:
                st.markdown(
                    f"""
                    <div style="background: rgba(255, 107, 120, 0.08); border: 1px solid #FF6B78; border-radius: 6px; padding: 0.65rem 0.85rem; font-size: 0.85rem; color: #FFB3BA; margin: 0.5rem 0;">
                        <strong>Solving Terminated:</strong> {current_sol.error_message}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                    <div style="text-align: center; margin: 0.4rem 0;">
                        <span class="status-tag success">✨ Valid Sudoku Solution Completed!</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            if st.button("✏️ Edit Grid", use_container_width=True):
                st.session_state["sudoku_view_mode"] = "edit"
                st.session_state["sudoku_solution"] = None
                st.rerun()

    # Telemetry Panel
    if current_sol is not None:
        st.markdown("---")
        st.markdown("### 📊 Measured Backtracking Telemetry")
        t_ms = current_sol.execution_time_sec * 1000
        st.markdown(
            f"""
            <div class="metric-strip">
                <div class="metric-cell">
                    <div class="metric-cell-label">Elapsed Time</div>
                    <div class="metric-cell-value cyan">{t_ms:.2f} ms</div>
                </div>
                <div class="metric-cell">
                    <div class="metric-cell-label">Assignments Attempted</div>
                    <div class="metric-cell-value indigo">{current_sol.attempted_assignments:,}</div>
                </div>
                <div class="metric-cell">
                    <div class="metric-cell-label">Backtracking Steps</div>
                    <div class="metric-cell-value green">{current_sol.backtracks_count:,}</div>
                </div>
                <div class="metric-cell">
                    <div class="metric-cell-label">Heuristic Strategy</div>
                    <div class="metric-cell-value amber" style="font-size: 1rem;">{'MRV (Fail-First)' if use_mrv else 'Linear Scan'}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Educational CSP Mechanics
    st.markdown("---")
    with st.expander("📘 Constraint Satisfaction Formulation & MRV Theory", expanded=False):
        st.markdown(
            """
            - **Formal Variables:** 81 variables $X_{(r, c)}$ with domains $D_{(r, c)} \subseteq \{1, \dots, 9\}$.
            - **Binary / AllDifferent Constraints:**
              - Rows: $\\forall r, c_1 \\neq c_2 \\implies X_{(r, c_1)} \\neq X_{(r, c_2)}$
              - Columns: $\\forall c, r_1 \\neq r_2 \\implies X_{(r_1, c)} \\neq X_{(r_2, c)}$
              - Subgrids: $\\forall$ 3×3 blocks, all non-zero cells must be unique.
            - **Minimum Remaining Values (MRV):** Picks the variable with the smallest domain size $|D_{(r, c)}|$.
              When an empty cell has only 1 legal value, it is assigned immediately. If an empty cell has 0 legal values,
              the solver backtracks immediately, avoiding thousands of fruitless sub-branches!
            """
        )
