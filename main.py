import requests
import csv
from datetime import datetime
from dotenv import load_dotenv
import os

# ================= LOAD API KEY =================
load_dotenv()
API_KEY = os.getenv("API_KEY")

# ================= COLOR OUTPUT =================
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    RESET = "\033[0m"

# ================= FORECAST MODE =================
def fetch_forecast(city):
    url = "http://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200:
            print("❌ Error:", data.get("message", "Unknown error"))
            return None

        return data

    except Exception as e:
        print("❌ Request failed:", e)
        return None


def process_forecast(data):
    temps = []
    humidity = []

    for entry in data["list"]:
        temps.append(entry["main"]["temp"])
        humidity.append(entry["main"]["humidity"])

    return {
        "max_temp": max(temps),
        "min_temp": min(temps),
        "avg_temp": sum(temps)/len(temps),
        "max_humidity": max(humidity)
    }


def generate_alerts_forecast(stats):
    alerts = []

    if stats["max_temp"] > 35:
        alerts.append(f"🔥 High Temperature Alert: {stats['max_temp']:.2f}°C")

    if stats["max_humidity"] > 80:
        alerts.append(f"💧 High Humidity Alert: {stats['max_humidity']}%")

    return alerts


def display_forecast(stats, alerts):
    print("\n" + "="*50)
    print("📊 FORECAST WEATHER REPORT")
    print("="*50)

    print(f"🌡️ Max Temp     : {stats['max_temp']:.2f} °C")
    print(f"❄️ Min Temp     : {stats['min_temp']:.2f} °C")
    print(f"📊 Avg Temp     : {stats['avg_temp']:.2f} °C")
    print(f"💧 Max Humidity : {stats['max_humidity']}%")

    print("\n" + "="*50)
    print("⚠️ WEATHER ALERTS")
    print("="*50)

    if alerts:
        for i, alert in enumerate(alerts, 1):
            print(f"{Colors.RED}{i}. {alert}{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}✅ No alerts. Weather is safe.{Colors.RESET}")


def save_report(stats):
    os.makedirs("reports", exist_ok=True)

    with open("reports/forecast_report.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Max Temp", "Min Temp", "Avg Temp", "Max Humidity"])
        writer.writerow([
            stats["max_temp"],
            stats["min_temp"],
            stats["avg_temp"],
            stats["max_humidity"]
        ])


def run_forecast_mode():
    print("\n📊 FORECAST MODE")

    city = input("Enter city name: ")

    data = fetch_forecast(city)
    if not data:
        return

    stats = process_forecast(data)
    alerts = generate_alerts_forecast(stats)

    display_forecast(stats, alerts)
    save_report(stats)

# ================= LIVE MODE =================
def fetch_live_weather(city):
    url = "http://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200:
            print("❌ Error:", data.get("message", "Unknown error"))
            return None

        return data

    except Exception as e:
        print("❌ Request failed:", e)
        return None


def process_live_weather(data):
    return {
        "temp": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["main"]
    }


def generate_alerts_live(weather):
    alerts = []

    if weather["temp"] > 35:
        alerts.append(f"🔥 High Temperature Alert: {weather['temp']}°C")

    if weather["humidity"] > 80:
        alerts.append(f"💧 High Humidity Alert: {weather['humidity']}%")

    if "Rain" in weather["condition"]:
        alerts.append("🌧️ Rain Alert: Carry umbrella!")

    return alerts


def display_live(weather, alerts):
    print("\n" + "="*50)
    print("🌍 LIVE WEATHER REPORT")
    print("="*50)

    print(f"🌡️ Current Temp : {weather['temp']} °C")
    print(f"💧 Humidity     : {weather['humidity']} %")
    print(f"☁️ Condition    : {weather['condition']}")

    print("\n" + "="*50)
    print("⚠️ WEATHER ALERTS")
    print("="*50)

    if alerts:
        for i, alert in enumerate(alerts, 1):
            print(f"{Colors.RED}{i}. {alert}{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}✅ No alerts. Weather is safe.{Colors.RESET}")


def run_live_mode():
    print("\n🌐 LIVE WEATHER MODE")

    city = input("Enter city name: ")

    data = fetch_live_weather(city)
    if not data:
        return

    weather = process_live_weather(data)
    alerts = generate_alerts_live(weather)

    display_live(weather, alerts)

# ================= MAIN =================
def main():
    print("\n" + "="*50)
    print("🌦️ WEATHER FORECAST & ALERT APPLICATION")
    print("="*50)

    print("\nSelect Mode:")
    print("1. Forecast Mode")
    print("2. Live Mode")

    choice = input("Enter choice (1/2): ")

    if choice == "1":
        run_forecast_mode()
    elif choice == "2":
        run_live_mode()
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()