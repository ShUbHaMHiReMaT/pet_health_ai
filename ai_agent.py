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

def analyze_vitals(temp, hr, weight=None, age=None, breed_group=None):

    history.append({"temperature": temp, "heart_rate": hr})

    baseline_temp, baseline_hr, std_temp, std_hr = calculate_baseline()

    std_temp = std_temp if std_temp > 0 else 0.1
    std_hr = std_hr if std_hr > 0 else 1

    temp_z = abs((temp - baseline_temp) / std_temp)
    hr_z = abs((hr - baseline_hr) / std_hr)

    temp_trend = calculate_trend([h["temperature"] for h in history])
    hr_trend = calculate_trend([h["heart_rate"] for h in history])

    data = pd.DataFrame([[temp, hr]],
                        columns=["temperature", "heart_rate"])

    anomaly_score = model.decision_function(data)[0]
    anomaly_flag = model.predict(data)[0]

    risk_score = 0
    reasons = []
    recommendations = []

    # -----------------------------
    # HARD MEDICAL SAFETY THRESHOLDS
    # -----------------------------
    if temp > 40 or temp < 35:
        risk_score += 60
        reasons.append("Dangerous body temperature")
        recommendations.append("Immediate veterinary attention required")

    if hr > 180 or hr < 40:
        risk_score += 50
        reasons.append("Dangerous heart rate")
        recommendations.append("Check for cardiac distress immediately")

    # -----------------------------
    # BREED SIZE BASED NORMAL RANGES
    # -----------------------------
    normal_hr_min = 60
    normal_hr_max = 140

    if breed_group == "small":
        normal_hr_min, normal_hr_max = 100, 140
    elif breed_group == "medium":
        normal_hr_min, normal_hr_max = 80, 120
    elif breed_group == "large":
        normal_hr_min, normal_hr_max = 60, 100
    elif breed_group == "giant":
        normal_hr_min, normal_hr_max = 50, 90

    if hr < normal_hr_min or hr > normal_hr_max:
        risk_score += 25
        reasons.append("Heart rate abnormal for breed size")
        recommendations.append("Monitor heart rate for 30 minutes")

    if temp < 38.3 or temp > 39.2:
        risk_score += 20
        reasons.append("Temperature outside normal range")
        recommendations.append("Keep pet hydrated and recheck temperature")

    # -----------------------------
    # BASELINE DEVIATION
    # -----------------------------
    if temp_z > 2:
        risk_score += 20
        reasons.append("Temperature deviating from baseline")

    if hr_z > 2:
        risk_score += 20
        reasons.append("Heart rate deviating from baseline")

    # -----------------------------
    # TREND DETECTION
    # -----------------------------
    if temp_trend > 0.8:
        risk_score += 15
        reasons.append("Sustained temperature rise")

    if hr_trend > 20:
        risk_score += 15
        reasons.append("Rapid heart rate increase")

    # -----------------------------
    # ML ANOMALY
    # -----------------------------
    if anomaly_flag == -1:
        risk_score += 20
        reasons.append("AI anomaly detected")

    # Normalize
    risk_score = min(risk_score, 100)
    health_index = 100 - risk_score

    if risk_score >= 70:
        level = "CRITICAL"
    elif risk_score >= 40:
        level = "WARNING"
    else:
        level = "STABLE"

    # -----------------------------
    # FALSE DATA MONITORING
    # -----------------------------
    inconsistency_flag = False
    if len(history) >= 12:
        recent = list(history)[-12:]
        temps = [r["temperature"] for r in recent]
        if max(temps) - min(temps) > 8:
            inconsistency_flag = True
            recommendations.append("Possible incorrect breed/age input detected")

    return {
        "temperature": temp,
        "heart_rate": hr,
        "baseline_temp": round(baseline_temp, 2),
        "baseline_hr": round(baseline_hr, 2),
        "risk_score": risk_score,
        "health_index": health_index,
        "risk_level": level,
        "anomaly_score": float(anomaly_score),
        "reasons": reasons,
        "recommendations": recommendations,
        "inconsistency_flag": inconsistency_flag
    }

    
    # -----------------------------
    # HARD MEDICAL SAFETY THRESHOLDS
    # -----------------------------
    if temp > 40 or temp < 35:
     risk_score += 60
    reasons.append("Dangerous body temperature")

    if hr > 160 or hr < 40:
     risk_score += 40
    reasons.append("Dangerous heart rate")
   # -----------------------------

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
        # Deviation strength
        
    if temp_z > 2:
     risk_score += 25
     reasons.append("Temperature deviating from baseline")

    if hr_z > 2:
     risk_score += 25
     reasons.append("Heart rate deviating from baseline")


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
