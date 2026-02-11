from flask import Flask, request, jsonify
from pymongo import MongoClient
from ai_agent import analyze_vitals

app = Flask(__name__)

# Connect to MongoDB Atlas
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

    #collection.insert_one(record)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
