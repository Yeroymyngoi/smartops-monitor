from fastapi import FastAPI
import sqlite3
from pydantic import BaseModel

# Create FastAPI app instance
app = FastAPI()

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
def get_metrics():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, cpu, memory, disk FROM metrics ORDER BY id DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to list of Metric objects
    metrics = [Metric(**dict(row)) for row in rows]
    return metrics
