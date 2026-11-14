import os
import sys
from pathlib import Path
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
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

def train_xgboost(data_path=PROCESSED_DATA_PATH, output_dir=SAVED_MODELS_DIR, random_state=42):
    """
    Trains XGBoost classifier with LabelEncoder for target categories.
    """
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv(data_path)
    X = df[FEATURE_COLUMNS]
    y_raw = df[TARGET_COLUMN]

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=random_state, stratify=y
    )

    xgb_model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=random_state,
        eval_metric='mlogloss'
    )

    print("Training XGBoost Classifier...")
    xgb_model.fit(X_train, y_train)

    y_pred = xgb_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"XGBoost Test Accuracy: {accuracy:.4f}")

    y_test_names = label_encoder.inverse_transform(y_test)
    y_pred_names = label_encoder.inverse_transform(y_pred)
    print("\nClassification Report:")
    print(classification_report(y_test_names, y_pred_names))

    model_path = os.path.join(output_dir, "xgboost_model.joblib")
    encoder_path = os.path.join(output_dir, "label_encoder.joblib")

    joblib.dump(xgb_model, model_path)
    joblib.dump(label_encoder, encoder_path)
    print(f"XGBoost model saved to {model_path}")
    print(f"Label encoder saved to {encoder_path}")

    return xgb_model, label_encoder, X_test, y_test

if __name__ == "__main__":
    train_xgboost()
