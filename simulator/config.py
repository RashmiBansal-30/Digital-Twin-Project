NUM_RECORDS = 20000 # Number of telemetry records to generate

FAULT_CLASSES = [
    "Normal",
    "Overheating",
    "Lubrication Fault",
    "Mechanical/Vibration Fault"
]

ENGINE_PARAMETERS = [
    "rpm",
    "oil_pressure",
    "oil_temperature",
    "cylinder_head_temperature",
    "exhaust_gas_temperature",
    "fuel_flow",
    "manifold_pressure",
    "vibration",
    "engine_load",
    "ambient_temperature"
]

SIMULATION_PROFILES = {
    
    "Normal": {
        "rpm": (2800, 100),
        "oil_pressure": (4.2, 0.25),
        "oil_temperature": (90, 5),
        "cylinder_head_temperature": (170, 8),
        "exhaust_gas_temperature": (620, 25),
        "fuel_flow": (8.5, 0.5),
        "manifold_pressure": (0.85, 0.05),
        "vibration": (0.25, 0.05),
        "engine_load": (70, 8),
        "ambient_temperature": (25, 5)
    },
    
    "Overheating": {
            "rpm": (2700, 140),
            "oil_pressure": (3.9, 0.30),
            "oil_temperature": (105, 8),
            "cylinder_head_temperature": (205, 12),
            "exhaust_gas_temperature": (690, 30),
            "fuel_flow": (9.0, 0.7),
            "manifold_pressure": (0.80, 0.07),
            "vibration": (0.38, 0.08),
            "engine_load": (78, 10),
            "ambient_temperature": (25, 5)
        },
    
    "Lubrication Fault": {
            "rpm": (2600, 160),
            "oil_pressure": (2.8, 0.40),
            "oil_temperature": (100, 8),
            "cylinder_head_temperature": (185, 10),
            "exhaust_gas_temperature": (650, 30),
            "fuel_flow": (7.8, 0.8),
            "manifold_pressure": (0.72, 0.08),
            "vibration": (0.45, 0.10),
            "engine_load": (65, 12),
            "ambient_temperature": (25, 5)
        },
    
    "Mechanical/Vibration Fault": {
            "rpm": (2750, 180),
            "oil_pressure": (3.7, 0.40),
            "oil_temperature": (94, 7),
            "cylinder_head_temperature": (180, 12),
            "exhaust_gas_temperature": (640, 40),
            "fuel_flow": (8.4, 0.9),
            "manifold_pressure": (0.78, 0.09),
            "vibration": (0.75, 0.15),
            "engine_load": (75, 15),
            "ambient_temperature": (25, 5)
        },
}