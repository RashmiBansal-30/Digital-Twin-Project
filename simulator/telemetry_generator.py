import numpy as np
import pandas as pd

from config import NUM_RECORDS, FAULT_CLASSES, SIMULATION_PROFILES

def get_fault_distribution():
    records_per_fault = NUM_RECORDS // len(FAULT_CLASSES)
    
    distribution = {}
    
    for fault in FAULT_CLASSES:
        distribution[fault ] = records_per_fault
        
    return distribution

def generate_record(fault_type):
    profile = SIMULATION_PROFILES[fault_type]
    
    engine_load = np.random.normal(
        profile["engine_load"][0],
        profile["engine_load"][1]
    )
    
    engine_load = np.clip(engine_load, 10, 100)
    
    rpm = np.random.normal(
        profile["rpm"][0],
        profile["rpm"][1]
    )
    
    oil_pressure = np.random.normal(
        profile["oil_pressure"][0],
        profile["oil_pressure"][1]
    )
    
    oil_temperature = np.random.normal(
        profile["oil_temperature"][0],
        profile["oil_temperature"][1]
    )
    
    cylinder_head_temperature = np.random.normal(
        profile["cylinder_head_temperature"][0],
        profile["cylinder_head_temperature"][1]
    )
    
    exhaust_gas_temperature = np.random.normal(
        profile["exhaust_gas_temperature"][0],
        profile["exhaust_gas_temperature"][1]
    )
    
    vibration = np.random.normal(
        profile["vibration"][0],
        profile["vibration"][1]
    )
    
    ambient_temperature = np.random.normal(
        profile["ambient_temperature"][0],
        profile["ambient_temperature"][1]
    )
    
    # fuel flow increases with engine load
    fuel_flow = ( 5.0 + (engine_load * 0.05) + np.random.normal(0, 0.25))
    
    # Manifold pressure increases with engine load
    manifold_pressure = (0.45 + (engine_load * 0.005) + np.random.normal(0, 0.02))
    
    
    if fault_type == "Overheating":
        cylinder_head_temperature += 10
        oil_temperature += 5
        exhaust_gas_temperature += 15  
    elif fault_type == "Lubrication Fault":
        oil_pressure -= 0.5
        oil_temperature += 4
        vibration += 0.05
    elif fault_type == "Mechanical/Vibration Fault":
        vibration += 0.25
        rpm += np.random.normal(0, 100)
        
    return {
        "rpm": rpm,
        "oil_pressure": oil_pressure,
        "oil_temperature": oil_temperature,
        "cylinder_head_temperature": cylinder_head_temperature,
        "exhaust_gas_temperature": exhaust_gas_temperature,
        "fuel_flow": fuel_flow,
        "manifold_pressure": manifold_pressure,
        "vibration": vibration,
        "engine_load": engine_load,
        "ambient_temperature": ambient_temperature,
        "fault_type": fault_type
    }
    
def generate_dataset():
    records = []
    
    fault_distribution = get_fault_distribution()
    
    start_time = pd.Timestamp("2026-01-01 00:00:00")
    
    for fault_type, count in fault_distribution.items():
        for i in range(count):
            record = generate_record(fault_type)
            record["timestamp"] = start_time + pd.Timedelta(seconds=len(records))
            record["engine_id"] = "UAV-ENGINE-001"
            
            records.append(record)
        
    return pd.DataFrame(records)

if __name__ == "__main__":
    dataset = generate_dataset()
    
    output_path = "../data/raw/engine_telemetry.csv"
    dataset.to_csv(output_path, index=False)
    
    print("Dataset generated successfully!")
    print(f"Total records: {len(dataset)}")
    print(f"Saved to {output_path}")