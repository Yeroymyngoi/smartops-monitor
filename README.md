# SmartOps Monitor

A lightweight infrastructure monitoring system that collects system metrics, stores them, and detects anomalies in real time.

## Current Status
- [x] Data collection — CPU, RAM, disk every 5 seconds
- [x] SQLite storage
- [ ] REST API (Week 2)
- [ ] Anomaly detection (Week 3)
- [ ] Docker + GitHub Actions (Week 4)
- [ ] Live deployment (Week 4)

## Why This Exists
Small teams and independent developers often lack access to affordable monitoring tools. SmartOps Monitor is a self-hosted, lightweight alternative that runs on a single machine and provides the core essentials: metrics history and anomaly alerts.

## Architecture
Collector (psutil) → SQLite → (Week 2: FastAPI) → (Week 3: Detector) → Dashboard

## How to Run
1. Clone the repo
2. Create a virtual environment: `python -m venv venv`
3. Activate it:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install psutil`
5. Run the collector: `python collector.py`

Press `Ctrl+C` to stop.

## Tech Stack
- Python 3.14
- psutil (system metrics)
- SQLite (storage)

## Author
Yerzhigit Tuimebay 