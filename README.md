# AI-Enabled Real-Time Digital Twin System for UAV Aero Piston Engine Health Monitoring & Fault Prediction

An end-to-end software AI-enabled Digital Twin system designed for real-time telemetry streaming, fault detection, health monitoring, and mission reliability risk estimation of aero piston engines used in MALE UAVs.

---

## Key Features

- **Real-Time Telemetry Simulation Engine**: Generates continuous 10-parameter engine telemetry records with realistic parameter dependencies and custom fault injection scenarios (*Normal*, *Overheating*, *Lubrication Fault*, *Mechanical/Vibration Fault*).
- **Machine Learning Inference Engine**: Includes Support Vector Machine (SVM), Random Forest, XGBoost, and Soft Voting Ensemble classifiers trained on 20,000 engine telemetry records.
- **Digital Twin State Core**: Maintains real-time virtual engine state, continuous health scoring (0–100), automated parameter alert generation, and rolling history tracking.
- **Mission Reliability & Risk Evaluator**: Calculates qualitative and numeric mission risk indicators (*Low Risk*, *Medium Risk*, *High Risk*) with operational recommendations and transparent explainability notes.
- **FastAPI Backend & SQLite Persistence**: Asynchronous Python REST API providing complete digital twin endpoints and persistent SQLite audit logging.
- **Aerospace Monitoring Web Console**: Dark-themed responsive dashboard built with HTML5, CSS3, Vanilla JavaScript, and Chart.js featuring real-time telemetry line charts, virtual subsystem status indicators, active alert logs, model comparison benchmarks, and simulation controls.
- **Automated Testing Suite**: Built-in `pytest` suite covering simulation generation, model inference, health monitoring, mission risk evaluation, and API endpoints.

---

## Project Structure

```text
UAV-Engine-Digital-Twin/
├── README.md                          # Project documentation and quickstart guide
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git ignore rules
├── data/
│   ├── raw/                           # Raw synthetic telemetry dataset (20,000 records)
│   └── processed/                     # Preprocessed dataset
├── simulator/
│   ├── config.py                      # Simulation bounds & fault profiles
│   ├── telemetry_generator.py         # Telemetry record & dataset generator
│   └── validate_dataset.py            # Dataset structure & integrity validator
├── preprocessing/
│   └── preprocess.py                  # Preprocessing script
├── models/
│   ├── train_svm.py                   # SVM training pipeline with StandardScaler
│   ├── train_random_forest.py         # Random Forest classifier training
│   ├── train_xgboost.py               # XGBoost classifier training with LabelEncoder
│   └── ensemble.py                    # Soft Voting Ensemble classifier
├── saved_models/                      # Trained model joblib artifacts
├── evaluation/
│   ├── evaluate_models.py             # Evaluation & plotting script
│   ├── metrics.json                   # Structured classification metrics
│   └── plots/                         # Comparison charts, confusion matrices & feature importance plots
├── prediction/
│   └── predictor.py                   # Inference engine wrapper
├── digital_twin/
│   ├── engine_twin.py                 # Core Digital Twin virtual engine state
│   ├── health_monitor.py              # Rule-based health score & alert engine
│   └── reliability.py                 # Mission reliability & risk evaluator
├── backend/
│   ├── app.py                         # FastAPI web application & background streaming loop
│   └── db.py                          # SQLite database schema and log management
├── frontend/
│   ├── index.html                     # Main dashboard console HTML
│   ├── css/
│   │   └── style.css                  # Aerospace dark theme stylesheet
│   └── js/
│       └── script.js                  # Frontend state management & Chart.js rendering
├── tests/                             # Automated pytest test suite
│   ├── test_simulator.py
│   ├── test_prediction.py
│   ├── test_digital_twin.py
│   └── test_backend.py
└── docs/                              # Project documentation
    ├── architecture/                  # System architecture specifications
    ├── research/                      # Dataset & parameter definitions
    └── report/                        # Evaluation report & benchmarks
```

---

## Quickstart Guide

### 1. Prerequisites & Installation

Ensure Python 3.9+ is installed. Clone the repository and install required dependencies:

```bash
pip install -r requirements.txt
```

### 2. Preprocessing & Model Training

To preprocess dataset and train all machine learning classifiers:

```bash
# 1. Run Preprocessing
python preprocessing/preprocess.py

# 2. Train Models and Run Evaluation Pipeline
python evaluation/evaluate_models.py
```

This generates trained model artifacts in `saved_models/`, metrics in `evaluation/metrics.json`, and performance plots in `evaluation/plots/`.

### 3. Running Automated Tests

Run the full pytest suite to verify all system components:

```bash
pytest tests/
```

### 4. Launching the Digital Twin Dashboard & API Server

Start the FastAPI application and backend streaming loop:

```bash
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

Open your web browser and navigate to:

- **Dashboard UI**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive API Documentation (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## API Endpoints Summary

- `GET /api/health` — Backend health check and simulation state.
- `GET /api/twin/current` — Current Digital Twin state (telemetry, prediction, health score, active alerts, mission risk level).
- `GET /api/telemetry/latest` — Latest raw engine telemetry record.
- `GET /api/telemetry/history` — Recent telemetry history logs.
- `GET /api/prediction/latest` — Latest fault prediction output.
- `GET /api/alerts` — Active parameter threshold warnings and logged alert history.
- `GET /api/models/metrics` — Model benchmark evaluation results.
- `POST /api/simulation/start` — Start real-time telemetry streaming.
- `POST /api/simulation/pause` — Pause real-time telemetry streaming.
- `POST /api/simulation/reset` — Reset simulation history and clear database.
- `POST /api/simulation/fault` — Set current simulation fault scenario (`Normal`, `Overheating`, `Lubrication Fault`, `Mechanical/Vibration Fault`).
- `POST /api/model/select` — Change active ML prediction model (`rf`, `svm`, `xgboost`, `ensemble`).

---

## Academic Disclaimer

This software-only application is developed solely for academic research and educational demonstration. Telemetry data is generated by a mathematical simulation model. Thresholds and risk scores are project-defined assumptions and are not flight-certified or approved for physical aircraft safety operations.
