import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from ai_agent import analyze_vitals

app = Flask(__name__)
CORS(app)

# MongoDB (optional)
client = MongoClient("YOUR_MONGODB_CONNECTION_STRING")
db = client["pet_health"]
collection = db["vitals"]


@app.route("/")
def home():
    return "Pet Health AI Cloud Server Running 🚀"


@app.route("/upload", methods=["POST"])
def upload_data():

    data = request.json

    temp = data["temperature"]
    hr = data["heart_rate"]
    pet_id = data["pet_id"]

    result = analyze_vitals(temp, hr)

    record = {
        "pet_id": pet_id,
        "temperature": temp,
        "heart_rate": hr,
        "analysis": result
    }

    # Uncomment if using MongoDB
    # collection.insert_one(record)

    return jsonify(result)
@app.route("/latest", methods=["GET"])
def get_latest():
    import pandas as pd

    df = pd.read_csv("dataset.csv")
    last = df.iloc[-1]

    return jsonify({
        "temperature": float(last["temperature"]),
        "heart_rate": float(last["heart_rate"]),
        "health_index": 85,
        "risk_level": last["status"]
    })



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
