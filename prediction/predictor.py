import os
import sys
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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

class Predictor:
    """
    Inference engine that loads trained model artifacts and predicts engine fault classes.
    Supports Random Forest, SVM, XGBoost, and Ensemble models.
    """
    def __init__(self, model_type="rf", models_dir=SAVED_MODELS_DIR):
        self.models_dir = models_dir
        self.model_type = model_type.lower()
        self.model = None
        self.label_encoder = None
        self.load_model(self.model_type)

    def load_model(self, model_type):
        self.model_type = model_type.lower()
        if self.model_type == "rf" or self.model_type == "random_forest":
            model_path = os.path.join(self.models_dir, "rf_model.joblib")
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found at {model_path}. Please run training first.")
            self.model = joblib.load(model_path)
            self.label_encoder = None

        elif self.model_type == "svm":
            model_path = os.path.join(self.models_dir, "svm_model.joblib")
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found at {model_path}. Please run training first.")
            self.model = joblib.load(model_path)
            self.label_encoder = None

        elif self.model_type == "xgboost" or self.model_type == "xgb":
            model_path = os.path.join(self.models_dir, "xgboost_model.joblib")
            encoder_path = os.path.join(self.models_dir, "label_encoder.joblib")
            if not os.path.exists(model_path) or not os.path.exists(encoder_path):
                raise FileNotFoundError(f"XGBoost artifacts not found in {self.models_dir}. Please run training first.")
            self.model = joblib.load(model_path)
            self.label_encoder = joblib.load(encoder_path)

        elif self.model_type == "ensemble":
            from models.ensemble import EnsemblePredictor
            self.model = EnsemblePredictor(models_dir=self.models_dir)
            self.label_encoder = getattr(self.model, "label_encoder", None)

        else:
            raise ValueError(f"Unsupported model_type: {model_type}. Choose 'rf', 'svm', 'xgboost', or 'ensemble'.")

    def predict(self, telemetry_data):
        """
        Predicts fault class and confidence scores for incoming telemetry.
        `telemetry_data` can be a dictionary or pandas DataFrame.
        """
        if self.model is None:
            raise RuntimeError("No model is loaded for prediction.")

        if isinstance(telemetry_data, dict):
            df = pd.DataFrame([telemetry_data])
        elif isinstance(telemetry_data, pd.DataFrame):
            df = telemetry_data
        else:
            raise TypeError("telemetry_data must be a dictionary or pandas DataFrame.")

        # Validate feature presence
        missing_feats = [col for col in FEATURE_COLUMNS if col not in df.columns]
        if missing_feats:
            raise ValueError(f"Missing required telemetry features: {missing_feats}")

        X = df[FEATURE_COLUMNS]

        if self.model_type == "ensemble":
            probabilities = self.model.predict_proba(X)[0]
            classes = self.model.classes_
            best_idx = np.argmax(probabilities)
            predicted_class = str(classes[best_idx])
            confidence = float(probabilities[best_idx])
            prob_dict = {str(classes[i]): float(probabilities[i]) for i in range(len(classes))}

        elif self.model_type in ["xgboost", "xgb"]:
            pred_idx = self.model.predict(X)[0]
            predicted_class = str(self.label_encoder.inverse_transform([pred_idx])[0])
            if hasattr(self.model, "predict_proba"):
                probabilities = self.model.predict_proba(X)[0]
                classes = self.label_encoder.classes_
                confidence = float(np.max(probabilities))
                prob_dict = {str(classes[i]): float(probabilities[i]) for i in range(len(classes))}
            else:
                confidence = 1.0
                prob_dict = {predicted_class: 1.0}

        else:
            predicted_class = str(self.model.predict(X)[0])
            if hasattr(self.model, "predict_proba"):
                probabilities = self.model.predict_proba(X)[0]
                classes = getattr(self.model, "classes_", getattr(getattr(self.model, "named_steps", {}).get("classifier", None), "classes_", None))
                if classes is not None:
                    confidence = float(np.max(probabilities))
                    prob_dict = {str(classes[i]): float(probabilities[i]) for i in range(len(classes))}
                else:
                    confidence = 1.0
                    prob_dict = {predicted_class: 1.0}
            else:
                confidence = 1.0
                prob_dict = {predicted_class: 1.0}

        return {
            "predicted_fault": predicted_class,
            "confidence": round(confidence, 4),
            "probabilities": prob_dict,
            "model_used": self.model_type
        }

if __name__ == "__main__":
    sample_data = {
        "rpm": 2800,
        "oil_pressure": 4.2,
        "oil_temperature": 90,
        "cylinder_head_temperature": 170,
        "exhaust_gas_temperature": 620,
        "fuel_flow": 8.5,
        "manifold_pressure": 0.85,
        "vibration": 0.25,
        "engine_load": 70,
        "ambient_temperature": 25
    }
    predictor = Predictor(model_type="rf")
    result = predictor.predict(sample_data)
    print("Sample Prediction Result:", result)
