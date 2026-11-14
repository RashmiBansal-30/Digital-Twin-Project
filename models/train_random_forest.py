import os
import sys
from pathlib import Path
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

PROCESSED_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "engine_telemetry_processed.csv")
SAVED_MODELS_DIR = os.path.join(PROJECT_ROOT, "saved_models")

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

def train_random_forest(data_path=PROCESSED_DATA_PATH, output_dir=SAVED_MODELS_DIR, random_state=42):
    """
    Trains Random Forest classifier on telemetry features.
    """
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv(data_path)
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=random_state, stratify=y
    )

    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        random_state=random_state,
        n_jobs=-1
    )

    print("Training Random Forest Classifier...")
    rf_model.fit(X_train, y_train)

    y_pred = rf_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Random Forest Test Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    model_path = os.path.join(output_dir, "rf_model.joblib")
    joblib.dump(rf_model, model_path)
    print(f"Random Forest model saved to {model_path}")

    return rf_model, X_test, y_test

if __name__ == "__main__":
    train_random_forest()
