import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os

# ================= LOAD API KEY =================
load_dotenv()
API_KEY = os.getenv("API_KEY")

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Weather Intelligence Dashboard", layout="wide")

st.title("🌦️ Weather Intelligence Dashboard")

# ================= SIDEBAR =================
mode = st.sidebar.radio(
    "📊 Select Mode",
    ["Live Weather", "Forecast", "Compare Cities", "Insights"]
)

city = st.sidebar.text_input("📍 Enter City", "Pune")

# ================= API FUNCTIONS =================
def get_live_weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    return requests.get(url, params=params).json()

def get_forecast(city):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    return requests.get(url, params=params).json()

# ================= FIXED DANGER ENGINE =================
def danger_score(temp, humidity, condition):
    score = 0

    # 🌡️ Temperature risk
    if temp >= 45:
        score += 4
    elif temp >= 40:
        score += 3
    elif temp >= 35:
        score += 2
    elif temp >= 30:
        score += 1

    # 💧 Humidity risk
    if humidity >= 85:
        score += 3
    elif humidity >= 70:
        score += 2
    elif humidity >= 55:
        score += 1

    # 🌧️ Weather condition risk
    condition = condition.lower()
    if "thunder" in condition:
        score += 4
    elif "storm" in condition:
        score += 4
    elif "rain" in condition:
        score += 3
    elif "cloud" in condition:
        score += 1

    return score

def risk_label(score):
    if score <= 2:
        return "🟢 SAFE"
    elif score <= 5:
        return "🟡 MODERATE"
    else:
        return "🔴 DANGEROUS"

# ================= LIVE WEATHER =================
if mode == "Live Weather":

    if st.button("🚀 Get Live Weather"):

        data = get_live_weather(city)

        if "main" in data:

            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            cond = data["weather"][0]["main"]

            col1, col2, col3 = st.columns(3)
            col1.metric("🌡️ Temp", f"{temp}°C")
            col2.metric("💧 Humidity", f"{humidity}%")
            col3.metric("☁️ Condition", cond)

            df = pd.DataFrame({
                "Metric": ["Temperature", "Humidity"],
                "Value": [temp, humidity]
            })

            fig = px.bar(df, x="Metric", y="Value", color="Metric", title="Live Weather Overview")
            st.plotly_chart(fig, use_container_width=True)

            st.success(f"{city}: {cond} with {temp}°C temperature")

        else:
            st.error("Error fetching live weather")

# ================= FORECAST =================
elif mode == "Forecast":

    if st.button("🚀 Get Forecast"):

        data = get_forecast(city)

        if "list" in data:

            times = []
            temps = []
            humidity = []

            for i in data["list"]:
                times.append(i["dt_txt"])
                temps.append(i["main"]["temp"])
                humidity.append(i["main"]["humidity"])

            df = pd.DataFrame({
                "Time": times,
                "Temperature": temps,
                "Humidity": humidity
            })

            st.subheader("📊 Temperature Forecast")

            fig = px.line(df, x="Time", y="Temperature", markers=True)
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("💧 Humidity Forecast")

            fig2 = px.line(df, x="Time", y="Humidity", markers=True)
            st.plotly_chart(fig2, use_container_width=True)

            st.write("🔥 Max Temp:", df["Temperature"].max())
            st.write("❄️ Min Temp:", df["Temperature"].min())
            st.write("📊 Avg Temp:", round(df["Temperature"].mean(), 2))

        else:
            st.error("Forecast data not available")

# ================= COMPARE =================
elif mode == "Compare Cities":

    cities = st.multiselect(
        "Select Cities",
        ["Pune", "Mumbai", "Delhi", "Bangalore", "Chennai"],
        default=["Pune", "Mumbai"]
    )

    if st.button("🚀 Compare"):

        results = []

        for c in cities:
            data = get_live_weather(c)

            if "main" in data:

                temp = data["main"]["temp"]
                humidity = data["main"]["humidity"]
                cond = data["weather"][0]["main"]

                score = danger_score(temp, humidity, cond)

                results.append({
                    "City": c,
                    "Temp": temp,
                    "Humidity": humidity,
                    "Condition": cond,
                    "Score": score,
                    "Risk": risk_label(score)
                })

        df = pd.DataFrame(results)

        st.subheader("📊 Comparison Table")
        st.dataframe(df, use_container_width=True)

        fig = px.bar(df, x="City", y="Temp", color="Temp", title="Temperature Comparison")
        st.plotly_chart(fig, use_container_width=True)

# ================= INSIGHTS =================
elif mode == "Insights":

    cities = ["Pune", "Mumbai", "Delhi"]

    results = []

    for c in cities:
        data = get_live_weather(c)

        if "main" in data:

            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            cond = data["weather"][0]["main"]

            score = danger_score(temp, humidity, cond)

            results.append({
                "City": c,
                "Temp": temp,
                "Humidity": humidity,
                "Score": score
            })

    df = pd.DataFrame(results)

    st.subheader("⚠️ Risk Gauge")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=df["Score"].mean(),
        title={"text": "Weather Risk Index"},
        gauge={
            "axis": {"range": [0, 8]},
            "steps": [
                {"range": [0, 2], "color": "green"},
                {"range": [2, 5], "color": "yellow"},
                {"range": [5, 8], "color": "red"}
            ]
        }
    ))

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True)