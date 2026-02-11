import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

# Load dataset
df = pd.read_csv("dataset.csv")

# Use only healthy data for baseline
healthy_data = df[df["state"] == "healthy"][["temperature","heart_rate"]]

# Train Isolation Forest
model = IsolationForest(contamination=0.1, random_state=42)
model.fit(healthy_data)

# Save model
joblib.dump(model, "model.pkl")

print("Model trained and saved as model.pkl")
