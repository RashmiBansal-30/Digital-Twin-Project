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

class EnsemblePredictor:
    """
    Combines SVM, Random Forest, and XGBoost models using soft voting
    (average probability distribution across models).
    """
    def __init__(self, models_dir=SAVED_MODELS_DIR):
        self.models_dir = models_dir
        self.svm = None
        self.rf = None
        self.xgb = None
        self.label_encoder = None
        self.classes_ = None
        self._load_models()

    def _load_models(self):
        svm_path = os.path.join(self.models_dir, "svm_model.joblib")
        rf_path = os.path.join(self.models_dir, "rf_model.joblib")
        xgb_path = os.path.join(self.models_dir, "xgboost_model.joblib")
        encoder_path = os.path.join(self.models_dir, "label_encoder.joblib")

        if os.path.exists(svm_path):
            self.svm = joblib.load(svm_path)
        if os.path.exists(rf_path):
            self.rf = joblib.load(rf_path)
        if os.path.exists(xgb_path):
            self.xgb = joblib.load(xgb_path)
        if os.path.exists(encoder_path):
            self.label_encoder = joblib.load(encoder_path)
            self.classes_ = self.label_encoder.classes_

        if self.rf is not None and self.classes_ is None:
            self.classes_ = self.rf.classes_

    def predict_proba(self, X):
        """
        Returns soft voting ensemble probabilities for each class.
        """
        probs = []
        if self.svm is not None:
            probs.append(self.svm.predict_proba(X))
        if self.rf is not None:
            probs.append(self.rf.predict_proba(X))
        if self.xgb is not None:
            probs.append(self.xgb.predict_proba(X))

        if not probs:
            raise RuntimeError("No models loaded for ensemble prediction.")

        avg_proba = np.mean(probs, axis=0)
        return avg_proba

    def predict(self, X):
        """
        Returns predicted class label for given sample(s).
        """
        proba = self.predict_proba(X)
        best_idx = np.argmax(proba, axis=1)
        if self.classes_ is not None:
            return np.array([self.classes_[i] for i in best_idx])
        return best_idx
