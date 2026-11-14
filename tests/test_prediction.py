import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from prediction.predictor import Predictor

def test_predictor_rf():
    predictor = Predictor(model_type="rf")
    sample = {
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
    result = predictor.predict(sample)
    assert "predicted_fault" in result
    assert "confidence" in result
    assert "probabilities" in result
    assert 0.0 <= result["confidence"] <= 1.0

def test_predictor_missing_feature():
    predictor = Predictor(model_type="rf")
    incomplete_sample = {"rpm": 2800}
    with pytest.raises(ValueError):
        predictor.predict(incomplete_sample)
