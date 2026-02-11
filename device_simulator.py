import requests
import random
import time

URL = "http://127.0.0.1:5000/upload"

while True:

    data = {
        "pet_id": "dog_001",
        "temperature": round(random.uniform(38.4, 40.0),2),
        "heart_rate": round(random.uniform(80, 140),2)
    }

    response = requests.post(URL, json=data)
    print(response.json())

    time.sleep(300)  # 5 minutes
