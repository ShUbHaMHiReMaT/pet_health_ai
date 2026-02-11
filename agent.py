import joblib
import pandas as pd
import numpy as np

# Load trained model
model = joblib.load("model.pkl")

# Memory buffer
history = []

BASELINE_HR = 85
BASELINE_TEMP = 38.5


def evaluate_reading(temp, hr):

    global history

    # Add to history
    history.append({"temperature": temp, "heart_rate": hr})

    # Keep only last 3 readings (15 mins)
    if len(history) > 3:
        history.pop(0)

    # ML anomaly detection
    data = pd.DataFrame([[temp, hr]],
                        columns=["temperature", "heart_rate"])
    anomaly = model.predict(data)[0]

    reasoning = []

    # --------------------------
    # RULE 1: Fever Logic
    # --------------------------
    if temp > 39.5 and hr > BASELINE_HR * 1.2:
        reasoning.append("Possible fever pattern detected.")

    # --------------------------
    # RULE 2: Stress Spike
    # --------------------------
    if hr > BASELINE_HR * 1.4 and temp < 39:
        reasoning.append("Possible stress or anxiety spike.")

    # --------------------------
    # RULE 3: Sustained Rising Trend
    # --------------------------
    if len(history) == 3:
        temps = [x["temperature"] for x in history]
        if temps[0] < temps[1] < temps[2]:
            reasoning.append("Sustained temperature rise over 15 minutes.")

    # --------------------------
    # ML Anomaly Layer
    # --------------------------
    if anomaly == -1:
        reasoning.append("AI baseline anomaly detected.")

    if not reasoning:
        reasoning.append("Vitals stable and within normal range.")

    return {
        "Temperature": temp,
        "Heart Rate": hr,
        "Assessment": reasoning
    }


# Simulate 3 consecutive readings
print(evaluate_reading(38.7, 90))
print(evaluate_reading(39.2, 105))
print(evaluate_reading(39.8, 120))
