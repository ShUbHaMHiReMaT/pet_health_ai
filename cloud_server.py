import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from ai_agent import analyze_vitals
import pandas as pd
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATA_FILE = "dataset.csv"

@app.route("/")
def home():
    return jsonify({"message": "Pet Health AI Cloud Server Running 🚀"})

# ===============================
# UPLOAD ROUTE (APP → AI)
# ===============================

@app.route("/upload", methods=["POST"])
def upload_data():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON received"}), 400

        temp = float(data.get("temperature", 0))
        hr = float(data.get("heart_rate", 0))
        weight = data.get("weight")
        age = data.get("age")
        breed_group = data.get("breed_group", "medium")

        # 🚨 Reject invalid sensor values
        if temp == 0 or hr == 0:
            return jsonify({
                "error": "Invalid sensor values",
                "health_index": 0,
                "risk_level": "NO SENSOR DATA"
            }), 400

        # 🔥 RUN AI
        result = analyze_vitals(
            temp,
            hr,
            weight=weight,
            age=age,
            breed_group=breed_group
        )

        # 🔥 STORE IN CSV
        row = {
            "timestamp": datetime.now(),
            "temperature": temp,
            "heart_rate": hr,
            "risk_level": result["risk_level"]
        }

        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        else:
            df = pd.DataFrame([row])

        df.to_csv(DATA_FILE, index=False)

        return jsonify(result)

    except Exception as e:
        print("SERVER ERROR:", e)
        return jsonify({
            "health_index": 0,
            "risk_level": "SERVER ERROR"
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
