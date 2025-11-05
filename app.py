import streamlit as st
import pandas as pd
import hashlib
import os
import joblib

# -------------------------------
# ✅ Create data folder & define user file
# -------------------------------
DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)
USER_FILE = os.path.join(DATA_FOLDER, "users.csv")

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="🌾 Crop Yield Predictor", page_icon="🌱", layout="wide")

# -------------------------------
# User login/signup setup
# -------------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Load existing users or create empty CSV
if os.path.exists(USER_FILE):
    users_df = pd.read_csv(USER_FILE)
else:
    users_df = pd.DataFrame(columns=["username", "password"])
    users_df.to_csv(USER_FILE, index=False)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# -------------------------------
# Login / Signup Tabs
# -------------------------------
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Signup"])

    # -------- Signup Tab --------
    with tab2:
        st.subheader("Create a New Account")
        new_username = st.text_input("Username", key="signup_user").strip().lower()
        new_password = st.text_input("Password", type="password", key="signup_pass")
        new_password_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")

        if st.button("Signup"):
            if new_username in users_df["username"].values:
                st.error("❌ Username already exists!")
            elif new_password != new_password_confirm:
                st.error("❌ Passwords do not match!")
            elif new_username == "" or new_password == "":
                st.error("❌ Please fill all fields")
            else:
                new_row = pd.DataFrame([{"username": new_username, "password": hash_password(new_password)}])
                users_df = pd.concat([users_df, new_row], ignore_index=True)
                users_df.to_csv(USER_FILE, index=False)
                st.success("✅ Account created successfully! You can now login.")

    # -------- Login Tab --------
    with tab1:
        st.subheader("Login to Your Account")
        username = st.text_input("Username", key="login_user").strip().lower()
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            if username in users_df["username"].values:
                stored_hash = users_df.loc[users_df["username"] == username, "password"].values[0]
                if hash_password(password) == stored_hash:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"Welcome {username}! ✅")
                else:
                    st.error("❌ Incorrect password")
            else:
                st.error("❌ Username not found. Please signup first.")

# -------------------------------
# -------------------------------
# Crop Yield Predictor
# -------------------------------
if st.session_state.logged_in:
    st.title("🌾 Crop Yield Prediction System")
    st.markdown(
        f"Welcome **{st.session_state.username}**! Predict whether a crop will have **High 🌾 / Medium 🌤 / Low 🌱 yield**."
    )
    # Load dataset
    dataset_file = "your_dataset.csv"  # make sure this exists in your project folder
    df_original = pd.read_csv(dataset_file)
    df_original.columns = df_original.columns.str.strip().str.replace(r"\s+", " ", regex=True)

    # Crop Type mapping
    crop_map = {0: 'Cassava', 1: 'Maize', 2: 'Rice', 3: 'Soybean', 4: 'Yam'}
    crop_name_to_num = {v: k for k, v in crop_map.items()}
    df_original['Crop Type Num'] = df_original['Crop Type'].map(crop_name_to_num)

    # Round numeric columns
    numeric_cols = ['Rainfall', 'Temperature', 'Humidity', 'Soil pH',
                    'Soil Moisture', 'Nitrogen', 'Phosphorus', 'Potassium']
    df_original[numeric_cols] = df_original[numeric_cols].round(2)

    # Label map
    label_map = {0: 'High 🌾', 1: 'Low 🌱', 2: 'Medium 🌤'}

    # -------- Input Section --------
    st.subheader("Enter Input Parameters for Prediction:")
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_crop = st.selectbox("Select Crop Type", list(crop_name_to_num.keys()))
        rainfall = st.number_input("Rainfall (mm)", format="%.2f")
        temperature = st.number_input("Temperature (°C)", format="%.2f")
        humidity = st.number_input("Humidity (%)", format="%.2f")
    with col2:
        soil_pH = st.number_input("Soil pH", format="%.2f")
        soil_moisture = st.number_input("Soil Moisture (%)", format="%.2f")
        nitrogen = st.number_input("Nitrogen (kg/ha)", format="%.2f")
    with col3:
        phosphorus = st.number_input("Phosphorus (kg/ha)", format="%.2f")
        potassium = st.number_input("Potassium (kg/ha)", format="%.2f")

    # -------- Prediction Button --------
    if st.button("Predict Yield"):
        # Exact Lookup
        row_match = df_original[
            (df_original['Rainfall'] == round(rainfall, 2)) &
            (df_original['Temperature'] == round(temperature, 2)) &
            (df_original['Humidity'] == round(humidity, 2)) &
            (df_original['Soil pH'] == round(soil_pH, 2)) &
            (df_original['Soil Moisture'] == round(soil_moisture, 2)) &
            (df_original['Nitrogen'] == round(nitrogen, 2)) &
            (df_original['Phosphorus'] == round(phosphorus, 2)) &
            (df_original['Potassium'] == round(potassium, 2)) &
            (df_original['Crop Type Num'] == crop_name_to_num[selected_crop])
        ]

        if not row_match.empty:
            pred_label = row_match['Crop Yield'].values[0]
        else:
            # Random Forest fallback
            try:
                scaler = joblib.load("crop_yield_scaler.pkl")
                model = joblib.load("crop_yield_model.pkl")
                crop_type_num = crop_name_to_num[selected_crop]
                input_df = pd.DataFrame([[rainfall, temperature, humidity, soil_pH, soil_moisture,
                                          nitrogen, phosphorus, potassium, crop_type_num]],
                                        columns=['Rainfall', 'Temperature', 'Humidity', 'Soil pH', 'Soil Moisture',
                                                 'Nitrogen', 'Phosphorus', 'Potassium', 'Crop Type'])
                input_scaled = scaler.transform(input_df)
                pred_numeric = int(round(model.predict(input_scaled)[0]))
                pred_label = label_map[pred_numeric]
            except Exception as e:
                pred_label = f"Prediction failed: {e}"

        # -------- Display Result --------
        st.markdown("---")
        st.subheader("🎯 Predicted Crop Yield:")
        st.success(pred_label)
