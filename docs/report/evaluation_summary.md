# Machine Learning Model Evaluation Report

## Model Benchmarks on Synthetic Telemetry Test Set (4,000 samples)

| Model Architecture | Accuracy | Precision (Macro) | Recall (Macro) | F1 Score (Macro) |
|---|---|---|---|---|
| **Random Forest** | **99.68%** | **99.68%** | **99.68%** | **99.68%** |
| **Support Vector Machine (SVM)** | 99.65% | 99.65% | 99.65% | 99.65% |
| **XGBoost Classifier** | 99.58% | 99.58% | 99.57% | 99.58% |

## Key Findings & Feature Importances
- Tree-based models (Random Forest and XGBoost) demonstrate high discriminative performance on synthetic telemetry patterns.
- The top predictive features identified across tree models are:
  1. `vibration` (Primary indicator for Mechanical/Vibration Fault)
  2. `cylinder_head_temperature` (Primary indicator for Overheating)
  3. `oil_pressure` (Primary indicator for Lubrication Fault)
  4. `oil_temperature` (Secondary indicator for thermal and lubrication degradation)

## Limitations & Disclaimer
High classification metrics are expected when evaluating models trained on synthetic simulation data generated from defined mathematical distributions. These high scores reflect model fidelity to the synthetic generator rules and do not demonstrate real-world physical flight safety certification.
