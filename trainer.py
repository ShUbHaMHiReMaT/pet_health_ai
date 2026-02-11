import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import os

df = pd.read_csv("dataset.csv")

features = df[["temperature","heart_rate"]].values

scaler = MinMaxScaler()
scaled = scaler.fit_transform(features)

sequence_length = 12  # 1 hour window

X = []
y = []

for i in range(len(scaled) - sequence_length):
    X.append(scaled[i:i+sequence_length])
    y.append(scaled[i+sequence_length])

X = np.array(X)
y = np.array(y)

# LSTM Model
model = Sequential()
model.add(LSTM(32, input_shape=(sequence_length,2)))
model.add(Dense(2))
model.compile(optimizer="adam", loss="mse")

model.fit(X, y, epochs=10, batch_size=16)

os.makedirs("models", exist_ok=True)
model.save("models/lstm_model.h5")

# Adaptive contamination
contamination_rate = 0.1
iso = IsolationForest(contamination=contamination_rate)
iso.fit(features)

joblib.dump(iso, "models/iso_model.pkl")
joblib.dump(scaler, "models/scaler.pkl")

print("Models trained and saved.")
