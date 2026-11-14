import os
import sys
from pathlib import Path
from datetime import datetime
from collections import deque

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from prediction.predictor import Predictor
from digital_twin.health_monitor import HealthMonitor
from digital_twin.reliability import MissionReliabilityEvaluator

class EngineDigitalTwin:
    """
    Stateful Digital Twin model for an Aero Piston Engine.
    Integrates real-time telemetry updates with ML fault inference,
    rule-based health monitoring, and mission risk evaluation.
    """
    def __init__(self, engine_id="UAV-ENGINE-001", model_type="rf", max_history=100):
        self.engine_id = engine_id
        self.max_history = max_history
        self.history = deque(maxlen=max_history)

        self.predictor = Predictor(model_type=model_type)
        self.health_monitor = HealthMonitor()
        self.reliability_evaluator = MissionReliabilityEvaluator()

        self.current_telemetry = {
            "rpm": 2800.0,
            "oil_pressure": 4.2,
            "oil_temperature": 90.0,
            "cylinder_head_temperature": 170.0,
            "exhaust_gas_temperature": 620.0,
            "fuel_flow": 8.5,
            "manifold_pressure": 0.85,
            "vibration": 0.25,
            "engine_load": 70.0,
            "ambient_temperature": 25.0
        }

        self.latest_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.latest_prediction = {
            "predicted_fault": "Normal",
            "confidence": 1.0,
            "probabilities": {"Normal": 1.0},
            "model_used": model_type
        }
        self.latest_health = {
            "health_score": 100.0,
            "health_status": "Healthy",
            "alerts": []
        }
        self.latest_reliability = {
            "risk_level": "Low Risk",
            "risk_score": 5.0,
            "recommendation": "Normal mission profile approved.",
            "explanation": "All parameters nominal."
        }

    def set_model(self, model_type):
        self.predictor.load_model(model_type)

    def update_telemetry(self, telemetry_dict):
        """
        Processes new incoming telemetry dict and updates Digital Twin state.
        """
        self.current_telemetry = {
            "rpm": float(telemetry_dict.get("rpm", 2800.0)),
            "oil_pressure": float(telemetry_dict.get("oil_pressure", 4.2)),
            "oil_temperature": float(telemetry_dict.get("oil_temperature", 90.0)),
            "cylinder_head_temperature": float(telemetry_dict.get("cylinder_head_temperature", 170.0)),
            "exhaust_gas_temperature": float(telemetry_dict.get("exhaust_gas_temperature", 620.0)),
            "fuel_flow": float(telemetry_dict.get("fuel_flow", 8.5)),
            "manifold_pressure": float(telemetry_dict.get("manifold_pressure", 0.85)),
            "vibration": float(telemetry_dict.get("vibration", 0.25)),
            "engine_load": float(telemetry_dict.get("engine_load", 70.0)),
            "ambient_temperature": float(telemetry_dict.get("ambient_temperature", 25.0))
        }

        self.latest_timestamp = str(telemetry_dict.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        # 1. Run ML Fault Inference
        self.latest_prediction = self.predictor.predict(self.current_telemetry)

        # 2. Run Health Monitoring
        self.latest_health = self.health_monitor.evaluate(self.current_telemetry)

        # 3. Evaluate Mission Risk
        history_list = list(self.history)
        self.latest_reliability = self.reliability_evaluator.evaluate_risk(
            predicted_fault=self.latest_prediction["predicted_fault"],
            confidence=self.latest_prediction["confidence"],
            health_score=self.latest_health["health_score"],
            active_alerts=self.latest_health["alerts"],
            history=history_list
        )

        # Snapshot full state for history
        snapshot = self.get_current_state()
        self.history.append(snapshot)
        return snapshot

    def get_current_state(self):
        """
        Returns full current state dictionary of the twin.
        """
        return {
            "engine_id": self.engine_id,
            "timestamp": self.latest_timestamp,
            "telemetry": self.current_telemetry,
            "prediction": self.latest_prediction,
            "health": self.latest_health,
            "reliability": self.latest_reliability
        }

    def get_history(self, limit=50):
        """
        Returns last `limit` telemetry snapshots.
        """
        history_list = list(self.history)
        return history_list[-limit:] if limit else history_list
