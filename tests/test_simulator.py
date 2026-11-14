import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulator.config import PARAMETER_BOUNDS, FAULT_CLASSES
from simulator.telemetry_generator import generate_record, get_fault_distribution, generate_dataset

def test_fault_distribution():
    dist = get_fault_distribution()
    assert len(dist) == len(FAULT_CLASSES)
    assert sum(dist.values()) == 20000

def test_generate_record_normal():
    record = generate_record("Normal")
    assert record["fault_type"] == "Normal"
    for param, (low, high) in PARAMETER_BOUNDS.items():
        assert low <= record[param] <= high, f"Parameter {param} value {record[param]} out of bounds [{low}, {high}]"

def test_generate_record_faults():
    for fault in FAULT_CLASSES:
        record = generate_record(fault)
        assert record["fault_type"] == fault
        assert "rpm" in record
        assert "oil_pressure" in record
        assert "cylinder_head_temperature" in record
