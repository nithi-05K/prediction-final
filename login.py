import streamlit as st
import pandas as pd
import hashlib
import os
import webbrowser

st.set_page_config(page_title="🔒 Crop Yield Predictor Login / Signup", page_icon="🔑")

st.title("🔒 Crop Yield Predictor Login / Signup")

# -------------------------------
# Config
# -------------------------------
USER_FILE = "users.csv"

# Hash password function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Load existing users or create empty CSV
if os.path.exists(USER_FILE):
    users_df = pd.read_csv(USER_FILE)
else:
    users_df = pd.DataFrame(columns=["username", "password"])
    users_df.to_csv(USER_FILE, index=False)

# Tabs for Login and Signup
tab1, tab2 = st.tabs(["Login", "Signup"])

# -------------------------------
# Signup Tab
# -------------------------------
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
            # Add new user
            new_row = pd.DataFrame([{
                "username": new_username,
                "password": hash_password(new_password)
            }])
            users_df = pd.concat([users_df, new_row], ignore_index=True)
            users_df.to_csv(USER_FILE, index=False)
            st.success("✅ Account created successfully! You can now login.")

# -------------------------------
# Login Tab
# -------------------------------
with tab1:
    st.subheader("Login to Your Account")
    username = st.text_input("Username", key="login_user").strip().lower()
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        if username in users_df["username"].values:
            stored_hash = users_df.loc[users_df["username"] == username, "password"].values[0]
            if hash_password(password) == stored_hash:
                st.success(f"Welcome {username}! ✅")
                st.write("You can now open the Crop Yield Predictor.")

                if st.button("➡️ Go to Crop Yield Predictor"):
                    # Opens predictor in a new browser tab
                    webbrowser.open_new_tab("http://localhost:8502")  # Update if using a different port
            else:
                st.error("❌ Incorrect password")
        else:
            st.error("❌ Username not found. Please signup first.")
