from __future__ import annotations

import argparse
import json
import math
import shutil
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class CPUSnapshot:
    idle: int
    total: int


class HealthMonitor:
    def __init__(self, history_path: str = "health_metrics.jsonl", disk_path: str = "/") -> None:
        self.history_path = Path(history_path)
        self.disk_path = disk_path
        self._previous_cpu: CPUSnapshot | None = None

    def _read_cpu_snapshot(self) -> CPUSnapshot:
        with Path("/proc/stat").open("r", encoding="utf-8") as file:
            cpu_line = file.readline().strip().split()

        values = [int(value) for value in cpu_line[1:]]
        idle = values[3] + values[4]
        total = sum(values)
        return CPUSnapshot(idle=idle, total=total)

    def _read_cpu_percent(self) -> float:
        current = self._read_cpu_snapshot()

        if self._previous_cpu is None:
            self._previous_cpu = current
            return 0.0

        total_delta = current.total - self._previous_cpu.total
        idle_delta = current.idle - self._previous_cpu.idle
        self._previous_cpu = current

        if total_delta <= 0:
            return 0.0

        busy = total_delta - idle_delta
        return round((busy / total_delta) * 100, 2)

    def _read_memory_percent(self) -> float:
        mem_total_kb = 0
        mem_available_kb = 0

        with Path("/proc/meminfo").open("r", encoding="utf-8") as file:
            for line in file:
                if line.startswith("MemTotal:"):
                    mem_total_kb = int(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    mem_available_kb = int(line.split()[1])

        if mem_total_kb == 0:
            return 0.0

        used_percent = (1 - (mem_available_kb / mem_total_kb)) * 100
        return round(used_percent, 2)

    def _read_disk_percent(self) -> float:
        usage = shutil.disk_usage(self.disk_path)
        if usage.total == 0:
            return 0.0

        used_percent = (usage.used / usage.total) * 100
        return round(used_percent, 2)

    def collect(self) -> dict[str, float | str]:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu_percent": self._read_cpu_percent(),
            "memory_percent": self._read_memory_percent(),
            "disk_percent": self._read_disk_percent(),
        }

    def persist(self, sample: dict[str, Any]) -> None:
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(sample) + "\n")

    def load_history(self) -> list[dict[str, Any]]:
        if not self.history_path.exists():
            return []

        rows: list[dict[str, Any]] = []
        with self.history_path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                rows.append(json.loads(line))
        return rows

    def flag_abnormal(
        self,
        latest: dict[str, float | str],
        prior_samples: list[dict[str, float | str]],
        min_samples: int = 5,
        z_threshold: float = 2.5,
    ) -> dict[str, Any]:
        result = {"is_abnormal": False, "metrics": []}

        if len(prior_samples) < min_samples:
            return result

        metric_keys = ("cpu_percent", "memory_percent", "disk_percent")

        for key in metric_keys:
            baseline = [float(sample[key]) for sample in prior_samples if key in sample]
            if len(baseline) < min_samples:
                continue

            mean = sum(baseline) / len(baseline)
            variance = sum((value - mean) ** 2 for value in baseline) / len(baseline)
            std_dev = math.sqrt(variance)
            if std_dev == 0:
                continue

            latest_value = float(latest[key])
            z_score = abs((latest_value - mean) / std_dev)
            if z_score >= z_threshold:
                result["is_abnormal"] = True
                result["metrics"].append(
                    {
                        "metric": key,
                        "value": latest_value,
                        "mean": round(mean, 2),
                        "std_dev": round(std_dev, 2),
                        "z_score": round(z_score, 2),
                    }
                )

        return result

    def run(self, interval_seconds: int = 5, iterations: int | None = None) -> None:
        count = 0
        while iterations is None or count < iterations:
            prior_samples = self.load_history()
            sample = self.collect()
            self.persist(sample)
            anomaly = self.flag_abnormal(sample, prior_samples)

            print(json.dumps({"sample": sample, "anomaly": anomaly}))

            count += 1
            if iterations is None or count < iterations:
                time.sleep(interval_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monitor CPU, memory, and disk health")
    parser.add_argument("--interval", type=int, default=5, help="Sample interval in seconds")
    parser.add_argument(
        "--iterations",
        type=int,
        default=None,
        help="Number of samples to collect (default: run forever)",
    )
    parser.add_argument(
        "--history-file",
        default="health_metrics.jsonl",
        help="Path for stored health metrics history",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    monitor = HealthMonitor(history_path=args.history_file)
    monitor.run(interval_seconds=args.interval, iterations=args.iterations)


if __name__ == "__main__":
    main()
