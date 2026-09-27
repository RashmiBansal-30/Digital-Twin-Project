import pandas as pd

INPUT_PATH = "../data/raw/engine_telemetry.csv"
OUTPUT_PATH = "../data/processed/engine_telemetry_processed.csv"

def load_dataset():
    dataset = pd.read_csv(INPUT_PATH)
    return dataset

def preprocess_dataset(dataset):
    # String timestamp -> datetime
    dataset["timestamp"] = pd.to_datetime(dataset["timestamp"])
    
    dataset = dataset.sort_values("timestamp").reset_index(drop=True)
    
    if dataset.isnull().sum().sum() > 0:
        print("Warning: Missing values found.")
        dataset = dataset.dropna()
    
    return dataset

def separate_features_target(dataset):
    feature_columns = [
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
    
    X = dataset[feature_columns]
    y = dataset["fault_type"]
    
    return X, y

if __name__ == "__main__":
    print("Loading dataset...")
    dataset = load_dataset()
    
    print(f"Original rows: {len(dataset)}")
    print(f"Original columns: {len(dataset.columns)}")
    
    print("\nPreprocessing dataset...")
    
    dataset = preprocess_dataset(dataset)
    
    X, y = separate_features_target(dataset)
    
    dataset.to_csv(OUTPUT_PATH, index=False)
    
    print(f"Processed rows: {len(dataset)}")
    print(f"Processed columns: {len(dataset.columns)}")
    
    print("\nFeature shape:")
    print(X.shape)
    
    print("\nTarget distribution:")
    print(y.value_counts())
    
    print(f"\nProcessed dataset saved to: {OUTPUT_PATH}")