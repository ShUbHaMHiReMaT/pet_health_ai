from ai_core import analyze
import random
import time

while True:
    temp = round(random.uniform(38.4, 40.5),2)
    hr = round(random.uniform(80, 150),2)

    result = analyze(temp, hr)
    print(result)

    # Real-time retraining trigger
    if result.get("risk_score",0) < 20:
        print("Stable pattern — eligible for background retraining")

    time.sleep(5)
