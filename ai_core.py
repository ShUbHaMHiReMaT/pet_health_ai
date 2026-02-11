import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model
from collections import deque

# Load models
lstm = load_model("models/lstm_model.h5")
iso = joblib.load("models/iso_model.pkl")
scaler = joblib.load("models/scaler.pkl")

# 24 hours memory (5 min interval = 288 readings)
history = deque(maxlen=288)

def bayesian_fusion(lstm_prob, iso_prob):
    combined = 0.6 * lstm_prob + 0.4 * iso_prob
    return min(max(combined, 0), 1)

def analyze(temp, hr):

    history.append([temp, hr])

    # Need at least 12 readings (1 hour) before full intelligence
    if len(history) < 12:
        return {"status": "Collecting baseline data..."}

    data_array = np.array(history)

    # Auto baseline recalibration (rolling 24h mean)
    baseline_temp = np.mean(data_array[:, 0])
    baseline_hr = np.mean(data_array[:, 1])

    # Scale data
    scaled = scaler.transform(data_array)
    seq = scaled[-12:]
    seq = np.expand_dims(seq, axis=0)

    # LSTM prediction
    pred = lstm.predict(seq, verbose=0)
    actual = scaled[-1]

    error = np.mean((pred[0] - actual) ** 2)
    lstm_prob = min(error * 10, 1)

    # Isolation Forest
    iso_flag = iso.predict([[temp, hr]])[0]
    iso_score = iso.decision_function([[temp, hr]])[0]
    iso_prob = 1 if iso_flag == -1 else 0

    # Bayesian Fusion
    anomaly_prob = bayesian_fusion(lstm_prob, iso_prob)

    # --- Smoothed Risk Computation ---
    risk_score = 0

    temp_dev_ratio = abs(temp - baseline_temp) / baseline_temp
    hr_dev_ratio = abs(hr - baseline_hr) / baseline_hr

    risk_score += min(temp_dev_ratio * 100, 30)
    risk_score += min(hr_dev_ratio * 100, 25)
    risk_score += min(lstm_prob * 30, 20)

    if iso_flag == -1:
        risk_score += 15

    # Sustained confirmation (last 3 readings)
    if len(history) >= 3:
        recent = list(history)[-3:]
        temp_rising = recent[0][0] < recent[1][0] < recent[2][0]
        hr_rising = recent[0][1] < recent[1][1] < recent[2][1]

        if temp_rising and hr_rising:
            risk_score += 10

    risk_score = min(risk_score, 100)
    health_index = 100 - risk_score

    # Risk level calibration
    if risk_score >= 80:
        level = "CRITICAL"
    elif risk_score >= 50:
        level = "WARNING"
    else:
        level = "STABLE"

    return {
        "temperature": temp,
        "heart_rate": hr,
        "baseline_temp": round(baseline_temp, 2),
        "baseline_hr": round(baseline_hr, 2),
        "risk_score": round(risk_score, 2),
        "health_index": round(health_index, 2),
        "risk_level": level,
        "lstm_error": float(error),
        "iso_score": float(iso_score)
    }
