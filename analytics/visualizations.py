"""Matplotlib visual charting customized for modern dark-themed AI telemetry."""

import matplotlib
matplotlib.use("Agg")  # Headless backend for web app compatibility
import matplotlib.pyplot as plt
import pandas as pd

# Palette tokens: Midnight Graphite / Scientific Indigo
COLOR_BG = "#0B0F14"
COLOR_CARD = "#111821"
COLOR_GRID = "#263341"
COLOR_TEXT = "#F3F6FA"
COLOR_MUTED = "#A6B3C2"
PALETTE = ["#45C6D9", "#7C8CFF", "#48D597", "#F4B860", "#FF6B78", "#96A3FF"]


def set_dark_plot_style(ax: plt.Axes, title: str, xlabel: str, ylabel: str) -> None:
    """Apply modern dark styling tokens to a Matplotlib axes."""
    fig = ax.get_figure()
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_facecolor(COLOR_CARD)

    ax.set_title(title, color=COLOR_TEXT, fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel, color=COLOR_MUTED, fontsize=10, labelpad=8)
    ax.set_ylabel(ylabel, color=COLOR_MUTED, fontsize=10, labelpad=8)

    ax.tick_params(colors=COLOR_MUTED, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color(COLOR_GRID)

    ax.grid(True, linestyle="--", alpha=0.3, color=COLOR_GRID)


def plot_execution_time_bar(df: pd.DataFrame) -> plt.Figure:
    """Generate a clean bar chart comparing mean execution time by algorithm."""
    fig, ax = plt.subplots(figsize=(7, 3.8), dpi=100)

    if df.empty or "execution_time_ms" not in df.columns:
        set_dark_plot_style(ax, "Mean Execution Time (ms)", "Algorithm", "Time (ms)")
        ax.text(
            0.5, 0.5, "No benchmark data recorded yet.",
            ha="center", va="center", color=COLOR_MUTED, transform=ax.transAxes
        )
        fig.tight_layout()
        return fig

    means = df.groupby("algorithm")["execution_time_ms"].mean().reset_index()
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(means))]

    bars = ax.bar(means["algorithm"], means["execution_time_ms"], color=colors, width=0.55, edgecolor="#334155")

    # Add numeric labels on bars
    for bar in bars:
        h = bar.get_height()
        ax.annotate(
            f"{h:.2f} ms",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center", va="bottom",
            color=COLOR_TEXT, fontsize=8.5, fontweight="bold"
        )

    set_dark_plot_style(ax, "Average Execution Time (Lower is Faster)", "Algorithm", "Time (ms)")
    ax.set_xticks(range(len(means)))
    ax.set_xticklabels(means["algorithm"], rotation=15, ha="right", color=COLOR_MUTED)
    fig.tight_layout()
    return fig


def plot_nodes_explored_bar(df: pd.DataFrame) -> plt.Figure:
    """Generate a clean bar chart comparing mean states explored by algorithm."""
    fig, ax = plt.subplots(figsize=(7, 3.8), dpi=100)

    if df.empty or "nodes_explored" not in df.columns:
        set_dark_plot_style(ax, "Average Nodes Explored", "Algorithm", "Nodes Count")
        ax.text(
            0.5, 0.5, "No benchmark data recorded yet.",
            ha="center", va="center", color=COLOR_MUTED, transform=ax.transAxes
        )
        fig.tight_layout()
        return fig

    means = df.groupby("algorithm")["nodes_explored"].mean().reset_index()
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(means))]

    bars = ax.bar(means["algorithm"], means["nodes_explored"], color=colors, width=0.55, edgecolor="#334155")

    for bar in bars:
        h = bar.get_height()
        ax.annotate(
            f"{int(h):,}",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center", va="bottom",
            color=COLOR_TEXT, fontsize=8.5, fontweight="bold"
        )

    set_dark_plot_style(ax, "Average Explored States (Lower is More Efficient)", "Algorithm", "States / Nodes")
    ax.set_xticks(range(len(means)))
    ax.set_xticklabels(means["algorithm"], rotation=15, ha="right", color=COLOR_MUTED)
    fig.tight_layout()
    return fig


def plot_runtime_vs_nodes_scatter(df: pd.DataFrame) -> plt.Figure:
    """Generate scatter plot correlating execution time with nodes explored."""
    fig, ax = plt.subplots(figsize=(7, 3.8), dpi=100)

    if df.empty or len(df) < 1:
        set_dark_plot_style(ax, "Execution Time vs. States Explored", "Explored Nodes", "Time (ms)")
        ax.text(
            0.5, 0.5, "Insufficient benchmark points.",
            ha="center", va="center", color=COLOR_MUTED, transform=ax.transAxes
        )
        fig.tight_layout()
        return fig

    algos = df["algorithm"].unique()
    for i, algo in enumerate(algos):
        subset = df[df["algorithm"] == algo]
        ax.scatter(
            subset["nodes_explored"],
            subset["execution_time_ms"],
            label=algo,
            color=PALETTE[i % len(PALETTE)],
            alpha=0.85,
            edgecolors="#FFFFFF",
            s=60,
        )

    set_dark_plot_style(ax, "Search Complexity: Runtime vs. Explored States", "Nodes Explored", "Execution Time (ms)")
    ax.legend(facecolor=COLOR_CARD, edgecolor=COLOR_GRID, labelcolor=COLOR_TEXT, fontsize=8)
    fig.tight_layout()
    return fig
