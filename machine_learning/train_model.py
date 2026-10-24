"""Train and evaluate a supervised Random Forest model for 8-puzzle difficulty prediction."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Tuple
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from machine_learning.dataset_generator import generate_difficulty_dataset

ARTIFACTS_DIR = Path(__file__).resolve().parent / "model_artifacts"
MODEL_FILE = ARTIFACTS_DIR / "difficulty_model.joblib"
METRICS_FILE = ARTIFACTS_DIR / "metrics.json"
DATASET_FILE = ARTIFACTS_DIR / "dataset.csv"

FEATURE_NAMES = [
    "manhattan_distance",
    "misplaced_tiles",
    "inversions_count",
    "linear_conflicts",
    "blank_row",
    "blank_col",
    "correct_row_count",
    "correct_col_count",
]


def train_and_save_model(
    num_samples: int = 180,
    seed: int = 42,
    force_regenerate: bool = False,
) -> Tuple[RandomForestClassifier, Dict[str, Any]]:
    """Train Random Forest classifier on mathematically derived 8-puzzle features.

    Returns:
        Trained model instance and metrics dictionary.
    """
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    if DATASET_FILE.exists() and not force_regenerate:
        df = pd.read_csv(DATASET_FILE)
    else:
        df = generate_difficulty_dataset(num_samples=num_samples, seed=seed)
        df.to_csv(DATASET_FILE, index=False)

    X = df[FEATURE_NAMES]
    y = df["difficulty_label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=seed, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        random_state=seed,
        class_weight="balanced",
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    conf_mat = confusion_matrix(y_test, y_pred, labels=["Easy", "Medium", "Hard"]).tolist()

    feature_importances = dict(zip(FEATURE_NAMES, [round(f, 4) for f in clf.feature_importances_]))

    metrics = {
        "accuracy": round(report["accuracy"], 4),
        "total_samples": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "classes": ["Easy", "Medium", "Hard"],
        "classification_report": report,
        "confusion_matrix": conf_mat,
        "feature_importances": feature_importances,
    }

    # Save artifacts
    joblib.dump(clf, MODEL_FILE)
    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    return clf, metrics


def load_model_and_metrics() -> Tuple[RandomForestClassifier, Dict[str, Any]]:
    """Load cached model and metrics, training a new instance if artifacts do not exist."""
    if MODEL_FILE.exists() and METRICS_FILE.exists():
        clf = joblib.load(MODEL_FILE)
        with open(METRICS_FILE, "r", encoding="utf-8") as f:
            metrics = json.load(f)
        return clf, metrics

    return train_and_save_model()


if __name__ == "__main__":
    print("Training 8-puzzle difficulty prediction model...")
    model, metrics_dict = train_and_save_model(num_samples=180)
    print(f"Model successfully trained! Test Accuracy: {metrics_dict['accuracy'] * 100:.1f}%")
    print("Feature Importances:", metrics_dict["feature_importances"])
