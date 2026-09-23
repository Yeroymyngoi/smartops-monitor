import psutil
import sqlite3
import time
from datetime import datetime

# Connect to (or create) the database file
conn = sqlite3.connect("metrics.db")
cursor = conn.cursor()

# Create the table if it doesn’t already exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    cpu REAL,
    memory REAL,
    disk REAL
)
""")
conn.commit()

# Infinite loop to collect metrics
while True:
    # Read system usage
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    # Current timestamp
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insert values into the database
    cursor.execute("INSERT INTO metrics (timestamp, cpu, memory, disk) VALUES (?, ?, ?, ?)",
                   (ts, cpu, memory, disk))
    conn.commit()

    # Print values to terminal
    print(f"{ts} | CPU: {cpu}% | Memory: {memory}% | Disk: {disk}%")

    # Wait 5 seconds
    time.sleep(5)
