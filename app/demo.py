import os
import streamlit as st
import requests

st.title("🏥 Readmission Predictor")

# Get API host from environment variable with a fallback default
default_api_host = os.getenv("API_HOST", "http://localhost:8000")

# Sidebar for host config
st.sidebar.header("API Endpoint Settings")
host = st.sidebar.text_input("API Host", default_api_host)

# Form inputs
st.header("Patient Features")
age = st.number_input("Age", min_value=0, max_value=120, value=65)
gender = st.selectbox("Gender", ["Unknown", "m", "f"])
race = st.selectbox(
    "Race", ["Unknown", "white", "native", "other", "hawaiian", "asian", "black"]
)
ethnicity = st.selectbox("Ethnicity", ["Unknown", "hispanic", "nonhispanic"])
has_diabetes = st.checkbox("Has Diabetes? (Doesn't seem to influence prediction)")
has_hypertension = st.checkbox(
    "Has Hypertension? (Doesn't seem to influence prediction)"
)
num_meds = st.number_input("Number of Medications", 0, 100, 5)
num_procedures = st.number_input("Number of Procedures", 0, 50, 2)

# Submit button
if st.button("Predict Readmission Probability"):
    data = {
        "age": age,
        "gender": gender,
        "race": race,
        "ethnicity": ethnicity,
        "has_diabetes": has_diabetes,
        "has_hypertension": has_hypertension,
        "num_meds": num_meds,
        "num_procedures": num_procedures,
    }

    try:
        response = requests.post(f"{host}/predict", json=data)
        if response.status_code == 200:
            st.success(
                f"Predicted Readmission Probability: {response.json()['readmission_probability']:.2%}"
            )
        else:
            st.error(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Request failed: {e}")
