# Aero Engine Telemetry Dataset Specification

## Overview
The dataset contains 20,000 synthetic telemetry records generated for a four-cylinder aero piston engine suitable for MALE UAV applications. The dataset features 10 numerical telemetry parameters and 1 categorical fault target variable.

## Telemetry Parameters & Simulation Bounds

| Parameter Name | Symbol | Unit | Nominal Range | Simulation Bounds | Description |
|---|---|---|---|---|---|
| Engine Speed | `rpm` | RPM | 2600 - 2900 | 1800 - 3600 | Engine crankshaft rotations per minute |
| Oil Pressure | `oil_pressure` | bar | 3.5 - 4.5 | 1.5 - 5.5 | Lubrication system pressure |
| Oil Temperature | `oil_temperature` | °C | 85 - 95 | 70 - 130 | Lubricating oil operating temperature |
| Cylinder Head Temp | `cylinder_head_temperature` | °C | 160 - 180 | 130 - 240 | Cylinder head thermal measurement |
| Exhaust Gas Temp | `exhaust_gas_temperature` | °C | 600 - 640 | 500 - 800 | Exhaust gas thermal measurement |
| Fuel Flow | `fuel_flow` | L/h | 7.5 - 9.5 | 5.0 - 11.0 | Engine fuel consumption rate |
| Manifold Pressure | `manifold_pressure` | bar | 0.80 - 0.90 | 0.50 - 1.05 | Intake manifold absolute pressure |
| Vibration Level | `vibration` | g | 0.20 - 0.30 | 0.05 - 1.20 | Structural vibration amplitude |
| Engine Load | `engine_load` | % | 60 - 80 | 10 - 100 | Calculated engine percentage load |
| Ambient Temperature | `ambient_temperature` | °C | 20 - 30 | 10 - 40 | Ambient atmospheric temperature |

## Target Fault Classes (Balanced 5,000 samples each)
1. **Normal**: All parameters within nominal operating distributions.
2. **Overheating**: Characterized by elevated Cylinder Head Temp (>205°C), Oil Temp (>105°C), and EGT (>690°C).
3. **Lubrication Fault**: Characterized by dropped Oil Pressure (<2.8 bar) and elevated Oil Temp (>100°C).
4. **Mechanical/Vibration Fault**: Characterized by elevated vibration (>0.75 g) and RPM fluctuations.
