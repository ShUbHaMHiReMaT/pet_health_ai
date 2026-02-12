import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from ai_agent import analyze_vitals
import pandas as pd

app = Flask(__name__)
CORS(app)

# ===============================
# ROOT ROUTE
# ===============================

@app.route("/")
def home():
    return jsonify({"message": "Pet Health AI Cloud Server Running 🚀"})


# ===============================
# UPLOAD ROUTE (ESP32 → AI)
# ===============================

@app.route("/upload", methods=["POST"])
def upload_data():

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON received"}), 400

        temp = float(data.get("temperature", 0))
        hr = float(data.get("heart_rate", 0))
        pet_id = data.get("pet_id", "unknown")

        result = analyze_vitals(temp, hr)

        return jsonify(result)

    except Exception as e:
        print("UPLOAD ERROR:", e)
        return jsonify({
            "temperature": 0,
            "heart_rate": 0,
            "health_index": 0,
            "risk_level": "SERVER ERROR"
        }), 500


# ===============================
# LATEST DATA ROUTE (APP → SERVER)
# ===============================

@app.route("/latest", methods=["GET"])
def get_latest():

    try:
        file_path = os.path.join(os.getcwd(), "dataset.csv")

        if not os.path.exists(file_path):
            return jsonify({
                "temperature": 0,
                "heart_rate": 0,
                "health_index": 0,
                "risk_level": "NO DATA"
            })

        df = pd.read_csv(file_path)

        if df.empty:
            return jsonify({
                "temperature": 0,
                "heart_rate": 0,
                "health_index": 0,
                "risk_level": "NO DATA"
            })

        last = df.iloc[-1]

        # Safely read columns
        temperature = float(last.get("temperature", 0))
        heart_rate = float(last.get("heart_rate", 0))
        status = str(last.get("status", "STABLE")).upper()

        return jsonify({
            "temperature": temperature,
            "heart_rate": heart_rate,
            "health_index": 85,
            "risk_level": status
        })

    except Exception as e:
        print("LATEST ERROR:", e)
        return jsonify({
            "temperature": 0,
            "heart_rate": 0,
            "health_index": 0,
            "risk_level": "SERVER ERROR"
        }), 500


# ===============================
# START SERVER
# ===============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
