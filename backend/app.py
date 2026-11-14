import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from digital_twin.engine_twin import EngineDigitalTwin
from simulator.telemetry_generator import generate_record
from backend.db import init_db, log_telemetry_snapshot, fetch_telemetry_history, fetch_alerts_log, clear_db

# Initialize Digital Twin and simulation state
twin = EngineDigitalTwin(engine_id="UAV-ENGINE-001", model_type="rf")

# Load processed telemetry dataset for continuous replay mode
PROCESSED_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "engine_telemetry_processed.csv")
dataset_records = []
if os.path.exists(PROCESSED_DATA_PATH):
    try:
        dataset_records = pd.read_csv(PROCESSED_DATA_PATH).to_dict(orient="records")
        print(f"Loaded {len(dataset_records)} processed telemetry records for continuous dataset replay mode.")
    except Exception as e:
        print(f"Error loading dataset file: {e}")

simulation_state = {
    "is_running": True,
    "simulation_mode": "auto_cycle",  # "auto_cycle", "dataset_replay", "manual"
    "current_fault": "Normal",
    "mission_phase_text": "PHASE 1: NOMINAL UAV CLIMB & CRUISE",
    "step_interval": 1.0,
    "speed_multiplier": 1.0,
    "step_count": 0,
    "dataset_cursor": 0,
    "manual_rpm": None
}

async def simulation_loop():
    """
    Background loop that continuously streams simulated telemetry,
    updates the Digital Twin, and logs to SQLite.
    Supports Auto Scenario Cycling, Continuous Dataset Replay, and Manual Fault Injection.
    """
    while True:
        if simulation_state["is_running"]:
            try:
                mode = str(simulation_state["simulation_mode"])
                step = int(simulation_state["step_count"])

                if mode == "auto_cycle":
                    cycle_step = step % 65
                    if cycle_step < 20:
                        fault_type = "Normal"
                        phase_text = "PHASE 1: NOMINAL UAV CLIMB & CRUISE"
                    elif cycle_step < 35:
                        fault_type = "Overheating"
                        phase_text = "PHASE 2: THERMAL OVERHEATING STAGE (CHT ELEVATED)"
                    elif cycle_step < 50:
                        fault_type = "Lubrication Fault"
                        phase_text = "PHASE 3: LUBRICATION PRESSURE DROP (BEARING STARVATION)"
                    else:
                        fault_type = "Mechanical/Vibration Fault"
                        phase_text = "PHASE 4: MECHANICAL VIBRATION STRESS (ROD KNOCK)"

                    simulation_state["current_fault"] = fault_type
                    simulation_state["mission_phase_text"] = phase_text
                    record = generate_record(fault_type)

                elif mode == "dataset_replay" and dataset_records:
                    cursor = int(simulation_state["dataset_cursor"]) % len(dataset_records)
                    raw_rec = dataset_records[cursor]
                    fault_type = str(raw_rec.get("fault_type", "Normal"))
                    simulation_state["current_fault"] = fault_type
                    simulation_state["mission_phase_text"] = f"CONTINUOUS DATASET REPLAY (RECORD #{cursor + 1}/{len(dataset_records)})"
                    
                    feature_cols = [
                        "rpm", "oil_pressure", "oil_temperature", "cylinder_head_temperature",
                        "exhaust_gas_temperature", "fuel_flow", "manifold_pressure",
                        "vibration", "engine_load", "ambient_temperature"
                    ]
                    record = {col: float(raw_rec[col]) for col in feature_cols if col in raw_rec}
                    record["fault_type"] = fault_type
                    simulation_state["dataset_cursor"] = cursor + 1

                else:  # Manual Control Mode
                    fault_type = str(simulation_state["current_fault"])
                    simulation_state["mission_phase_text"] = f"MANUAL SCENARIO CONTROL: {fault_type.upper()}"
                    record = generate_record(fault_type)

                manual_rpm = simulation_state.get("manual_rpm")
                if manual_rpm is not None:
                    record["rpm"] = float(manual_rpm)
                record["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                record["engine_id"] = twin.engine_id

                snapshot = twin.update_telemetry(record)
                log_telemetry_snapshot(snapshot)
                simulation_state["step_count"] = step + 1
            except Exception as e:
                print(f"Error in simulation loop: {e}")

        speed = float(simulation_state.get("speed_multiplier", 1.0))
        interval = float(simulation_state.get("step_interval", 1.0)) / max(0.1, speed)
        await asyncio.sleep(interval)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    task = asyncio.create_task(simulation_loop())
    yield
    task.cancel()

app = FastAPI(
    title="UAV Aero Engine Digital Twin API",
    description="Real-time Digital Twin API for aero piston engine telemetry, fault prediction, health monitoring, and mission reliability risk indicator.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Request Models
class FaultSelection(BaseModel):
    fault_type: str

class ModeSelection(BaseModel):
    mode: str

class ModelSelection(BaseModel):
    model_type: str

class RpmSelection(BaseModel):
    rpm: float

class SpeedSelection(BaseModel):
    speed: float

class SimulationControl(BaseModel):
    interval: float = 1.0

# API Endpoints
@app.get("/api/health")
def get_health():
    return {
        "status": "online",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "simulation_running": simulation_state["is_running"],
        "simulation_mode": simulation_state["simulation_mode"],
        "mission_phase_text": simulation_state["mission_phase_text"],
        "active_fault_scenario": simulation_state["current_fault"],
        "active_model": twin.predictor.model_type,
        "step_count": simulation_state["step_count"],
        "manual_rpm": simulation_state["manual_rpm"],
        "speed_multiplier": simulation_state["speed_multiplier"]
    }

@app.get("/api/twin/current")
def get_current_twin_state():
    state = twin.get_current_state()
    state["simulation_mode"] = simulation_state["simulation_mode"]
    state["mission_phase_text"] = simulation_state["mission_phase_text"]
    return state

@app.get("/api/telemetry/latest")
def get_latest_telemetry():
    return {
        "timestamp": twin.latest_timestamp,
        "engine_id": twin.engine_id,
        "telemetry": twin.current_telemetry
    }

@app.get("/api/telemetry/history")
def get_telemetry_history(limit: int = 50):
    db_history = fetch_telemetry_history(limit=limit)
    if db_history:
        return db_history
    return twin.get_history(limit=limit)

@app.get("/api/prediction/latest")
def get_latest_prediction():
    return twin.latest_prediction

@app.get("/api/alerts")
def get_alerts(limit: int = 50):
    db_alerts = fetch_alerts_log(limit=limit)
    return {
        "active_alerts": twin.latest_health.get("alerts", []),
        "historical_alerts": db_alerts
    }

@app.get("/api/models/metrics")
def get_model_metrics():
    metrics_path = os.path.join(PROJECT_ROOT, "evaluation", "metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            return json.load(f)
    raise HTTPException(status_code=444, detail="Model evaluation metrics file not found. Run evaluation first.")

@app.post("/api/simulation/start")
def start_simulation():
    simulation_state["is_running"] = True
    return {"message": "Simulation started", "is_running": True}

@app.post("/api/simulation/pause")
def pause_simulation():
    simulation_state["is_running"] = False
    return {"message": "Simulation paused", "is_running": False}

@app.post("/api/simulation/resume")
def resume_simulation():
    simulation_state["is_running"] = True
    return {"message": "Simulation resumed", "is_running": True}

@app.post("/api/simulation/reset")
def reset_simulation():
    clear_db()
    twin.history.clear()
    simulation_state["step_count"] = 0
    simulation_state["dataset_cursor"] = 0
    simulation_state["is_running"] = True
    simulation_state["manual_rpm"] = None
    return {"message": "Simulation and database reset successfully"}

@app.post("/api/simulation/mode")
def set_simulation_mode(payload: ModeSelection):
    valid_modes = ["auto_cycle", "dataset_replay", "manual"]
    if payload.mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Invalid simulation mode. Must be one of {valid_modes}")
    simulation_state["simulation_mode"] = payload.mode
    return {"message": f"Simulation mode set to '{payload.mode}'", "mode": payload.mode}

@app.post("/api/simulation/rpm")
def set_manual_rpm(payload: RpmSelection):
    if payload.rpm < 500 or payload.rpm > 4000:
        raise HTTPException(status_code=400, detail="RPM must be between 500 and 4000.")
    simulation_state["manual_rpm"] = payload.rpm
    twin.current_telemetry["rpm"] = payload.rpm
    twin.update_telemetry(twin.current_telemetry)
    return {"message": f"Manual RPM set to {payload.rpm}", "rpm": payload.rpm}

@app.post("/api/simulation/speed")
def set_simulation_speed(payload: SpeedSelection):
    if payload.speed < 0.1 or payload.speed > 10.0:
        raise HTTPException(status_code=400, detail="Speed multiplier must be between 0.1 and 10.0.")
    simulation_state["speed_multiplier"] = payload.speed
    return {"message": f"Simulation speed multiplier set to {payload.speed}x", "speed": payload.speed}

@app.post("/api/simulation/fault")
def set_fault_scenario(payload: FaultSelection):
    valid_faults = ["Normal", "Overheating", "Lubrication Fault", "Mechanical/Vibration Fault"]
    if payload.fault_type not in valid_faults:
        raise HTTPException(status_code=400, detail=f"Invalid fault scenario. Must be one of {valid_faults}")
    simulation_state["current_fault"] = payload.fault_type
    simulation_state["simulation_mode"] = "manual"
    return {"message": f"Simulation fault scenario set to '{payload.fault_type}'", "current_fault": payload.fault_type}

@app.post("/api/model/select")
def select_model(payload: ModelSelection):
    try:
        twin.set_model(payload.model_type)
        return {"message": f"Active prediction model set to '{payload.model_type}'", "model_used": twin.predictor.model_type}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Static Files serving for Frontend
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
