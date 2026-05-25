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
app = Flask(__name__)

ALLOWED_ORIGINS = {
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:5501",
    "http://localhost:5501"
}


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")

    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"

    return response


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


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Traffic Congestion Speed Prediction API Running"
    })


@app.route("/predictdata", methods=["POST", "OPTIONS"])
def predict():
    if request.method == "OPTIONS":
        return "", 204

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = [
            "location",
            "date",
            "time"
        ]

        missing_fields = [
            field for field in required_fields
            if field not in data
        ]

        if missing_fields:
            return jsonify({
                "error": f"Missing fields: {missing_fields}"
            }), 400

        location = data["location"]
        date = data["date"]
        time = data["time"]

        selected_date = datetime.strptime(date, "%Y-%m-%d").date()
        today = datetime.today().date()

        if selected_date < today:
            return jsonify({
                "error": "Past dates are not allowed. Enter today or future date."
            }), 400

        dt = datetime.strptime(
            f"{date} {time}",
            "%Y-%m-%d %H:%M"
        )

        lat, lng = get_coordinates(location)

        weather = fetch_weather_by_coords(
            latitude=lat,
            longitude=lng,
            date=date,
            time=time
        )

        input_data = CustomData(
            Start_Lat=lat,
            Start_Lng=lng,
            Humidity=weather["Humidity(%)"],
            Visibility=weather["Visibility(mi)"],
            Temperature=weather["Temperature(C)"],
            Start_hour=dt.hour,
            Start_minute=dt.minute,
            Start_month=dt.month,
            Start_day=dt.day,
            Weather_Conditions=weather["Weather_Conditions"],
            Severity=1
        )

        pred_df = input_data.get_datas_as_df()

        pipeline = PredictionPipeline()
        prediction = pipeline.predict(pred_df)

        prediction_map = {
            0: "Slow",
            1: "Moderate",
            2: "Fast"
        }

        prediction_result = prediction_map.get(
            int(prediction[0]),
            "Unknown"
        )

        return jsonify({
            "Traffic prediction": prediction_result,
            "coordinates": {
                "latitude": lat,
                "longitude": lng
            },
            "weather_used": weather,
            "status": "success"
        }), 200

    except ValueError as e:
        return jsonify({
            "error": f"Invalid datatype or date/time format: {str(e)}"
        }), 422

    except Exception as e:
        return jsonify({
            "error": f"Prediction failed: {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=8000
    )
