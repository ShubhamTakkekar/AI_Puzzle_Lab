"""AI PUZZLE LAB: Interactive Intelligent Problem-Solving Simulator.

Main Streamlit application entry point.
"""

import streamlit as st

from ui.styles import apply_custom_styles
from views.analytics_view import render_analytics_view
from views.arena_view import render_arena_view
from views.eight_puzzle_view import render_eight_puzzle_view
from views.home import render_home_view
from views.missionaries_view import render_missionaries_view
from views.predictor_view import render_predictor_view
from views.sudoku_view import render_sudoku_view

# Application Page Setup
st.set_page_config(
    page_title="AI Puzzle Lab | Intelligent Problem-Solving Simulator",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply Modern Dark-Themed Styling
apply_custom_styles()

# Navigation Pages Mapping
PAGES = {
    "Home Dashboard": render_home_view,
    "8-Puzzle Lab": render_eight_puzzle_view,
    "Missionaries & Cannibals": render_missionaries_view,
    "Sudoku Lab": render_sudoku_view,
    "Algorithm Arena": render_arena_view,
    "Data Analytics": render_analytics_view,
    "Puzzle Difficulty Predictor": render_predictor_view,
}

# Ensure session state page key
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home Dashboard"

# Sidebar Navigation
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 0.25rem 0 0.85rem 0;">
            <div style="font-size: 1.25rem; font-weight: 800; color: #F3F6FA; letter-spacing: -0.02em;">
                🧩 AI PUZZLE <span style="color: #7C8CFF;">LAB</span>
            </div>
            <div style="font-size: 0.75rem; color: #A6B3C2; margin-top: 0.15rem;">
                Intelligent Problem-Solving Simulator
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page_names = list(PAGES.keys())
    current_idx = (
        page_names.index(st.session_state["current_page"])
        if st.session_state["current_page"] in page_names
        else 0
    )

    selected_page = st.radio(
        "Navigation",
        options=page_names,
        index=current_idx,
        label_visibility="collapsed",
    )

    # Sync navigation state
    if selected_page != st.session_state["current_page"]:
        st.session_state["current_page"] = selected_page
        st.rerun()

    st.markdown("---")

    # Real Telemetry in Sidebar if runs have occurred
    history = st.session_state.get("benchmark_history", [])
    if history:
        st.markdown(
            f"""
            <div style="background: #111821; border: 1px solid #263341; border-radius: 6px; padding: 0.65rem 0.85rem; margin-bottom: 0.75rem;">
                <div style="font-size: 0.68rem; font-weight: 700; text-transform: uppercase; color: #6C7D93; letter-spacing: 0.05em;">Session Telemetry</div>
                <div style="display: flex; justify-content: space-between; margin-top: 0.35rem; font-size: 0.82rem;">
                    <span style="color: #A6B3C2;">Searches:</span>
                    <strong style="color: #45C6D9; font-family: monospace;">{len(history)}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 0.2rem; font-size: 0.82rem;">
                    <span style="color: #A6B3C2;">Explored:</span>
                    <strong style="color: #7C8CFF; font-family: monospace;">{sum(r['nodes_explored'] for r in history):,}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div style="color: #6C7D93; font-size: 0.72rem; line-height: 1.4;">
            <strong>AI Puzzle Lab</strong> v2.0<br>
            Python 3.14 · Streamlit 1.66<br>
            Classical AI Search & CSP
        </div>
        """,
        unsafe_allow_html=True,
    )

# Render the selected page view
render_fn = PAGES.get(st.session_state["current_page"], render_home_view)
render_fn()
