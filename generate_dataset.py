import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

def generate_data(days=7):
    start_time = datetime.now()
    rows = []

    baseline_hr = 85
    baseline_temp = 38.5

    for i in range(days * 288):  # 288 readings per day (5 min interval)
        timestamp = start_time + timedelta(minutes=5*i)

        state = random.choices(
            ["healthy", "fever", "stress"],
            weights=[0.75, 0.15, 0.10]
        )[0]

        if state == "healthy":
            hr = baseline_hr + np.random.normal(0, 5)
            temp = baseline_temp + np.random.normal(0, 0.2)

        elif state == "fever":
            hr = baseline_hr + np.random.normal(25, 5)
            temp = baseline_temp + np.random.normal(1.2, 0.3)

        elif state == "stress":
            hr = baseline_hr + np.random.normal(40, 10)
            temp = baseline_temp + np.random.normal(0.1, 0.1)

        rows.append([timestamp, round(temp,2), round(hr,2), state])

    df = pd.DataFrame(rows, columns=["timestamp","temperature","heart_rate","state"])
    df.to_csv("dataset.csv", index=False)
    print("Dataset saved as dataset.csv")

generate_data()
