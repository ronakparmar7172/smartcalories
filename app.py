import streamlit as st
import pickle
import pandas as pd
import os

# ---------------- LOAD MODEL ----------------


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    model = pickle.load(open(os.path.join(BASE_DIR, "predictor", "model.pkl"), "rb"))
    scaler = pickle.load(open(os.path.join(BASE_DIR, "predictor", "scaler.pkl"), "rb"))
    encoder = pickle.load(open(os.path.join(BASE_DIR, "predictor", "encoder.pkl"), "rb"))
except Exception as e:
    st.error(f"Error loading model: {e}")

feature_columns = [
    'Age', 'Height', 'Weight', 'Duration',
    'Heart_Rate', 'Body_Temp',
    'Gender_male',
    'Activity_Type_Light',
    'Activity_Type_Moderate'
]

# ---------------- SESSION ----------------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- UI CONFIG ----------------
st.set_page_config(page_title="SmartCalories", page_icon="🔥", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.big-title {font-size:40px; font-weight:bold; text-align:center;}
.card {background:#f5f5f5; padding:20px; border-radius:10px;}
</style>
""", unsafe_allow_html=True)

# ---------------- NAV ----------------
menu = st.sidebar.radio("Navigation", ["🏠 Home", "📜 History", "📊 Dashboard"])

# ================= HOME =================
if menu == "🏠 Home":

    st.markdown('<p class="big-title">🔥 SmartCalories Predictor</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        age = st.text_input("Age")
        gender = st.selectbox("Gender", ["male", "female"])
        height = st.text_input("Height (cm)")
        weight = st.text_input("Weight (kg)")

    with col2:
        duration = st.text_input("Duration (min)")
        heart_rate = st.text_input("Heart Rate")
        body_temp = st.text_input("Body Temp")
        activity_type = st.selectbox("Activity", ["Light", "Moderate", "Intense"])

    if st.button("Predict 🔥"):

        try:
            # Convert safely
            age = float(age or 0)
            height = float(height or 0)
            weight = float(weight or 0)
            duration = float(duration or 0)
            heart_rate = float(heart_rate or 0)
            body_temp = float(body_temp or 0)

            input_data = pd.DataFrame({
                "Age": [age],
                "Gender": [gender],
                "Height": [height],
                "Weight": [weight],
                "Duration": [duration],
                "Heart_Rate": [heart_rate],
                "Body_Temp": [body_temp],
                "Activity_Type": [activity_type]
            })

            encoded = encoder.transform(input_data[["Gender", "Activity_Type"]])
            encoded_df = pd.DataFrame(
                encoded,
                columns=encoder.get_feature_names_out(["Gender", "Activity_Type"])
            )

            input_data = input_data.drop(["Gender", "Activity_Type"], axis=1)
            input_data = pd.concat([input_data, encoded_df], axis=1)

            input_data = input_data.reindex(columns=feature_columns, fill_value=0)

            input_scaled = scaler.transform(input_data)

            prediction = model.predict(input_scaled)
            result = round(prediction[0], 2)

            bmi = round(weight / ((height / 100) ** 2), 2) if height > 0 else 0

            if result < 200:
                suggestion = "Low activity - Try increasing workout"
            elif result < 400:
                suggestion = "Moderate activity - Good job!"
            else:
                suggestion = "High activity - Excellent!"

            # Save history
            st.session_state.history.append({
                "Calories": result,
                "Activity": activity_type,
                "Duration": duration
            })

            # Output
            st.success(f"🔥 Calories Burned: {result}")
            st.info(f"💪 BMI: {bmi}")
            st.warning(f"💡 {suggestion}")

        except Exception as e:
            st.error("Invalid input! Please check values.")

# ================= HISTORY =================
elif menu == "📜 History":

    st.header("📜 Prediction History")

    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download History", csv, "history.csv")

        if st.button("🗑 Clear History"):
            st.session_state.history = []
            st.success("History cleared!")

    else:
        st.info("No history yet")

# ================= DASHBOARD =================
elif menu == "📊 Dashboard":

    st.header("📊 Dashboard")

    if st.session_state.history:

        df = pd.DataFrame(st.session_state.history)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total", len(df))
        col2.metric("Max", df["Calories"].max())
        col3.metric("Avg", round(df["Calories"].mean(), 2))

        st.line_chart(df["Calories"])

    else:
        st.info("No data available")