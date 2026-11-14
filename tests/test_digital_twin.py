import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from digital_twin.health_monitor import HealthMonitor
from digital_twin.reliability import MissionReliabilityEvaluator
from digital_twin.engine_twin import EngineDigitalTwin

def test_health_monitor_normal():
    hm = HealthMonitor()
    telemetry = {
        "cylinder_head_temperature": 170.0,
        "oil_temperature": 90.0,
        "oil_pressure": 4.2,
        "vibration": 0.25,
        "exhaust_gas_temperature": 620.0
    }
    res = hm.evaluate(telemetry)
    assert res["health_score"] == 100.0
    assert res["health_status"] == "Healthy"
    assert len(res["alerts"]) == 0

def test_health_monitor_overheating():
    hm = HealthMonitor()
    telemetry = {
        "cylinder_head_temperature": 215.0,
        "oil_temperature": 115.0,
        "oil_pressure": 4.0,
        "vibration": 0.3,
        "exhaust_gas_temperature": 730.0
    }
    res = hm.evaluate(telemetry)
    assert res["health_score"] < 50.0
    assert res["health_status"] == "Critical"
    assert len(res["alerts"]) > 0

def test_reliability_evaluator():
    mre = MissionReliabilityEvaluator()
    risk = mre.evaluate_risk(
        predicted_fault="Overheating",
        confidence=0.95,
        health_score=40.0,
        active_alerts=[{"severity": "CRITICAL", "message": "High CHT"}]
    )
    assert risk["risk_level"] in ["Low Risk", "Medium Risk", "High Risk"]
    assert "explanation" in risk
    assert "recommendation" in risk

def test_engine_digital_twin_update():
    twin = EngineDigitalTwin(model_type="rf")
    sample = {
        "timestamp": "2026-03-30 12:00:00",
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
    snapshot = twin.update_telemetry(sample)
    assert snapshot["engine_id"] == "UAV-ENGINE-001"
    assert snapshot["prediction"]["predicted_fault"] == "Normal"
    assert len(twin.get_history()) == 1
