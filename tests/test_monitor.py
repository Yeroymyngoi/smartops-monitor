import json
import tempfile
import unittest
from pathlib import Path

from monitor import HealthMonitor


class HealthMonitorTests(unittest.TestCase):
    def test_persist_and_load_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = Path(temp_dir) / "health.jsonl"
            monitor = HealthMonitor(history_path=str(history_path))

            sample = {
                "timestamp": "2026-01-01T00:00:00+00:00",
                "cpu_percent": 10.5,
                "memory_percent": 30.1,
                "disk_percent": 55.2,
            }

            monitor.persist(sample)
            loaded = monitor.load_history()

            self.assertEqual(loaded, [sample])

            with history_path.open("r", encoding="utf-8") as file:
                stored = json.loads(file.readline())
            self.assertEqual(stored, sample)

    def test_flag_abnormal_detects_spike(self) -> None:
        monitor = HealthMonitor()
        baseline = [
            {"cpu_percent": 10.0, "memory_percent": 40.0, "disk_percent": 60.0},
            {"cpu_percent": 11.0, "memory_percent": 41.0, "disk_percent": 60.0},
            {"cpu_percent": 10.5, "memory_percent": 39.5, "disk_percent": 60.0},
            {"cpu_percent": 10.0, "memory_percent": 40.0, "disk_percent": 60.0},
            {"cpu_percent": 9.5, "memory_percent": 40.5, "disk_percent": 60.0},
        ]
        latest = {"cpu_percent": 95.0, "memory_percent": 40.0, "disk_percent": 60.0}

        anomaly = monitor.flag_abnormal(latest, baseline)

        self.assertTrue(anomaly["is_abnormal"])
        self.assertEqual(anomaly["metrics"][0]["metric"], "cpu_percent")

    def test_flag_abnormal_needs_min_samples(self) -> None:
        monitor = HealthMonitor()
        latest = {"cpu_percent": 60.0, "memory_percent": 70.0, "disk_percent": 80.0}
        baseline = [{"cpu_percent": 10.0, "memory_percent": 20.0, "disk_percent": 30.0}]

        anomaly = monitor.flag_abnormal(latest, baseline)

        self.assertFalse(anomaly["is_abnormal"])
        self.assertEqual(anomaly["metrics"], [])


if __name__ == "__main__":
    unittest.main()
