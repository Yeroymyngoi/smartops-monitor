from fastapi import FastAPI
import sqlite3
from pydantic import BaseModel
from detector import detect_anomalies

# Create FastAPI app instance
app = FastAPI()
@app.on_event("startup")
def startup():
    conn = sqlite3.connect("metrics.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            cpu REAL,
            memory REAL,
            disk REAL
        )
    """)
    conn.commit()
    conn.close()
# Define the data model for a metric reading
class Metric(BaseModel):
    timestamp: str
    cpu: float
    memory: float
    disk: float

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect("metrics.db")
    conn.row_factory = sqlite3.Row  # allows dict-like access to rows
    return conn

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "ok"}

# Metrics endpoint: return last 50 readings
@app.get("/metrics")
def get_metrics(limit: int = 50):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, cpu, memory, disk FROM metrics ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to list of Metric objects
    metrics = [Metric(**dict(row)) for row in rows]
    return metrics

@app.get("/anomalies")
def get_anomalies(limit: int = 100, threshold: float = 2.0):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT cpu FROM metrics ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()

    cpu_values = [row["cpu"] for row in rows]
    anomalies = detect_anomalies(cpu_values, threshold)

    return {
        "total_readings_checked": len(cpu_values),
        "anomalies_found": len(anomalies),
        "threshold": threshold,
        "anomalies": [
            {"index": idx, "value": val, "z_score": round(z, 3)}
            for idx, val, z in anomalies
        ]
    }