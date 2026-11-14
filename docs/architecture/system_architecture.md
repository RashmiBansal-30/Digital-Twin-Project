# System Architecture: AI-Enabled Aero Piston Engine Digital Twin

## Executive Overview

This document details the software architecture of the AI-Enabled Real-Time Digital Twin System designed for health monitoring, fault prediction, and mission reliability enhancement of aero piston engines used in Medium-Altitude Long-Endurance (MALE) Unmanned Aerial Vehicles (UAVs).

```
 +---------------------------------------------------------------------------------+
 |                              SIMULATION ENGINE                                  |
 |  Real-Time Telemetry Generator (Normal, Overheating, Lubrication, Vibration)    |
 +----------------------------------------+----------------------------------------+
                                          |
                                          v
 +---------------------------------------------------------------------------------+
 |                               DIGITAL TWIN CORE                                 |
 |  +--------------------+   +-----------------------+   +----------------------+  |
 |  | Predictor (ML)     |   | Health Monitor (Rules)|   | Mission Reliability  |  |
 |  | SVM, RF, XGBoost   |   | Score: 0-100, Alerts  |   | Low / Medium / High  |  |
 |  +--------------------+   +-----------------------+   +----------------------+  |
 +----------------------------------------+----------------------------------------+
                                          |
                                          v
 +---------------------------------------------------------------------------------+
 |                           FASTAPI BACKEND & SQLITE                              |
 |  REST API Endpoints, Asynchronous Event Loop, Persistent Audit Database        |
 +----------------------------------------+----------------------------------------+
                                          |
                                          v
 +---------------------------------------------------------------------------------+
 |                          FRONTEND DASHBOARD CONSOLE                             |
 |  HTML5, Modern Dark CSS, Vanilla JS, Chart.js Real-time Telemetry Visualization |
 +---------------------------------------------------------------------------------+
```

## System Components

### 1. Telemetry Generator & Preprocessing Pipeline
- **Generator (`simulator/telemetry_generator.py`)**: Generates realistic synthetic 10-parameter aero piston engine telemetry with continuous stochastic variation and realistic parameter correlations.
- **Preprocessing (`preprocessing/preprocess.py`)**: Handles timestamp ordering, validation, missing value checks, and target label separation.

### 2. Machine Learning Inference Engine (`prediction/predictor.py`)
- **Trained Classifiers**:
  - Support Vector Machine (StandardScaler Pipeline)
  - Random Forest Classifier (100 Decision Trees)
  - XGBoost Gradient Boosted Classifier
  - Soft Voting Ensemble
- Predicts fault type (Normal, Overheating, Lubrication Fault, Mechanical/Vibration Fault) and outputs confidence probabilities.

### 3. Digital Twin Engine & Health Monitor (`digital_twin/`)
- **Engine Twin (`digital_twin/engine_twin.py`)**: Stateful object maintaining real-time telemetry, model predictions, health scores, active warnings, and rolling history.
- **Health Monitor (`digital_twin/health_monitor.py`)**: Evaluates parameter bounds and standard operational thresholds to assign a 0–100 health score and generate explainable alerts.
- **Reliability Evaluator (`digital_twin/reliability.py`)**: Computes Mission Risk Level (Low, Medium, High) based on fault predictions, health scores, alert severity, and anomaly persistence.

### 4. FastAPI Backend & SQLite (`backend/`)
- Asynchronous FastAPI web service providing REST endpoints for current twin state, telemetry stream, metrics, and simulation control (Start, Pause, Reset, Fault Scenario Selection).
- SQLite persistence (`data/telemetry.db`) storing audit logs for historical telemetry and health alerts.

### 5. Frontend Dashboard (`frontend/`)
- Interactive web dashboard created with HTML5, CSS3, Vanilla JavaScript, and Chart.js.
- Dark theme styled as a professional aerospace engine monitoring console.

## Academic Disclaimer
This system is a software-only academic simulation developed for research and demonstration purposes. All telemetry data and operational thresholds represent simulation assumptions and are not flight-certified for real aircraft operations.
