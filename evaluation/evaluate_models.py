import os
import sys
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

PROCESSED_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "engine_telemetry_processed.csv")
SAVED_MODELS_DIR = os.path.join(PROJECT_ROOT, "saved_models")
PLOTS_DIR = os.path.join(PROJECT_ROOT, "evaluation", "plots")
METRICS_PATH = os.path.join(PROJECT_ROOT, "evaluation", "metrics.json")

FEATURE_COLUMNS = [
    "rpm",
    "oil_pressure",
    "oil_temperature",
    "cylinder_head_temperature",
    "exhaust_gas_temperature",
    "fuel_flow",
    "manifold_pressure",
    "vibration",
    "engine_load",
    "ambient_temperature"
]
TARGET_COLUMN = "fault_type"

def evaluate_all(data_path=PROCESSED_DATA_PATH, models_dir=SAVED_MODELS_DIR, plots_dir=PLOTS_DIR, metrics_path=METRICS_PATH, random_state=42):
    """
    Evaluates SVM, Random Forest, and XGBoost models on the test split,
    computes evaluation metrics, saves metrics JSON and performance plots.
    """
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)

    df = pd.read_csv(data_path)
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=random_state, stratify=y
    )

    class_names = sorted(y.unique().tolist())

    # Load trained models or train them if missing
    svm_path = os.path.join(models_dir, "svm_model.joblib")
    rf_path = os.path.join(models_dir, "rf_model.joblib")
    xgb_path = os.path.join(models_dir, "xgboost_model.joblib")
    encoder_path = os.path.join(models_dir, "label_encoder.joblib")

    if not (os.path.exists(svm_path) and os.path.exists(rf_path) and os.path.exists(xgb_path)):
        print("Training missing models before evaluation...")
        from models.train_svm import train_svm
        from models.train_random_forest import train_random_forest
        from models.train_xgboost import train_xgboost
        train_svm(data_path, models_dir, random_state)
        train_random_forest(data_path, models_dir, random_state)
        train_xgboost(data_path, models_dir, random_state)

    svm_model = joblib.load(svm_path)
    rf_model = joblib.load(rf_path)
    xgb_model = joblib.load(xgb_path)
    label_encoder = joblib.load(encoder_path)

    models = {
        "Support Vector Machine": (svm_model, False),
        "Random Forest": (rf_model, False),
        "XGBoost": (xgb_model, True)
    }

    metrics_dict = {}
    cm_dict = {}

    for name, (model, is_xgb) in models.items():
        if is_xgb:
            y_pred_idx = model.predict(X_test)
            y_pred = label_encoder.inverse_transform(y_pred_idx)
        else:
            y_pred = model.predict(X_test)

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, average="macro"))
        rec = float(recall_score(y_test, y_pred, average="macro"))
        f1 = float(f1_score(y_test, y_pred, average="macro"))

        report = classification_report(y_test, y_pred, output_dict=True)
        cm = confusion_matrix(y_test, y_pred, labels=class_names)
        cm_dict[name] = cm

        metrics_dict[name] = {
            "accuracy": round(acc, 4),
            "precision_macro": round(prec, 4),
            "recall_macro": round(rec, 4),
            "f1_macro": round(f1, 4),
            "classification_report": report
        }

        print(f"\n=== {name} Metrics ===")
        print(f"Accuracy:  {acc:.4f}")
        print(f"Precision: {prec:.4f}")
        print(f"Recall:    {rec:.4f}")
        print(f"F1 Score:  {f1:.4f}")

    # Save metrics JSON
    with open(metrics_path, "w") as f:
        json.dump(metrics_dict, f, indent=4)
    print(f"\nSaved evaluation metrics to {metrics_path}")

    # Plot 1: Model Comparison Chart
    plt.figure(figsize=(10, 6))
    model_names = list(metrics_dict.keys())
    metric_keys = ["accuracy", "precision_macro", "recall_macro", "f1_macro"]
    x = np.arange(len(model_names))
    width = 0.2

    for i, m_key in enumerate(metric_keys):
        values = [metrics_dict[m][m_key] for m in model_names]
        plt.bar(x + i * width, values, width, label=m_key.replace("_macro", "").capitalize())

    plt.title("Model Performance Comparison (Synthetic Telemetry Dataset)")
    plt.ylabel("Score")
    plt.ylim(0.0, 1.05)
    plt.xticks(x + width * 1.5, model_names)
    plt.legend(loc="lower right")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "model_comparison.png"), dpi=300)
    plt.close()

    # Plot 2: Confusion Matrices
    for name, cm in cm_dict.items():
        plt.figure(figsize=(7, 5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=class_names, yticklabels=class_names)
        plt.title(f"Confusion Matrix - {name}")
        plt.xlabel("Predicted Class")
        plt.ylabel("True Class")
        plt.tight_layout()
        filename = f"confusion_matrix_{name.lower().replace(' ', '_')}.png"
        plt.savefig(os.path.join(plots_dir, filename), dpi=300)
        plt.close()

    # Plot 3: Feature Importance (RF & XGBoost)
    plt.figure(figsize=(10, 6))
    rf_importances = rf_model.feature_importances_
    xgb_importances = xgb_model.feature_importances_

    indices = np.arange(len(FEATURE_COLUMNS))
    width = 0.35

    plt.barh(indices - width/2, rf_importances, width, label="Random Forest", color="#1f77b4")
    plt.barh(indices + width/2, xgb_importances, width, label="XGBoost", color="#ff7f0e")

    plt.yticks(indices, FEATURE_COLUMNS)
    plt.xlabel("Feature Importance")
    plt.title("Feature Importances for Tree-Based Models")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "feature_importance.png"), dpi=300)
    plt.close()

    print(f"Generated and saved all evaluation plots in {plots_dir}")
    return metrics_dict

if __name__ == "__main__":
    evaluate_all()
