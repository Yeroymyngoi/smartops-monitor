# smartops-monitor

Simple system health monitor that:
- checks CPU, memory, and disk usage every few seconds,
- stores each reading in a local history file,
- flags potentially abnormal readings using a rolling baseline.

## Run

```bash
python monitor.py --interval 5 --history-file health_metrics.jsonl
```

Optional one-shot sampling count:

```bash
python monitor.py --interval 2 --iterations 10 --history-file health_metrics.jsonl
```

## Test

```bash
python -m unittest discover -s tests
```
