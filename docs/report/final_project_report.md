# AI-Enabled Real-Time Digital Twin System for Health Monitoring, Fault Prediction and Mission Reliability Enhancement of Aero Piston Engines Used in MALE UAVs

## Project Information
- **Project Title**: AI-Enabled Real-Time Digital Twin System for Health Monitoring, Fault Prediction and Mission Reliability Enhancement of Aero Piston Engines Used in MALE UAVs
- **Application Domain**: UAV Aerospace Systems / Predictive Health Monitoring / Mechanical Digital Twins
- **Technology Stack**: Python 3, Pandas, NumPy, Scikit-learn, XGBoost, Joblib, FastAPI, Uvicorn, SQLite, Three.js, HTML5, CSS3, Vanilla JavaScript, Chart.js

---

## 1. Executive Summary

This project delivers a software-only, AI-enabled Digital Twin system designed to monitor engine health, predict potential mechanical and thermal faults, and provide a mission-reliability risk indicator for aero piston engines used in Medium-Altitude Long-Endurance (MALE) Unmanned Aerial Vehicles (UAVs).

The system integrates real-time telemetry generation, machine learning inference (SVM, Random Forest, XGBoost, and Soft Voting Ensemble), rule-based health monitoring (0–100 score with explainable alert rules), qualitative mission reliability risk classification (*Low Risk*, *Medium Risk*, *High Risk*), asynchronous REST API endpoints (FastAPI), SQLite audit persistence, and an interactive 3D WebGL aerospace monitoring console featuring a cutaway Inline-4 DOHC engine model with animated piston kinetics and thermal fault highlights.

---

## 2. Problem Statement & Academic Objectives

### Problem Statement
In MALE UAV flight operations, engine failures during long-duration missions pose critical risks to flight safety and payload security. Conventional threshold telemetry alerts often detect failures only after physical damage has occurred. A real-time Digital Twin model capable of continuous health scoring, multi-class fault prediction, and mission risk evaluation enables early proactive intervention.

### Core Objectives
1. **Telemetry Simulation**: Simulate realistic aero piston engine telemetry across 10 core parameters (*RPM, Oil Pressure, Oil Temperature, Cylinder Head Temperature, Exhaust Gas Temperature, Fuel Flow, Manifold Pressure, Vibration, Engine Load, Ambient Temperature*).
2. **Machine Learning Fault Classification**: Train and benchmark multi-class classifiers to predict 4 operational states (*Normal*, *Overheating*, *Lubrication Fault*, *Mechanical/Vibration Fault*).
3. **Digital Twin Core**: Maintain a stateful virtual engine model updating in real-time with health scoring (0–100) and mission risk indicators (*Low*, *Medium*, *High*).
4. **Interactive 3D Visualization**: Render a 3D WebGL cutaway aero piston engine with animated crankshaft/piston kinetics, 1-3-4-2 firing ignition sequence, and subsystem root-cause fault visualizers.
5. **Backend & Dashboard**: Provide an asynchronous FastAPI backend service with persistent SQLite logging and a responsive dark-themed monitoring console.

---

## 3. Dataset & Preprocessing Pipeline

- **Dataset Size**: 20,000 telemetry records (5,000 records per fault class).
- **Target Variable**: `fault_type` (*Normal*, *Overheating*, *Lubrication Fault*, *Mechanical/Vibration Fault*).
- **Numerical Features (10 parameters)**:

| Feature Name | Symbol | Unit | Nominal Operating Bounds | Fault Threshold Limit |
|---|---|---|---|---|
| Engine Speed | `rpm` | RPM | 2600 - 2900 | < 1800 or > 3600 |
| Oil Pressure | `oil_pressure` | bar | 3.5 - 4.5 | Critical < 2.2 bar |
| Oil Temperature | `oil_temperature` | °C | 85 - 95 | Critical > 112 °C |
| Cylinder Head Temp | `cylinder_head_temperature` | °C | 160 - 180 | Critical > 210 °C |
| Exhaust Gas Temp | `exhaust_gas_temperature` | °C | 600 - 640 | Critical > 720 °C |
| Fuel Flow | `fuel_flow` | L/h | 7.5 - 9.5 | 5.0 - 11.0 |
| Manifold Pressure | `manifold_pressure` | bar | 0.80 - 0.90 | 0.50 - 1.05 |
| Vibration Level | `vibration` | g | 0.20 - 0.30 | Critical > 0.70 g |
| Engine Load | `engine_load` | % | 60 - 80 | 10 - 100 % |
| Ambient Temp | `ambient_temperature` | °C | 20 - 30 | 10 - 40 °C |

- **Preprocessing**: `preprocessing/preprocess.py` handles datetime timestamp ordering, missing value verification, feature matrix $X$ extraction, and target $y$ label encoding.

---

## 4. Machine Learning Benchmarks

Four independent model architectures were trained on 80% training data and evaluated on a separate stratified 20% test split (4,000 records):

| Model Architecture | Accuracy | Precision (Macro) | Recall (Macro) | F1-Score (Macro) | Key Strengths |
|---|---|---|---|---|---|
| **Random Forest (100 Trees)** | **99.68%** | **99.68%** | **99.68%** | **99.68%** | Superior non-linear decision boundaries; robust to parameter variance. |
| **Support Vector Machine (SVM)** | 99.65% | 99.65% | 99.65% | 99.65% | Scaled via Scikit-learn Pipeline (`StandardScaler`); strong margin separation. |
| **XGBoost Classifier** | 99.58% | 99.58% | 99.57% | 99.58% | Gradient boosted decision trees with `LabelEncoder` target handling. |
| **Soft Voting Ensemble** | 99.68% | 99.68% | 99.68% | 99.68% | Combined probability distribution averaging across SVM, RF, and XGBoost. |

### Top Discriminative Features Identified
1. `vibration` (Primary indicator for Mechanical/Vibration Fault)
2. `cylinder_head_temperature` (Primary indicator for Thermal Overheating)
3. `oil_pressure` (Primary indicator for Lubrication Starvation)
4. `oil_temperature` (Secondary thermal & lubrication degradation signal)

---

## 5. Digital Twin Core & Health Analytics

### A. Health Monitoring Engine (`digital_twin/health_monitor.py`)
- Evaluates parameter deviations from nominal limits to compute a transparent **Health Score (0–100)**:
  - **Healthy (80–100)**: Nominal operational state.
  - **Warning (50–79)**: Minor parameter degradation; warning alerts issued.
  - **Critical (< 50)**: Severe threshold breach; immediate attention required.

### B. Mission Reliability & Risk Evaluator (`digital_twin/reliability.py`)
- Calculates a qualitative **Mission Risk Indicator**:
  - **Low Risk**: Normal mission profile approved.
  - **Medium Risk**: Elevated risk detected; recommend mission profile modification or return-to-base planning.
  - **High Risk**: CRITICAL RISK: Immediate abort / precautionary landing recommended.
- Combines predicted fault class, model confidence score, health score penalties, active alert counts, and anomaly persistence over recent cycles.

---

## 6. Interactive 3D Engine Model & Mechanical Kinetics

### A. 3D WebGL Architecture (`frontend/js/engine3d.js`)
- Constructed a **4-Cylinder Inline DOHC Cutaway Aero Engine** in Three.js:
  - **Semi-Transparent Cutaway Cylinders**: Glass sleeves revealing internal reciprocating pistons, ring grooves, and wrist pins.
  - **Counterweighted Crankshaft & Flywheel**: 4-throw offset crankshaft, main bearing journals, counterweights, and ring-gear flywheel.
  - **Dual Overhead Camshafts (DOHC) & Valves**: Twin camshafts with 8 cam lobes depressing poppet valves in synchronization.
  - **1-3-4-2 Ignition Sequence**: Combustion chamber flashes sequentially at Top Dead Center (TDC).

### B. Subsystem Fault Differentiation
- **Overheating**: Cylinder heads and exhaust manifold glow in fiery yellow-orange (`#ffaa00`), matching physical thermal accumulation.
- **Lubrication Fault**: Crankshaft main journals and oil sump illuminate in amber warning light (`#eab308`).
- **Mechanical/Vibration Fault**: Connecting rod caps flash in warning red with physical mechanical vibration oscillation applied to the engine block.

---

## 7. System Architecture & Component Diagram

```text
 +---------------------------------------------------------------------------------+
 |                              SIMULATION ENGINE                                  |
 |  Auto Mission Cycling | Continuous Dataset Replay | Manual Fault Injection     |
 +----------------------------------------+----------------------------------------+
                                          |
                                          v
 +---------------------------------------------------------------------------------+
 |                               DIGITAL TWIN CORE                                 |
 |  +--------------------+   +-----------------------+   +----------------------+  |
 |  | Predictor Engine   |   | Health Monitor (Rules)|   | Mission Reliability  |  |
 |  | SVM, RF, XGB, Ens  |   | Health Score (0-100)  |   | Low / Medium / High  |  |
 |  +--------------------+   +-----------------------+   +----------------------+  |
 +----------------------------------------+----------------------------------------+
                                          |
                                          v
 +---------------------------------------------------------------------------------+
 |                         FASTAPI BACKEND & SQLITE DB                             |
 |  Asynchronous Event Loop, REST API Endpoints, SQLite Audit Logging              |
 +----------------------------------------+----------------------------------------+
                                          |
                                          v
 +---------------------------------------------------------------------------------+
 |                         AEROSPACE DASHBOARD CONSOLE                             |
 |  Three.js 3D Viewport | Chart.js Telemetry Graphs | Subsystem Root-Cause Panel   |
 +---------------------------------------------------------------------------------+
```

---

## 8. Automated Testing & Verification

- **Test Suite (`pytest tests/`)**:
  - `test_simulator.py`: Telemetry generation & bounds checking.
  - `test_prediction.py`: ML model artifact loading & inference correctness.
  - `test_digital_twin.py`: Health score ranges, alert rules & mission risk calculation.
  - `test_backend.py`: FastAPI endpoints, simulation controls, speed multipliers, and streaming modes.
- **Result**: **14 / 14 unit and integration tests passed (`1.31s`)**.

---

## 9. Academic & Operational Disclaimer

This software application is developed solely for academic research and educational demonstration. All telemetry data is generated by an academic simulation model. Operating limits, health scores, and mission risk indicators are project-defined assumptions and are **not flight-certified or approved for real aircraft operations**.
