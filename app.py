import streamlit as st
import pickle
import pandas as pd
import os

# ---------------- LOAD MODEL ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = pickle.load(open(os.path.join(BASE_DIR, "predictor/model.pkl"), "rb"))
scaler = pickle.load(open(os.path.join(BASE_DIR, "predictor/scaler.pkl"), "rb"))
encoder = pickle.load(open(os.path.join(BASE_DIR, "predictor/encoder.pkl"), "rb"))

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

# ---------------- NAV ----------------
menu = st.sidebar.selectbox(
    "Navigation",
    ["🏠 Home", "📜 History","📈 EDA", "📂 Bulk Scanner"]#"📊 Dashboard"
)

# ================= HOME =================
if menu == "🏠 Home":

    st.title("🔥 SmartCalories Predictor")

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("Age", min_value=5, max_value=100, value=25,help="Enter age between 5–100")
        gender = st.selectbox("Gender", ["male", "female"])
        height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
        weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=70)

    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=300, value=30)
        heart_rate = st.number_input("Heart Rate", min_value=50, max_value=200, value=90)
        body_temp = st.number_input("Body Temp", min_value=35.0, max_value=42.0, value=37.0)
        activity_type = st.selectbox("Activity", ["Light", "Moderate", "Intense"])


    if st.button("Predict 🔥"):
        if age < 5 or age > 100:
            st.error("Age must be between 5 and 100")
            st.stop()

        if height < 100 or height > 250:
            st.error("Height must be realistic (100–250 cm)")
            st.stop()

        if weight < 30 or weight > 200:
            st.error("Weight must be realistic (30–200 kg)")
            st.stop()

        try:
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

            if result < 80:
                suggestion = "Low activity"
            elif result < 150:
                suggestion = "Moderate activity"
            else:
                suggestion = "High activity"

            st.session_state.history.append({
                "Calories": result,
                "Activity": activity_type,
                "Duration": duration
            })

            st.success(f"🔥 Calories Burned: {result}")
            st.info(f"💪 BMI: {bmi}")
            st.warning(f"💡 {suggestion}")

        except:
            st.error("Invalid input!")

# ================= HISTORY =================
elif menu == "📜 History":

    st.title("📜 History")

    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv)

        if st.button("Clear History"):
            st.session_state.history = []
    else:
        st.info("No history")

# ================= DASHBOARD =================
elif menu == "📊 Dashboard":

    st.title("📊 Dashboard")

    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total", len(df))
        col2.metric("Max", df["Calories"].max())
        col3.metric("Avg", round(df["Calories"].mean(), 2))

        st.line_chart(df["Calories"])
        st.bar_chart(df["Activity"].value_counts())

    else:
        st.info("No data")

# ================= EDA =================
elif menu == "📈 EDA":

    st.title("📈 EDA")

    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)

        st.dataframe(df)
        st.write(df.describe())
        st.bar_chart(df["Calories"])

    else:
        st.info("No data")

# ================= BULK =================
elif menu == "📂 Bulk Scanner":

    st.title("📂 Bulk Prediction")

    file = st.file_uploader("Upload CSV/Excel/JSON", type=["csv", "xlsx", "json"])

    if file:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(file)
        else:
            df = pd.read_json(file)

        try:
            encoded = encoder.transform(df[["Gender", "Activity_Type"]])
            encoded_df = pd.DataFrame(
                encoded,
                columns=encoder.get_feature_names_out(["Gender", "Activity_Type"])
            )

            df = df.drop(["Gender", "Activity_Type"], axis=1)
            df = pd.concat([df, encoded_df], axis=1)

            df = df.reindex(columns=feature_columns, fill_value=0)

            scaled = scaler.transform(df)
            df["Calories"] = model.predict(scaled)

            st.dataframe(df)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Result", csv)

        except:
            st.error("Invalid format")