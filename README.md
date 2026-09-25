# SmartOps Monitor

![Tests](https://github.com/Yeromyngoi/smartops-monitor/actions/workflows/tests.yml/badge.svg)

A lightweight infrastructure monitoring system that collects system metrics, stores them, and detects anomalies in real time.

## Current Status
- [x] Data collection
- [x] SQLite storage
- [x] REST API (FastAPI with /health, /metrics, /anomalies)
- [x] Z-score anomaly detection with pytest tests
- [ ] Docker + GitHub Actions 
- [ ] Live deployment 

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

## How Detection Works

The `/anomalies` endpoint uses Z-score detection. For each reading, it computes how many standard deviations away from the mean it is: `z = (value - mean) / std_dev`. If `|z| > threshold` (default 2.0), the reading is flagged as anomalous. This approach works without training data, making it suitable for cold-start monitoring scenarios.

Try it:
- `/anomalies` — default threshold 2.0
- `/anomalies?threshold=1.5` — more sensitive
- `/anomalies?limit=50&threshold=1.0` — very sensitive, last 50 readings

## Tech Stack
- Python 3.14
- psutil (system metrics)
- SQLite (storage)

## Author
Yerzhigit Tuimebay 