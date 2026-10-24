"""Product-quality Midnight Graphite / Scientific Indigo styling for AI Puzzle Lab."""

import streamlit as st

CUSTOM_CSS = """
<style>
/* -------------------------------------------------------------
   THEME DESIGN TOKENS: Midnight Graphite / Scientific Indigo
   ------------------------------------------------------------- */
:root {
    --bg-base: #0B0F14;
    --surface-secondary: #111821;
    --surface-elevated: #17212B;
    --border-color: #263341;
    --border-subtle: #1C2733;
    --text-primary: #F3F6FA;
    --text-secondary: #A6B3C2;
    --text-muted: #6C7D93;
    --accent-primary: #7C8CFF;
    --accent-hover: #96A3FF;
    --accent-cyan: #45C6D9;
    --accent-cyan-hover: #5CE0F3;
    --status-success: #48D597;
    --status-warning: #F4B860;
    --status-error: #FF6B78;
    --status-info: #7C8CFF;
}

/* Base Streamlit App Container */
.stApp {
    background-color: var(--bg-base);
    color: var(--text-primary);
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* Main Content Area */
.main .block-container {
    padding-top: 1.25rem;
    padding-bottom: 2.5rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1300px;
}

/* Compact Tool Header */
.tool-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 0.85rem;
    margin-bottom: 1.25rem;
    border-bottom: 1px solid var(--border-color);
}

.tool-header-left {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
}

.tool-category {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--accent-cyan);
}

.tool-title {
    font-size: 1.65rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
    letter-spacing: -0.02em;
}

.tool-subtitle {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin: 0;
}

/* Panel Containers (Developer Tooling Style) */
.panel-box {
    background: var(--surface-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
}

.panel-title {
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-secondary);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* Compact Scientific Metric Strip */
.metric-strip {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 0.6rem;
    margin: 0.85rem 0;
}

.metric-cell {
    background: var(--surface-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: 6px;
    padding: 0.65rem 0.85rem;
    text-align: left;
}

.metric-cell-label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
}

.metric-cell-value {
    font-size: 1.25rem;
    font-weight: 700;
    font-family: "JetBrains Mono", "SF Mono", Menlo, Consolas, monospace;
    color: var(--text-primary);
    margin-top: 0.15rem;
}

.metric-cell-value.cyan { color: var(--accent-cyan); }
.metric-cell-value.indigo { color: var(--accent-primary); }
.metric-cell-value.green { color: var(--status-success); }
.metric-cell-value.amber { color: var(--status-warning); }

/* Status Badges */
.status-tag {
    display: inline-flex;
    align-items: center;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

.status-tag.success {
    background: rgba(72, 213, 151, 0.12);
    border: 1px solid var(--status-success);
    color: var(--status-success);
}

.status-tag.error {
    background: rgba(255, 107, 120, 0.12);
    border: 1px solid var(--status-error);
    color: var(--status-error);
}

.status-tag.warning {
    background: rgba(244, 184, 96, 0.12);
    border: 1px solid var(--status-warning);
    color: var(--status-warning);
}

.status-tag.info {
    background: rgba(124, 140, 255, 0.12);
    border: 1px solid var(--accent-primary);
    color: var(--accent-primary);
}

/* Playback Control Bar */
.playback-bar {
    background: var(--surface-elevated);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin: 0.85rem 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

/* 8-Puzzle Board Representation */
.puzzle-board-wrap {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0.75rem 0;
}

.puzzle-grid-board {
    display: grid;
    grid-template-columns: repeat(3, 86px);
    grid-template-rows: repeat(3, 86px);
    gap: 8px;
    background: #080C10;
    padding: 10px;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

.puzzle-tile-node {
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 1.85rem;
    font-weight: 700;
    font-family: "JetBrains Mono", monospace;
    color: var(--text-primary);
    background: var(--surface-elevated);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    user-select: none;
    transition: transform 0.12s ease, border-color 0.12s ease;
}

.puzzle-tile-node.in-goal {
    border-color: rgba(69, 198, 217, 0.45);
    background: linear-gradient(145deg, #162638, #111B28);
    color: var(--accent-cyan);
}

.puzzle-tile-blank {
    background: #080C10;
    border: 1px dashed #263341;
    border-radius: 8px;
}

/* Streamlit Button Tweaks (Developer Tool Look) */
.stButton > button {
    background-color: var(--surface-elevated);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 0.45rem 0.9rem;
    transition: all 0.15s ease-in-out;
}

.stButton > button:hover {
    border-color: var(--accent-primary);
    color: #FFFFFF;
    background-color: #212E3D;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

.stButton > button:active {
    transform: translateY(1px);
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #5A6BEE 0%, #45C6D9 100%);
    border: none;
    color: #FFFFFF;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #6C7CFF 0%, #5CE0F3 100%);
    box-shadow: 0 2px 8px rgba(69, 198, 217, 0.25);
}

/* Sidebar Styling */
div[data-testid="stSidebar"] {
    background-color: #080C11;
    border-right: 1px solid var(--border-color);
}

/* Form Inputs & Selects */
div[data-baseweb="select"] > div {
    background-color: var(--surface-secondary) !important;
    border-color: var(--border-color) !important;
    border-radius: 6px !important;
}

/* Tab Headers */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid var(--border-color);
}

.stTabs [data-baseweb="tab"] {
    color: var(--text-secondary);
    font-size: 0.88rem;
    font-weight: 600;
    padding: 0.5rem 1rem;
    border-radius: 4px 4px 0 0;
}

.stTabs [aria-selected="true"] {
    color: var(--accent-cyan) !important;
    border-bottom: 2px solid var(--accent-cyan) !important;
    background-color: transparent !important;
}

/* Monospace State Code Box */
.state-code-box {
    font-family: "JetBrains Mono", Menlo, Consolas, monospace;
    font-size: 0.85rem;
    background: #080C10;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 0.6rem 0.8rem;
    color: var(--accent-cyan);
}
</style>
"""


def apply_custom_styles() -> None:
    """Inject Midnight Graphite / Scientific Indigo CSS into the active Streamlit app."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
