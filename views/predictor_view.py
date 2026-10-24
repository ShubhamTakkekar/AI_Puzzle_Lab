"""Puzzle Difficulty Predictor: Supervised machine learning difficulty estimation."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from machine_learning.predict_difficulty import predict_puzzle_difficulty
from machine_learning.train_model import (
    FEATURE_NAMES,
    load_model_and_metrics,
    train_and_save_model,
)
from puzzles.eight_puzzle import PRESET_PUZZLES, EightPuzzle
from ui.components import render_header, render_puzzle_html


def plot_feature_importances(importances: dict) -> plt.Figure:
    """Generate a clean dark-themed horizontal bar chart of feature importances."""
    fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=100)
    fig.patch.set_facecolor("#0B0F14")
    ax.set_facecolor("#111821")

    items = sorted(importances.items(), key=lambda x: x[1])
    names = [x[0].replace("_", " ").title() for x in items]
    vals = [x[1] for x in items]

    bars = ax.barh(names, vals, color="#45C6D9", height=0.55, edgecolor="#263341")
    for bar in bars:
        w = bar.get_width()
        ax.annotate(
            f"{w:.3f}",
            xy=(w, bar.get_y() + bar.get_height() / 2),
            xytext=(4, 0),
            textcoords="offset points",
            ha="left", va="center",
            color="#F3F6FA", fontsize=8, fontweight="bold",
        )

    ax.set_title("Random Forest Gini Feature Importances", color="#F3F6FA", fontsize=10.5, fontweight="bold", pad=10)
    ax.set_xlabel("Importance Weight", color="#A6B3C2", fontsize=9, labelpad=6)
    ax.tick_params(colors="#A6B3C2", labelsize=8.5)
    for spine in ax.spines.values():
        spine.set_color("#263341")
    ax.grid(True, linestyle="--", alpha=0.2, color="#263341")
    fig.tight_layout()
    return fig


def render_predictor_view() -> None:
    """Render the machine learning difficulty predictor view."""
    render_header(
        title="Puzzle Difficulty Predictor",
        subtitle="Supervised machine learning with Scikit-learn for state-space difficulty classification",
        category="Machine Learning & Heuristic Modeling",
    )

    clf, metrics = load_model_and_metrics()

    acc_pct = metrics.get("accuracy", 0.0) * 100
    train_n = metrics.get("train_samples", 0)
    test_n = metrics.get("test_samples", 0)

    st.markdown(
        f"""
        <div class="metric-strip">
            <div class="metric-cell">
                <div class="metric-cell-label">Classifier</div>
                <div class="metric-cell-value cyan" style="font-size: 1.05rem;">Random Forest</div>
            </div>
            <div class="metric-cell">
                <div class="metric-cell-label">Test Set Accuracy</div>
                <div class="metric-cell-value green">{acc_pct:.1f}%</div>
            </div>
            <div class="metric-cell">
                <div class="metric-cell-label">Training Size</div>
                <div class="metric-cell-value indigo">{train_n} boards</div>
            </div>
            <div class="metric-cell">
                <div class="metric-cell-label">Target Metric</div>
                <div class="metric-cell-value amber" style="font-size: 0.95rem;">Optimal Depth (A*)</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_pred, tab_model = st.tabs(["🎯 Live Difficulty Prediction", "📊 Model Diagnostics & Evaluation"])

    with tab_pred:
        left_col, right_col = st.columns([1, 1], gap="large")

        with left_col:
            st.markdown("#### ⚙️ Input Board Configuration")

            preset_key = st.selectbox(
                "Select 8-Puzzle Instance",
                options=list(PRESET_PUZZLES.keys()),
                index=3,  # Easy (4 Moves)
            )

            col_preset, col_rnd = st.columns(2)
            with col_preset:
                if st.button("Use Preset Board", use_container_width=True):
                    st.session_state["predictor_state"] = PRESET_PUZZLES[preset_key]
                    st.session_state["prediction_result"] = None
                    st.rerun()

            with col_rnd:
                if st.button("Generate Random Solvable", use_container_width=True):
                    rnd_state = EightPuzzle.generate_random_solvable(steps_from_goal=16)
                    st.session_state["predictor_state"] = rnd_state
                    st.session_state["prediction_result"] = None
                    st.rerun()

            active_state = st.session_state.get(
                "predictor_state", PRESET_PUZZLES["Easy (4 Moves)"]
            )

            if st.button("🤖 Predict Difficulty Tier", type="primary", use_container_width=True):
                with st.spinner("Extracting mathematical features and inferring difficulty..."):
                    pred_res = predict_puzzle_difficulty(active_state)
                    st.session_state["prediction_result"] = pred_res
                st.rerun()

        with right_col:
            st.markdown("#### 🧩 Inspected Board")
            render_puzzle_html(active_state)

        # Display Inference Output
        pred_res = st.session_state.get("prediction_result")
        if pred_res is not None:
            st.markdown("---")
            st.markdown("### 🔍 Model Inference Output")

            if not pred_res.get("solvable", True):
                st.markdown(
                    f"""
                    <div style="background: rgba(255, 107, 120, 0.08); border: 1px solid #FF6B78; border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem;">
                        <span class="status-tag error">Unsolvable Configuration</span>
                        <div style="font-size: 0.9rem; color: #FF6B78; margin-top: 0.5rem;">{pred_res['error_message']}</div>
                        <div style="font-size: 0.8rem; color: #A6B3C2; margin-top: 0.25rem;"><em>{pred_res['disclaimer']}</em></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                pred_label = pred_res["predicted_difficulty"]
                confidence = pred_res["confidence_pct"]
                probs = pred_res["probabilities"]

                color_map = {
                    "Easy": "#48D597",
                    "Medium": "#F4B860",
                    "Hard": "#FF6B78",
                }
                badge_color = color_map.get(pred_label, "#45C6D9")

                st.markdown(
                    f"""
                    <div style="background: #111821; border: 1px solid #263341; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 0.75rem;">
                        <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: #A6B3C2;">Predicted Difficulty Classification</div>
                        <div style="font-size: 2rem; font-weight: 800; color: {badge_color}; margin: 0.2rem 0;">{pred_label} Tier</div>
                        <div style="font-size: 0.9rem; color: #F3F6FA;">Model Confidence: <strong>{confidence}%</strong></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown("##### Class Probability Distribution")
                for cls_name, prob_val in probs.items():
                    col_cls, col_bar = st.columns([1, 4])
                    with col_cls:
                        st.write(f"**{cls_name}** ({prob_val * 100:.1f}%)")
                    with col_bar:
                        st.progress(float(prob_val))

                st.markdown("##### Extracted Feature Vector (No Target Leakage)")
                feats = pred_res["features"]
                feat_df = pd.DataFrame([
                    {"Feature": k.replace("_", " ").title(), "Value": v}
                    for k, v in feats.items()
                ])
                st.dataframe(feat_df, use_container_width=True)

                st.caption(f"ℹ️ {pred_res['disclaimer']}")

    with tab_model:
        st.markdown("#### 🔬 Supervised Training & Cross-Validation Diagnostics")

        st.markdown(
            """
            <div style="background: #111821; border: 1px solid #263341; border-radius: 8px; padding: 0.85rem 1rem; margin-bottom: 1rem; font-size: 0.88rem; color: #A6B3C2; line-height: 1.5;">
                <strong>Methodology & Target Leakage Prevention:</strong><br>
                • <strong>Ground Truth:</strong> Computed via optimal A* search. Binned into <em>Easy</em> (≤ 6 moves), <em>Medium</em> (7–12 moves), and <em>Hard</em> (≥ 13 moves).<br>
                • <strong>Zero Target Leakage:</strong> The classifier receives strictly intrinsic mathematical features (Manhattan distance, inversion count, misplaced tiles, linear conflicts). No search telemetry is provided at inference time.
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_rep, col_feat = st.columns([1, 1], gap="large")

        with col_rep:
            st.markdown("##### Test Set Classification Report")
            rep = metrics.get("classification_report", {})
            rows = []
            for cls in ["Easy", "Medium", "Hard"]:
                if cls in rep:
                    rows.append({
                        "Class": cls,
                        "Precision": round(rep[cls]["precision"], 3),
                        "Recall": round(rep[cls]["recall"], 3),
                        "F1-Score": round(rep[cls]["f1-score"], 3),
                        "Support": int(rep[cls]["support"]),
                    })
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True)

            st.markdown("##### Test Confusion Matrix")
            conf_mat = metrics.get("confusion_matrix", [])
            if conf_mat:
                conf_df = pd.DataFrame(
                    conf_mat,
                    index=["Actual Easy", "Actual Medium", "Actual Hard"],
                    columns=["Pred Easy", "Pred Medium", "Pred Hard"],
                )
                st.dataframe(conf_df, use_container_width=True)

        with col_feat:
            st.markdown("##### Gini Feature Importances")
            feat_imp = metrics.get("feature_importances", {})
            if feat_imp:
                fig = plot_feature_importances(feat_imp)
                st.pyplot(fig, use_container_width=True)

        st.markdown("---")
        if st.button("🔄 Retrain Classifier Live with Fresh Dataset", use_container_width=True):
            with st.spinner("Generating fresh balanced dataset and retraining classifier..."):
                _, new_metrics = train_and_save_model(num_samples=210, force_regenerate=True)
                st.success(f"Model retrained successfully! New Test Accuracy: {new_metrics['accuracy'] * 100:.1f}%")
            st.rerun()
