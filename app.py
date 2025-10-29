# ===================================================
# 🌾 Crop Yield Prediction - Streamlit UI (Final)
# ===================================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib

# ------------------------------
# Load Model and Scaler
# ------------------------------
model = joblib.load("best_model.pkl")
scaler = joblib.load("scaler.pkl")

st.set_page_config(page_title="🌾 Crop Yield Predictor", layout="centered")
st.title("🌾 Crop Yield Prediction App")
st.write("Enter the environmental and farming details below to predict the **Crop Yield**.")

# ------------------------------
# Input Fields
# ------------------------------
rainfall = st.number_input("🌧️ Rainfall", step=0.1, format="%.5f")
temperature = st.number_input("🌡️ Temperature (°C)", step=0.1, format="%.5f")
humidity = st.number_input("💧 Humidity (%)", step=0.1, format="%.5f")
wind_speed = st.number_input("🌬️ Wind Speed (m/s)", step=0.1, format="%.5f")
solar_radiation = st.number_input("☀️ Solar Radiation", step=0.1, format="%.5f")
soil_ph = st.number_input("🌱 Soil pH", step=0.1, format="%.5f")
soil_moisture = st.number_input("💦 Soil Moisture (%)", step=0.1, format="%.5f")
organic_matter = st.number_input("🌿 Organic Matter Content (%)", step=0.1, format="%.5f")
nitrogen = st.number_input("🧪 Nitrogen", step=0.1, format="%.5f")
phosphorus = st.number_input("🧪 Phosphorus", step=0.1, format="%.5f")
potassium = st.number_input("🧪 Potassium", step=0.1, format="%.5f")
plant_population = st.number_input("🌾 Plant Population", step=1.0)
fertilizer_rate = st.number_input("🧴 Fertilizer Rate", step=1.0)
weeding_frequency = st.number_input("🌿 Weeding Frequency (per season)", step=1.0)
sowing_date = st.number_input("📅 Sowing Date (day of year)", step=1.0)
tillage_practice = st.selectbox("🚜 Tillage Practice", ["Conventional", "No till", "strip till"])
crop_type = st.selectbox("🌽 Crop Type", ["Cassava", "Maize", "Rice", "Yam", "Soyabean"])

# ------------------------------
# Encoding for categorical inputs
# ------------------------------
tillage_map = {"Conventional": 0, "No till": 1, "strip till": 2}
crop_map = {"Cassava": 0, "Maize": 1, "Rice": 2, "Soyabean": 3, "Yam": 4}

tillage_val = tillage_map[tillage_practice]
crop_val = crop_map[crop_type]

# ------------------------------
# Prepare Input Data (Order must match training)
# ------------------------------
input_data = np.array([[
    rainfall, temperature, humidity, wind_speed, solar_radiation,
    soil_ph, soil_moisture, organic_matter, nitrogen, phosphorus,
    potassium, crop_val, plant_population, fertilizer_rate,
    tillage_val, sowing_date, weeding_frequency
]])

# Scale numeric features
input_data_scaled = scaler.transform(input_data)

# ------------------------------
# Predict Button
# ------------------------------
if st.button("🔍 Predict Crop Yield"):
    prediction = model.predict(input_data_scaled)[0]

    # Interpret output
    if prediction == 0:
        st.success("🌾 **Predicted Crop Yield: HIGH**")
    elif prediction == 1:
        st.warning("🌿 **Predicted Crop Yield: LOW**")
    elif prediction == 2:
        st.info("🌻 **Predicted Crop Yield: MEDIUM**")
    else:
        st.write(f"Predicted Crop Yield Value: {prediction:.2f}")
