import os
import sys
from pathlib import Path
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
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

def train_svm(data_path=PROCESSED_DATA_PATH, output_dir=SAVED_MODELS_DIR, random_state=42):
    """
    Trains Support Vector Machine classifier using a Scikit-learn Pipeline
    with StandardScaler to prevent data leakage.
    """
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv(data_path)
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=random_state, stratify=y
    )

    svm_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', SVC(probability=True, kernel='rbf', C=1.0, random_state=random_state))
    ])

    print("Training Support Vector Machine (SVM)...")
    svm_pipeline.fit(X_train, y_train)

    y_pred = svm_pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"SVM Test Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    model_path = os.path.join(output_dir, "svm_model.joblib")
    joblib.dump(svm_pipeline, model_path)
    print(f"SVM model saved to {model_path}")

    return svm_pipeline, X_test, y_test

if __name__ == "__main__":
    train_svm()
