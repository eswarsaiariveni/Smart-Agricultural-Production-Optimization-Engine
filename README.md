# OptiCrop: Smart Agricultural Production Optimization Engine

OptiCrop is a Flask-based crop recommendation system that uses soil nutrients and environmental inputs to recommend a suitable crop for cultivation.

## Features

- Crop prediction from Nitrogen, Phosphorus, Potassium, temperature, humidity, pH, and rainfall.
- Machine learning training script with Logistic Regression and Random Forest comparison.
- Representative crop dataset generator when `data/Crop_recommendation.csv` is not present.
- Research view for dataset, preprocessing, model evaluation, and policy-planning context.
- SQL schema for the ER model: User, SoilData, Crop, Dataset, MLModel, Prediction, and Report.

## Setup

```powershell
python -m pip install -r requirements.txt
python train_model.py
python app.py
```

Open the local server URL shown in the terminal, usually `http://127.0.0.1:5000`.

## Deploy on Render

This repository includes `render.yaml` and `.python-version`, so Render uses a
Python version compatible with the pinned scientific packages.

1. Push the repository to GitHub.
2. In Render, choose **New > Blueprint** and connect the repository.
3. Render will install the dependencies, train the model, and start the app with
   Gunicorn.

For an existing Render Web Service, use:

```text
Build Command: pip install -r requirements.txt && python train_model.py
Start Command: gunicorn app:app
Health Check Path: /health
```

After pushing these files, use **Manual Deploy > Clear build cache & deploy**.

## GitHub Pages

The repository-root `index.html` is a static project homepage for GitHub Pages.
The crop prediction feature requires the Python/Flask backend and therefore must
be run locally or deployed to a Python-compatible hosting service.

## No-Dependency Demo

If your Python environment cannot install scientific packages, run the standard-library demo:

```powershell
python demo_server.py
```

It uses the same crop profiles and interface style, but predicts with a nearest-profile suitability score instead of the trained scikit-learn model.

## Dataset

The project supports the Kaggle crop recommendation dataset:

`https://www.kaggle.com/datasets/chitrakumari25/smart-agricultural-production-optimizing-engine`

If you download the Kaggle CSV manually, place it at:

`data/Crop_recommendation.csv`

The columns should be:

`N, P, K, temperature, humidity, ph, rainfall, label`

## Project Structure

```text
index.html
app.py
train_model.py
requirements.txt
schema.sql
data/
models/
templates/
static/css/
docs/
```

## Scenarios Covered

1. Smart crop recommendation for farmers.
2. Crop suitability and environmental assessment.
3. Agricultural research and policy planning.
