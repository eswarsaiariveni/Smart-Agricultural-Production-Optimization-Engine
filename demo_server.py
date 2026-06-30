from __future__ import annotations

from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs


BASE_DIR = Path(__file__).resolve().parent
FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

CROP_PROFILES = {
    "rice": (88, 45, 42, 24, 84, 6.6, 235),
    "maize": (78, 48, 20, 23, 62, 6.3, 82),
    "chickpea": (38, 68, 78, 18, 17, 7.2, 82),
    "kidneybeans": (22, 60, 20, 20, 22, 5.8, 105),
    "pigeonpeas": (21, 66, 22, 28, 48, 5.8, 150),
    "mothbeans": (22, 48, 21, 29, 53, 6.8, 51),
    "mungbean": (21, 47, 20, 29, 85, 6.7, 49),
    "blackgram": (40, 67, 19, 30, 65, 7.1, 68),
    "lentil": (18, 68, 19, 19, 64, 6.9, 46),
    "pomegranate": (18, 18, 40, 22, 90, 6.4, 108),
    "banana": (100, 82, 50, 27, 80, 6.1, 105),
    "mango": (20, 28, 30, 32, 50, 5.8, 95),
    "grapes": (23, 132, 200, 24, 82, 6.0, 70),
    "watermelon": (100, 12, 50, 25, 86, 6.5, 52),
    "muskmelon": (100, 18, 50, 28, 92, 6.4, 25),
    "apple": (20, 125, 200, 22, 91, 6.0, 110),
    "orange": (19, 16, 10, 23, 92, 7.0, 110),
    "papaya": (50, 60, 50, 33, 92, 6.7, 140),
    "coconut": (22, 18, 30, 27, 95, 5.9, 175),
    "cotton": (118, 46, 20, 24, 80, 6.8, 80),
    "jute": (78, 46, 40, 25, 79, 6.8, 175),
    "coffee": (105, 35, 35, 25, 58, 6.5, 160),
}

SCALES = (140, 145, 205, 44, 100, 10, 300)


def recommend(values: dict[str, float]) -> tuple[str, float]:
    sample = tuple(values[name] for name in FEATURES)
    scores = []
    for crop, profile in CROP_PROFILES.items():
        distance = sum(((sample[i] - profile[i]) / SCALES[i]) ** 2 for i in range(len(FEATURES)))
        scores.append((distance, crop))
    scores.sort()
    best_distance, crop = scores[0]
    confidence = max(0.52, min(0.97, 1 - best_distance * 1.7))
    return crop, confidence


def layout(title: str, body: str) -> bytes:
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
<header class="topbar">
<a class="brand" href="/"><span class="brand-mark">OC</span><span>OptiCrop</span></a>
<nav class="nav">
<a href="/">Home</a>
<a href="/about">About</a>
<a href="/findyourcrop">Find Your Crop</a>
<a href="/research">Research</a>
</nav>
</header>
<main>{body}</main>
</body>
</html>"""
    return html.encode("utf-8")


def home() -> bytes:
    body = """
<section class="hero">
<div class="hero-copy">
<p class="eyebrow">Smart Agricultural Production Optimization Engine</p>
<h1>Crop decisions powered by soil, climate, and model logic.</h1>
<p>Use the OptiCrop workflow to recommend crops, assess suitability, and support sustainable farm planning.</p>
<div class="hero-actions">
<a class="button primary" href="/findyourcrop">Start Prediction</a>
<a class="button secondary" href="/research">View Research Flow</a>
</div>
</div>
<div class="field-visual"><div class="sun"></div><div class="field-row row-one"></div><div class="field-row row-two"></div><div class="field-row row-three"></div><div class="sensor-card"><strong>NPK</strong><span>soil profile</span></div></div>
</section>
<section class="metrics"><article><strong>7</strong><span>Input features</span></article><article><strong>22</strong><span>Supported crops</span></article><article><strong>3</strong><span>Project scenarios</span></article></section>
"""
    return layout("OptiCrop", body)


def about() -> bytes:
    body = """
<section class="page-header"><p class="eyebrow">Project Overview</p><h1>OptiCrop supports smarter, more sustainable farming decisions.</h1><p>The system uses data-driven insights to help farmers, researchers, policymakers, and agricultural stakeholders understand crop-environment relationships.</p></section>
<section class="content-band"><div class="two-column"><article><h2>Problem Addressed</h2><p>Farmers often face losses when crop selection does not match soil nutrients, rainfall, temperature, humidity, or pH.</p></article><article><h2>Business Value</h2><p>The platform supports fertilizer and water planning, crop failure reduction, and agricultural policy decisions.</p></article></div></section>
"""
    return layout("About OptiCrop", body)


def form(defaults: dict[str, float] | None = None, result: dict | None = None) -> bytes:
    defaults = defaults or {"N": 90, "P": 42, "K": 43, "temperature": 21, "humidity": 82, "ph": 6.5, "rainfall": 203}
    inputs = "".join(
        f'<label>{name}<input type="number" name="{name}" value="{defaults[name]}" step="0.01" required></label>'
        for name in FEATURES
    )
    if result:
        panel = f"""
<p class="eyebrow">Recommendation</p><h2>{result['crop'].title()}</h2>
<div class="confidence"><span>Confidence</span><strong>{result['confidence']:.2f}%</strong></div>
<p>{result['crop'].title()} is the strongest recommendation for the supplied soil and climate profile.</p>
<dl><div><dt>Season Fit</dt><dd>{result['season']}</dd></div><div><dt>Generated</dt><dd>{result['generated_at']}</dd></div></dl>
<div class="recommendations"><h3>Recommendations</h3><p>{result['water_note']}</p><p>{result['ph_note']}</p></div>
"""
    else:
        panel = "<p class=\"eyebrow\">Assessment Output</p><h2>Awaiting field data</h2><p>Submit soil and climate values to generate a crop recommendation.</p>"
    body = f"""
<section class="tool-layout">
<form class="predict-form" action="/predict" method="post">
<div class="form-heading"><p class="eyebrow">Prediction Form</p><h1>Find Your Crop</h1></div>
<div class="input-grid">{inputs}</div>
<button class="button primary wide" type="submit">Predict Crop</button>
</form>
<aside class="result-panel">{panel}</aside>
</section>
"""
    return layout("Find Your Crop", body)


def research() -> bytes:
    body = """
<section class="page-header compact"><p class="eyebrow">Research Workflow</p><h1>Crop-environment analysis for agricultural planning.</h1></section>
<section class="timeline">
<article><h2>1. Data Collection and Analysis</h2><p>Analyze N, P, K, temperature, humidity, pH, rainfall, and crop labels.</p></article>
<article><h2>2. Data Preprocessing</h2><p>Check missing values, inspect outliers, and split data for training and testing.</p></article>
<article><h2>3. Model Building</h2><p>Compare machine learning models and save the best classifier for prediction.</p></article>
<article><h2>4. Policy Use</h2><p>Use recommendations for sustainable crop planning, water allocation, and fertilizer management.</p></article>
</section>
"""
    return layout("Research", body)


def notes(values: dict[str, float]) -> dict[str, str]:
    if values["rainfall"] > 180:
        water_note = "High rainfall conditions detected. Drainage planning is important."
    elif values["rainfall"] < 60:
        water_note = "Low rainfall conditions detected. Irrigation planning is recommended."
    else:
        water_note = "Rainfall is within a moderate cultivation range."

    if values["ph"] < 5.8:
        ph_note = "Soil is acidic. Lime treatment may improve nutrient availability."
    elif values["ph"] > 7.8:
        ph_note = "Soil is alkaline. Organic matter can help improve soil balance."
    else:
        ph_note = "Soil pH is broadly suitable for many crop types."

    if values["temperature"] >= 30 and values["humidity"] >= 55:
        season = "Summer"
    elif values["temperature"] <= 20 and values["humidity"] >= 35:
        season = "Winter"
    elif values["rainfall"] >= 180 and values["humidity"] >= 55:
        season = "Rainy"
    else:
        season = "Mixed"
    return {"water_note": water_note, "ph_note": ph_note, "season": season}


class Handler(BaseHTTPRequestHandler):
    def send_html(self, content: bytes) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_css(self, path: Path) -> None:
        content = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/css; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self) -> None:
        if self.path == "/static/css/styles.css":
            self.send_css(BASE_DIR / "static" / "css" / "styles.css")
            return

        routes = {
            "/": home,
            "/about": about,
            "/findyourcrop": form,
            "/research": research,
        }
        self.send_html(routes.get(self.path, home)())

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        data = parse_qs(self.rfile.read(length).decode("utf-8"))
        values = {name: float(data[name][0]) for name in FEATURES}
        crop, confidence = recommend(values)
        result = {
            "crop": crop,
            "confidence": confidence * 100,
            "generated_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
            **notes(values),
        }
        self.send_html(form(values, result))


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 5000), Handler)
    print("OptiCrop demo server running at http://127.0.0.1:5000")
    server.serve_forever()
