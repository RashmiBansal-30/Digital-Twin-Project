import pandas as pd

DATASET_PATH = "../data/raw/engine_telemetry.csv"

def load_dataset():
    dataset = pd.read_csv(DATASET_PATH)
    
    print("Dataset loaded successfully!")
    print(f"Rows: {len(dataset)}")
    print(f"Columns: {len(dataset.columns)}")
    
    return dataset

def validate_structure(dataset):
    print("\n---- COLUMN CHECK ----")
    print(dataset.columns.tolist())
    
    print("\n---- MISSING VALUES CHECK -----")
    print(dataset.isnull().sum())

def validate_fault_distribution(dataset):
    print("\n---- FAULT DISTRIBUTION ----")
    fault_counts = dataset["fault_type"].value_counts()
    print(fault_counts)
    
def validate_duplicates(dataset):
    print("\n---- DUPLIcATE CHECK ----")
    duplicate_count = dataset.duplicated().sum()
    print(f"Duplicate rows: {duplicate_count}")
    
def validate_data_types(dataset):
    print("\n---- DATA TYPES ----")
    print(dataset.dtypes)

if __name__ == "__main__":
    dataset = load_dataset()
    
    validate_structure(dataset)
    validate_fault_distribution(dataset)
    
    validate_duplicates(dataset)
    validate_data_types(dataset)