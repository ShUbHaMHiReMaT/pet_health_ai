import joblib
import pandas as pd
import numpy as np
from collections import deque
import torch
import torch.nn as nn
import torch.optim as optim

# -----------------------------
# LOAD EXISTING ISOLATION MODEL
# -----------------------------
model = joblib.load("model.pkl")

# -----------------------------
# HISTORY BUFFER
# -----------------------------
history = deque(maxlen=288)  # 24 hrs if 5-min interval

# -----------------------------
# LSTM MODEL FOR PREDICTION
# -----------------------------
class LSTMModel(nn.Module):
    def __init__(self):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size=2, hidden_size=32, batch_first=True)
        self.fc = nn.Linear(32, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out

lstm_model = LSTMModel()

# -----------------------------
# FEDERATED LEARNING HOOK
# -----------------------------
def local_federated_update(temp, hr):
    """
    Simulates local training on user device.
    Only model weights are returned — not raw data.
    """
    optimizer = optim.Adam(lstm_model.parameters(), lr=0.001)
    criterion = nn.MSELoss()

    if len(history) < 10:
        return None

    data = np.array([[h["temperature"], h["heart_rate"]] for h in history])
    inputs = torch.tensor(data[:-1], dtype=torch.float32).unsqueeze(0)
    target = torch.tensor([[data[-1][0]]], dtype=torch.float32)

    optimizer.zero_grad()
    output = lstm_model(inputs)
    loss = criterion(output, target)
    loss.backward()
    optimizer.step()

    return lstm_model.state_dict()  # send only weights

# -----------------------------
# FUZZY LOGIC FUNCTIONS
# -----------------------------
def fuzzy_temperature(temp):
    if temp <= 38.3:
        return 0
    elif 38.3 < temp <= 39.2:
        return (temp - 38.3) / 0.9
    elif 39.2 < temp <= 40:
        return 1 + (temp - 39.2)
    else:
        return 2

def fuzzy_heart_rate(hr, min_hr, max_hr):
    if min_hr <= hr <= max_hr:
        return 0
    elif hr > max_hr:
        return (hr - max_hr) / max_hr
    else:
        return (min_hr - hr) / min_hr

# -----------------------------
# MAIN ANALYSIS FUNCTION
# -----------------------------
def analyze_vitals(temp, hr, weight=None, age=None, breed_group=None):

    history.append({"temperature": temp, "heart_rate": hr})

    # -------------------------
    # BASELINE CALCULATION
    # -------------------------
    if len(history) < 3:
        baseline_temp, baseline_hr = 38.5, 85
        std_temp, std_hr = 0.2, 5
    else:
        temps = [h["temperature"] for h in history]
        hrs = [h["heart_rate"] for h in history]
        baseline_temp = np.mean(temps)
        baseline_hr = np.mean(hrs)
        std_temp = np.std(temps) if np.std(temps) > 0 else 0.1
        std_hr = np.std(hrs) if np.std(hrs) > 0 else 1

    # -------------------------
    # BREED SIZE RANGE
    # -------------------------
    normal_hr_min, normal_hr_max = 60, 140
    if breed_group == "small":
        normal_hr_min, normal_hr_max = 100, 140
    elif breed_group == "medium":
        normal_hr_min, normal_hr_max = 80, 120
    elif breed_group == "large":
        normal_hr_min, normal_hr_max = 60, 100
    elif breed_group == "giant":
        normal_hr_min, normal_hr_max = 50, 90

    # -------------------------
    # FUZZY SCORING
    # -------------------------
    fuzzy_temp_score = fuzzy_temperature(temp)
    fuzzy_hr_score = fuzzy_heart_rate(hr, normal_hr_min, normal_hr_max)

    # -------------------------
    # ISOLATION FOREST
    # -------------------------
    data = pd.DataFrame([[temp, hr]],
                        columns=["temperature", "heart_rate"])

    anomaly_score = model.decision_function(data)[0]
    anomaly_flag = model.predict(data)[0]

    # -------------------------
    # RISK SCORING
    # -------------------------
    risk_score = 0
    reasons = []
    recommendations = []

    # Fuzzy contribution
    risk_score += fuzzy_temp_score * 20
    risk_score += fuzzy_hr_score * 20

    # Hard thresholds
    if temp > 40 or temp < 35:
        risk_score += 60
        reasons.append("Dangerous body temperature")

    if hr > 180 or hr < 40:
        risk_score += 50
        reasons.append("Dangerous heart rate")

    # Isolation Forest anomaly
    if anomaly_flag == -1:
        risk_score += 20
        reasons.append("AI anomaly detected")

    risk_score = min(risk_score, 100)
    health_index = 100 - risk_score

    # -------------------------
    # LSTM 6-HOUR PREDICTION
    # -------------------------
    predicted_risk = None
    if len(history) >= 20:
        data = np.array([[h["temperature"], h["heart_rate"]] for h in history])
        inputs = torch.tensor(data, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            future_temp = lstm_model(inputs).item()
        predicted_risk = future_temp

        if future_temp > 39.5:
            recommendations.append("Predicted fever within 6 hours")

    # -------------------------
    # FEDERATED LEARNING UPDATE
    # -------------------------
    federated_weights = local_federated_update(temp, hr)

    # -------------------------
    # RISK LEVEL
    # -------------------------
    if risk_score >= 70:
        level = "CRITICAL"
    elif risk_score >= 40:
        level = "WARNING"
    else:
        level = "STABLE"

    return {
        "temperature": temp,
        "heart_rate": hr,
        "baseline_temp": round(baseline_temp, 2),
        "baseline_hr": round(baseline_hr, 2),
        "risk_score": int(risk_score),
        "health_index": int(health_index),
        "risk_level": level,
        "anomaly_score": float(anomaly_score),
        "reasons": reasons,
        "recommendations": recommendations,
        "predicted_future_temp_6h": predicted_risk,
        "federated_update_sent": federated_weights is not None
    }
