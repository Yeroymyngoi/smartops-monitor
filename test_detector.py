import pytest
from detector import detect_anomalies

def test_no_anomalies():
    readings = [10.0, 11.0, 10.5, 9.8, 10.2, 10.1]
    result = detect_anomalies(readings)
    assert result == []  # all values close together → no anomalies

def test_clear_anomaly():
    readings = [10.0, 10.1, 10.2, 10.0, 50.0, 10.1, 10.0]
    result = detect_anomalies(readings)
    assert len(result) == 1  # only one anomaly
    assert result[0][1] == 50.0  # the anomalous value is 50.0

def test_too_few_readings():
    readings = [10.0, 11.0]  # only 2 readings
    result = detect_anomalies(readings)
    assert result == []  # not enough data to compute std dev
