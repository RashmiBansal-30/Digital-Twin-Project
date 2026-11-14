import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

class MissionReliabilityEvaluator:
    """
    Evaluates Mission Reliability and Risk Level (Low, Medium, High)
    based on predicted engine fault class, model confidence, health score,
    and parameter trend persistence.
    """
    def __init__(self):
        pass

    def evaluate_risk(self, predicted_fault, confidence, health_score, active_alerts=None, history=None):
        """
        Calculates mission risk indicator and risk explanation.
        Returns risk_level (str: "Low Risk", "Medium Risk", "High Risk") and risk_details (dict).
        """
        active_alerts = active_alerts or []
        risk_score = 0  # 0 to 100 risk score scale

        # 1. Fault class risk component
        fault_weights = {
            "Normal": 5,
            "Overheating": 65,
            "Lubrication Fault": 75,
            "Mechanical/Vibration Fault": 70
        }
        base_fault_risk = fault_weights.get(predicted_fault, 20)
        risk_score += base_fault_risk * (0.6 + 0.4 * confidence)

        # 2. Health score inverse component
        health_penalty = (100.0 - health_score) * 0.4
        risk_score += health_penalty

        # 3. Active alert severity component
        critical_alerts_count = sum(1 for a in active_alerts if a.get("severity") == "CRITICAL")
        warning_alerts_count = sum(1 for a in active_alerts if a.get("severity") == "WARNING")

        risk_score += (critical_alerts_count * 15) + (warning_alerts_count * 5)

        # 4. History persistence check if history available
        persistence_note = ""
        if history and len(history) >= 3:
            recent_faults = [h.get("predicted_fault") for h in history[-5:] if h.get("predicted_fault")]
            abnormal_count = sum(1 for f in recent_faults if f != "Normal")
            if abnormal_count >= 3:
                risk_score += 10
                persistence_note = f" Persistent anomaly detected ({abnormal_count}/5 recent cycles abnormal)."

        risk_score = max(0, min(100, risk_score))

        if risk_score < 30:
            risk_level = "Low Risk"
            recommendation = "Normal mission profile approved. Continue standard automated monitoring."
        elif risk_score < 65:
            risk_level = "Medium Risk"
            recommendation = "Elevated risk detected. Recommend mission profile modification or return-to-base planning."
        else:
            risk_level = "High Risk"
            recommendation = "CRITICAL RISK: Immediate abort/precautionary landing recommended to prevent engine damage."

        reasons = []
        if predicted_fault != "Normal":
            reasons.append(f"Model predicted fault: {predicted_fault} ({confidence*100:.1f}% confidence)")
        if health_score < 80:
            reasons.append(f"Engine health score degraded to {health_score:.1f}/100")
        if critical_alerts_count > 0:
            reasons.append(f"{critical_alerts_count} critical sensor threshold violations active")
        if not reasons:
            reasons.append("All engine telemetry parameters operate within nominal thresholds")

        explanation = "; ".join(reasons) + "." + persistence_note

        return {
            "risk_level": risk_level,
            "risk_score": round(risk_score, 1),
            "recommendation": recommendation,
            "explanation": explanation
        }
