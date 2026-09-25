import statistics

def detect_anomalies(readings: list[float], threshold: float = 2.0) -> list[tuple[int, float, float]]:
    # If fewer than 3 readings, we can't compute a meaningful std dev
    if len(readings) < 3:
        return []

    # Compute mean and standard deviation
    mean = statistics.mean(readings)
    std_dev = statistics.stdev(readings)

    # If std dev is zero, all values are identical → no anomalies
    if std_dev == 0:
        return []

    anomalies = []
    # Loop through each reading with its index
    for i, value in enumerate(readings):
        z = (value - mean) / std_dev
        if abs(z) > threshold:
            anomalies.append((i, value, z))

    return anomalies
