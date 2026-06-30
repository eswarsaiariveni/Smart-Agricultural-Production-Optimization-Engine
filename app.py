from __future__ import annotations

from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
from flask import Flask, render_template, request


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "model.pkl"
FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]


app = Flask(__name__)


def load_model_bundle() -> dict:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Model file not found. Run `python train_model.py` before starting the app."
        )
    return joblib.load(MODEL_PATH)


def crop_insights(crop: str, values: dict[str, float], confidence: float) -> dict:
    rainfall = values["rainfall"]
    ph = values["ph"]
    temperature = values["temperature"]
    humidity = values["humidity"]

    if rainfall > 180:
        water_note = "High rainfall conditions detected. Drainage planning is important."
    elif rainfall < 60:
        water_note = "Low rainfall conditions detected. Irrigation planning is recommended."
    else:
        water_note = "Rainfall is within a moderate cultivation range."

    if ph < 5.8:
        ph_note = "Soil is acidic. Lime treatment may improve nutrient availability."
    elif ph > 7.8:
        ph_note = "Soil is alkaline. Organic matter can help improve soil balance."
    else:
        ph_note = "Soil pH is broadly suitable for many crop types."

    if temperature >= 30 and humidity >= 55:
        season = "summer"
    elif temperature <= 20 and humidity >= 35:
        season = "winter"
    elif rainfall >= 180 and humidity >= 55:
        season = "rainy"
    else:
        season = "mixed"

    return {
        "crop": crop.title(),
        "confidence": round(confidence * 100, 2),
        "season": season.title(),
        "summary": f"{crop.title()} is the strongest recommendation for the supplied soil and climate profile.",
        "water_note": water_note,
        "ph_note": ph_note,
        "productivity": "High" if confidence >= 0.75 else "Moderate",
    }


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/findyourcrop")
def findyourcrop():
    defaults = {
        "N": 90,
        "P": 42,
        "K": 43,
        "temperature": 21,
        "humidity": 82,
        "ph": 6.5,
        "rainfall": 203,
    }
    return render_template("findyourcrop.html", defaults=defaults, result=None)


@app.route("/research")
def research():
    return render_template("research.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        values = {feature: float(request.form[feature]) for feature in FEATURES}
    except (KeyError, ValueError):
        defaults = {feature: request.form.get(feature, "") for feature in FEATURES}
        return render_template(
            "findyourcrop.html",
            defaults=defaults,
            result=None,
            error="Please enter valid numeric values for all crop parameters.",
        )

    bundle = load_model_bundle()
    model = bundle["model"]
    label_encoder = bundle["label_encoder"]

    sample = np.array([[values[feature] for feature in FEATURES]])
    predicted_label = model.predict(sample)[0]
    probabilities = model.predict_proba(sample)[0]
    confidence = float(np.max(probabilities))
    crop = label_encoder.inverse_transform([predicted_label])[0]

    result = crop_insights(crop, values, confidence)
    result["generated_at"] = datetime.now().strftime("%d %b %Y, %I:%M %p")
    result["inputs"] = values

    return render_template("findyourcrop.html", defaults=values, result=result)


if __name__ == "__main__":
    app.run(debug=True)
