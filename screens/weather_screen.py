import time
import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lcd")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rotary")))

from lcd.manager import LCDManager
from rotary.manager import RotaryEncoder

# Kochi, Kerala, India coordinates
LATITUDE = 9.93
LONGITUDE = 76.27
TIMEZONE = "Asia/Kolkata"

# Cache file
CACHE_FILE = "/tmp/timepi_weather.json"
CACHE_DURATION = 30 * 60  # 30 minutes in seconds

# ============================================================================
# WMO Weather Code Mapping
# https://www.open-meteo.com/en/docs
# ============================================================================

WMO_CODES = {
    0: "Clear",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Foggy",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Heavy drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Light snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Light showers",
    81: "Moderate showers",
    82: "Heavy showers",
    85: "Light snow shower",
    86: "Heavy snow shower",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with hail",
}

def get_wmo_description(code):
    """Return short description for WMO code, truncated to fit LCD."""
    desc = WMO_CODES.get(code, "Unknown")
    return desc[:18]  # Leave room for icons/prefix

def fetch_weather():
    """
    Fetch weather from Open-Meteo API.
    Returns: {"temp": float, "condition": str, "humidity": int, "timestamp": float}
    On error: returns None
    """
    try:
        import requests
    except ImportError:
        print("Warning: requests library not found. Install with: pip3 install requests")
        return None

    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={LATITUDE}"
            f"&longitude={LONGITUDE}"
            f"&current=temperature_2m,weathercode,relative_humidity_2m"
            f"&timezone={TIMEZONE}"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        current = data.get("current", {})

        temp = current.get("temperature_2m", 0)
        weather_code = current.get("weathercode", 0)
        humidity = current.get("relative_humidity_2m", 0)

        return {
            "temp": temp,
            "condition": get_wmo_description(weather_code),
            "humidity": humidity,
            "timestamp": time.time(),
        }
    except Exception as e:
        print(f"Weather fetch error: {e}")
        return None

def load_cached_weather():
    """
    Load weather from cache file if it exists and is fresh (<30 min old).
    Returns: dict if cache is valid, None otherwise.
    """
    if not os.path.exists(CACHE_FILE):
        return None

    try:
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)

        timestamp = data.get("timestamp", 0)
        age = time.time() - timestamp

        if age < CACHE_DURATION:
            return data
    except (json.JSONDecodeError, IOError):
        pass

    return None

def save_weather_cache(weather_data):
    """Save weather data to cache file."""
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(weather_data, f)
    except IOError as e:
        print(f"Failed to write weather cache: {e}")

def get_current_weather():
    """
    Get current weather: try cache first, fetch if stale, fallback gracefully.
    Returns: {"temp": float, "condition": str, "humidity": int}
    """
    # Try cache first
    cached = load_cached_weather()
    if cached:
        return cached

    # Cache miss or stale — fetch fresh
    fresh = fetch_weather()
    if fresh:
        save_weather_cache(fresh)
        return fresh

    # Fetch failed — return placeholder
    return {
        "temp": None,
        "condition": "No data",
        "humidity": None,
        "timestamp": time.time(),
    }

def main():
    lcd = LCDManager()
    rotary = RotaryEncoder()

    try:
        while True:
            weather = get_current_weather()

            # Line 0: Location + condition (truncated)
            condition = weather.get("condition", "Unknown")[:13]  # 7 chars for "Kochi  "
            lcd.write(f"Kochi  {condition}".ljust(20), line=0)

            # Line 1: Temperature
            temp = weather.get("temp")
            if temp is not None:
                temp_str = f"Temp: {temp:.1f}°C"
            else:
                temp_str = "Temp: --°C"
            lcd.write(temp_str.ljust(20), line=1)

            # Line 2: Humidity
            humidity = weather.get("humidity")
            if humidity is not None:
                humidity_str = f"Humidity: {humidity}%"
            else:
                humidity_str = "Humidity: --%"
            lcd.write(humidity_str.ljust(20), line=2)

            # Line 3: Instructions
            lcd.write("Press knob to exit".ljust(20), line=3)

            # Check for exit
            if rotary.read_button():
                raise KeyboardInterrupt

            # Update every 5 seconds (cache prevents hammer requests)
            for _ in range(50):
                if rotary.read_button():
                    raise KeyboardInterrupt
                time.sleep(0.1)

    except KeyboardInterrupt:
        pass
    finally:
        lcd.clear()
        rotary.cleanup()

if __name__ == "__main__":
    main()
