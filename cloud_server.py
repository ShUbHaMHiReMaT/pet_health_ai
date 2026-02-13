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

        temp = float(data.get("temperature", 0))
        hr = float(data.get("heart_rate", 0))
        pet_id = data.get("pet_id", "unknown")

        result = analyze_vitals(
            temp,
            hr,
            weight=data.get("weight"),
            age=data.get("age"),
            breed_group=data.get("breed_group")
        )

        # 🔥 APPEND TO dataset.csv
        file_path = os.path.join(os.getcwd(), "dataset.csv")

        new_row = pd.DataFrame([{
            "timestamp": pd.Timestamp.now(),
            "temperature": temp,
            "heart_rate": hr,
            "status": result["risk_level"]
        }])

        if os.path.exists(file_path):
            new_row.to_csv(file_path, mode='a', header=False, index=False)
        else:
            new_row.to_csv(file_path, index=False)

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

        temp = float(last.get("temperature", 0))
        hr = float(last.get("heart_rate", 0))

        # 🔥 RUN AI HERE
        result = analyze_vitals(
        temp,
        hr,
        weight=data.get("weight"),
        age=data.get("age"),
        breed_group=data.get("breed_group", "medium")
)


        return jsonify(result)

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
