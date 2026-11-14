import sys
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import app

client = TestClient(app)

def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

def test_api_twin_current():
    response = client.get("/api/twin/current")
    assert response.status_code == 200
    data = response.json()
    assert "telemetry" in data
    assert "prediction" in data
    assert "health" in data
    assert "reliability" in data

def test_simulation_controls():
    pause_res = client.post("/api/simulation/pause")
    assert pause_res.status_code == 200
    assert pause_res.json()["is_running"] is False

    resume_res = client.post("/api/simulation/resume")
    assert resume_res.status_code == 200
    assert resume_res.json()["is_running"] is True

    rpm_res = client.post("/api/simulation/rpm", json={"rpm": 3200.0})
    assert rpm_res.status_code == 200
    assert rpm_res.json()["rpm"] == 3200.0

    speed_res = client.post("/api/simulation/speed", json={"speed": 2.0})
    assert speed_res.status_code == 200
    assert speed_res.json()["speed"] == 2.0

def test_fault_scenario_selection():
    mode_res = client.post("/api/simulation/mode", json={"mode": "auto_cycle"})
    assert mode_res.status_code == 200
    assert mode_res.json()["mode"] == "auto_cycle"

    fault_res = client.post("/api/simulation/fault", json={"fault_type": "Overheating"})
    assert fault_res.status_code == 200
    assert fault_res.json()["current_fault"] == "Overheating"

def test_model_selection():
    model_res = client.post("/api/model/select", json={"model_type": "rf"})
    assert model_res.status_code == 200
    assert model_res.json()["model_used"] == "rf"
