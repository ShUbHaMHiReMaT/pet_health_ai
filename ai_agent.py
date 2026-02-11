import joblib
import pandas as pd
import numpy as np
from collections import deque

# Load trained model
model = joblib.load("model.pkl")

# Memory for last 12 readings (1 hour if 5 min interval)
history = deque(maxlen=12)

def calculate_baseline():
    temps = [h["temperature"] for h in history]
    hrs = [h["heart_rate"] for h in history]

    if len(temps) < 3:
        return 38.5, 85, 0.2, 5  # default baseline

    return (
        np.mean(temps),
        np.mean(hrs),
        np.std(temps),
        np.std(hrs)
    )

def calculate_trend(values):
    if len(values) < 3:
        return 0
    return values[-1] - values[0]

def analyze_vitals(temp, hr):

    history.append({"temperature": temp, "heart_rate": hr})

    baseline_temp, baseline_hr, std_temp, std_hr = calculate_baseline()

    # Avoid division by zero
    std_temp = std_temp if std_temp > 0 else 0.1
    std_hr = std_hr if std_hr > 0 else 1

    # Z-score deviation
    temp_z = abs((temp - baseline_temp) / std_temp)
    hr_z = abs((hr - baseline_hr) / std_hr)

    # Trend detection
    temp_trend = calculate_trend([h["temperature"] for h in history])
    hr_trend = calculate_trend([h["heart_rate"] for h in history])

    # ML anomaly
    data = pd.DataFrame([[temp, hr]],
                        columns=["temperature", "heart_rate"])

    anomaly_score = model.decision_function(data)[0]
    anomaly_flag = model.predict(data)[0]

    risk_score = 0
    reasons = []

    # Deviation strength
    if temp_z > 2:
        risk_score += 25
        reasons.append("Temperature deviating from baseline")

    if hr_z > 2:
        risk_score += 25
        reasons.append("Heart rate deviating from baseline")

    # Sustained trend
    if temp_trend > 0.8:
        risk_score += 20
        reasons.append("Sustained temperature rise")

    if hr_trend > 20:
        risk_score += 15
        reasons.append("Rapid heart rate increase")

    # ML anomaly
    if anomaly_flag == -1:
        risk_score += 20
        reasons.append("AI anomaly detected")

    # Normalize
    risk_score = min(risk_score, 100)

    # Health Stability Index (inverse of risk)
    health_index = 100 - risk_score

    if risk_score >= 70:
        level = "CRITICAL"
    elif risk_score >= 40:
        level = "WARNING"
    else:
        level = "STABLE"

    return {
        "temperature": temp,
        "heart_rate": hr,
        "baseline_temp": round(baseline_temp,2),
        "baseline_hr": round(baseline_hr,2),
        "risk_score": risk_score,
        "health_index": health_index,
        "risk_level": level,
        "anomaly_score": float(anomaly_score),
        "reasons": reasons
    }
