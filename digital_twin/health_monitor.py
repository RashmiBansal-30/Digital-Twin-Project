import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulator.config import PARAMETER_BOUNDS

class HealthMonitor:
    """
    Evaluates telemetry features to compute an engine Health Score (0-100),
    health status (Healthy, Warning, Critical), and explainable health alerts.
    """
    def __init__(self):
        # Nominal reference ranges for piston engine
        self.thresholds = {
            "cylinder_head_temperature": {"warning": 190.0, "critical": 210.0, "max_nominal": 180.0},
            "oil_temperature": {"warning": 102.0, "critical": 112.0, "max_nominal": 95.0},
            "oil_pressure": {"warning_low": 3.2, "critical_low": 2.2, "min_nominal": 4.0},
            "vibration": {"warning": 0.45, "critical": 0.70, "max_nominal": 0.30},
            "exhaust_gas_temperature": {"warning": 670.0, "critical": 720.0, "max_nominal": 640.0}
        }

    def evaluate(self, telemetry):
        """
        Evaluates current telemetry data.
        Returns health_score (float), health_status (str), and alerts (list of dicts).
        """
        health_score = 100.0
        alerts = []

        cht = telemetry.get("cylinder_head_temperature", 170.0)
        if cht >= self.thresholds["cylinder_head_temperature"]["critical"]:
            penalty = 35.0
            health_score -= penalty
            alerts.append({
                "severity": "CRITICAL",
                "parameter": "cylinder_head_temperature",
                "value": round(cht, 1),
                "message": f"Critical Cylinder Head Temp ({cht:.1f}°C >= {self.thresholds['cylinder_head_temperature']['critical']}°C limit)"
            })
        elif cht >= self.thresholds["cylinder_head_temperature"]["warning"]:
            penalty = 15.0
            health_score -= penalty
            alerts.append({
                "severity": "WARNING",
                "parameter": "cylinder_head_temperature",
                "value": round(cht, 1),
                "message": f"Elevated Cylinder Head Temp ({cht:.1f}°C >= {self.thresholds['cylinder_head_temperature']['warning']}°C threshold)"
            })

        oil_temp = telemetry.get("oil_temperature", 90.0)
        if oil_temp >= self.thresholds["oil_temperature"]["critical"]:
            penalty = 30.0
            health_score -= penalty
            alerts.append({
                "severity": "CRITICAL",
                "parameter": "oil_temperature",
                "value": round(oil_temp, 1),
                "message": f"Critical Oil Temperature ({oil_temp:.1f}°C >= {self.thresholds['oil_temperature']['critical']}°C limit)"
            })
        elif oil_temp >= self.thresholds["oil_temperature"]["warning"]:
            penalty = 15.0
            health_score -= penalty
            alerts.append({
                "severity": "WARNING",
                "parameter": "oil_temperature",
                "value": round(oil_temp, 1),
                "message": f"Elevated Oil Temperature ({oil_temp:.1f}°C >= {self.thresholds['oil_temperature']['warning']}°C threshold)"
            })

        oil_press = telemetry.get("oil_pressure", 4.2)
        if oil_press <= self.thresholds["oil_pressure"]["critical_low"]:
            penalty = 40.0
            health_score -= penalty
            alerts.append({
                "severity": "CRITICAL",
                "parameter": "oil_pressure",
                "value": round(oil_press, 2),
                "message": f"Critically Low Oil Pressure ({oil_press:.2f} bar <= {self.thresholds['oil_pressure']['critical_low']} bar limit)"
            })
        elif oil_press <= self.thresholds["oil_pressure"]["warning_low"]:
            penalty = 20.0
            health_score -= penalty
            alerts.append({
                "severity": "WARNING",
                "parameter": "oil_pressure",
                "value": round(oil_press, 2),
                "message": f"Low Oil Pressure Warning ({oil_press:.2f} bar <= {self.thresholds['oil_pressure']['warning_low']} bar threshold)"
            })

        vib = telemetry.get("vibration", 0.25)
        if vib >= self.thresholds["vibration"]["critical"]:
            penalty = 35.0
            health_score -= penalty
            alerts.append({
                "severity": "CRITICAL",
                "parameter": "vibration",
                "value": round(vib, 2),
                "message": f"Excessive Engine Vibration ({vib:.2f} g >= {self.thresholds['vibration']['critical']} g limit)"
            })
        elif vib >= self.thresholds["vibration"]["warning"]:
            penalty = 15.0
            health_score -= penalty
            alerts.append({
                "severity": "WARNING",
                "parameter": "vibration",
                "value": round(vib, 2),
                "message": f"Elevated Engine Vibration ({vib:.2f} g >= {self.thresholds['vibration']['warning']} g threshold)"
            })

        egt = telemetry.get("exhaust_gas_temperature", 620.0)
        if egt >= self.thresholds["exhaust_gas_temperature"]["critical"]:
            penalty = 25.0
            health_score -= penalty
            alerts.append({
                "severity": "CRITICAL",
                "parameter": "exhaust_gas_temperature",
                "value": round(egt, 1),
                "message": f"Critical Exhaust Gas Temp ({egt:.1f}°C >= {self.thresholds['exhaust_gas_temperature']['critical']}°C limit)"
            })
        elif egt >= self.thresholds["exhaust_gas_temperature"]["warning"]:
            penalty = 10.0
            health_score -= penalty
            alerts.append({
                "severity": "WARNING",
                "parameter": "exhaust_gas_temperature",
                "value": round(egt, 1),
                "message": f"Elevated Exhaust Gas Temp ({egt:.1f}°C >= {self.thresholds['exhaust_gas_temperature']['warning']}°C threshold)"
            })

        health_score = max(0.0, min(100.0, health_score))

        if health_score >= 80.0:
            health_status = "Healthy"
        elif health_score >= 50.0:
            health_status = "Warning"
        else:
            health_status = "Critical"

        return {
            "health_score": round(health_score, 1),
            "health_status": health_status,
            "alerts": alerts
        }
