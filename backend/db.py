import os
import sys
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = os.path.join(PROJECT_ROOT, "data", "telemetry.db")

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telemetry_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        engine_id TEXT NOT NULL,
        rpm REAL,
        oil_pressure REAL,
        oil_temperature REAL,
        cylinder_head_temperature REAL,
        exhaust_gas_temperature REAL,
        fuel_flow REAL,
        manifold_pressure REAL,
        vibration REAL,
        engine_load REAL,
        ambient_temperature REAL,
        predicted_fault TEXT,
        confidence REAL,
        health_score REAL,
        risk_level TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        engine_id TEXT NOT NULL,
        severity TEXT NOT NULL,
        parameter TEXT NOT NULL,
        value REAL,
        message TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def log_telemetry_snapshot(snapshot):
    conn = get_db_connection()
    cursor = conn.cursor()

    telemetry = snapshot.get("telemetry", {})
    prediction = snapshot.get("prediction", {})
    health = snapshot.get("health", {})
    reliability = snapshot.get("reliability", {})
    timestamp = snapshot.get("timestamp")
    engine_id = snapshot.get("engine_id", "UAV-ENGINE-001")

    cursor.execute("""
    INSERT INTO telemetry_history (
        timestamp, engine_id, rpm, oil_pressure, oil_temperature,
        cylinder_head_temperature, exhaust_gas_temperature, fuel_flow,
        manifold_pressure, vibration, engine_load, ambient_temperature,
        predicted_fault, confidence, health_score, risk_level
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp, engine_id,
        telemetry.get("rpm"), telemetry.get("oil_pressure"), telemetry.get("oil_temperature"),
        telemetry.get("cylinder_head_temperature"), telemetry.get("exhaust_gas_temperature"),
        telemetry.get("fuel_flow"), telemetry.get("manifold_pressure"),
        telemetry.get("vibration"), telemetry.get("engine_load"),
        telemetry.get("ambient_temperature"),
        prediction.get("predicted_fault"), prediction.get("confidence"),
        health.get("health_score"), reliability.get("risk_level")
    ))

    for alert in health.get("alerts", []):
        cursor.execute("""
        INSERT INTO alerts_log (timestamp, engine_id, severity, parameter, value, message)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            timestamp, engine_id, alert.get("severity"), alert.get("parameter"),
            alert.get("value"), alert.get("message")
        ))

    conn.commit()
    conn.close()

def fetch_telemetry_history(limit=50):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM telemetry_history ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def fetch_alerts_log(limit=50):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM alerts_log ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def clear_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM telemetry_history")
    cursor.execute("DELETE FROM alerts_log")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at", DB_PATH)
