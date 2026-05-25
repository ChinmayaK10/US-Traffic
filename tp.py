from flask import Flask, jsonify, request
import requests
from datetime import datetime
import re
import os
from src.prediction_pipeline.predict_output import (
    PredictionPipeline,
    CustomData
)
from dotenv import load_dotenv
load_dotenv()

def get_coordinates(location):
    API_KEY = os.getenv("OPENCAGE_API_KEY")

    url = "https://api.opencagedata.com/geocode/v1/json"

    params = {
        "q": location,
        "key": API_KEY,
        "limit": 1
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code != 200:
        raise Exception(f"OpenCage API Error: {data}")

    if "results" not in data or not data["results"]:
        raise Exception("Location not found")

    lat = data["results"][0]["geometry"]["lat"]
    lng = data["results"][0]["geometry"]["lng"]

    return lat, lng


def classify_weather(x):
    s = str(x).lower().strip()

    if re.search(r"thunder|t-storm|storm", s):
        return "thunderstorm"

    elif re.search(r"snow|sleet|ice|wintry|freezing|blizzard", s):
        return "snow"

    elif re.search(r"rain|drizzle|shower|precipitation", s):
        return "rain"

    elif re.search(r"fog|mist|haze|smoke", s):
        return "fog"

    elif re.search(r"windy|squalls|blowing|sandstorm|dust", s):
        return "windy"

    elif re.search(r"clear|fair|sunny", s):
        return "clear"

    elif re.search(r"cloud|cloudy|overcast|partly cloudy|mostly cloudy", s):
        return "cloudy"

    return "cloudy"


def fetch_weather_by_coords(latitude, longitude, date, time):
    API_KEY = os.getenv("VISUAL_CROSSING_API_KEY")

    location = f"{latitude},{longitude}"

    url = (
        "https://weather.visualcrossing.com/"
        "VisualCrossingWebServices/rest/services/"
        f"timeline/{location}/{date}"
    )

    params = {
        "key": API_KEY,
        "include": "hours",
        "unitGroup": "metric"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code != 200:
        raise Exception(f"Visual Crossing API Error: {data}")

    if "days" not in data or not data["days"]:
        raise Exception("Weather data not available")

    target_hour = time[:2]

    weather = next(
        (
            h for h in data["days"][0]["hours"]
            if h["datetime"].startswith(target_hour)
        ),
        None
    )

    if weather is None:
        raise Exception("Weather unavailable for selected time")

    visibility_km = weather.get("visibility", 0)
    visibility_mi = round(visibility_km * 0.621371, 2)

    return {
        "Humidity(%)": weather["humidity"],
        "Visibility(mi)": visibility_mi,
        "Temperature(C)": weather["temp"],
        "Wind Speed(km/h)": weather["windspeed"],
        "Weather_Conditions": classify_weather(weather["conditions"])
    }