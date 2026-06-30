CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'farmer'
);

CREATE TABLE soil_data (
    soil_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    nitrogen REAL NOT NULL,
    phosphorus REAL NOT NULL,
    potassium REAL NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL,
    ph REAL NOT NULL,
    rainfall REAL NOT NULL,
    season TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE crops (
    crop_id INTEGER PRIMARY KEY AUTOINCREMENT,
    crop_name TEXT NOT NULL UNIQUE,
    crop_type TEXT,
    season TEXT,
    optimal_ph REAL,
    water_requirement TEXT
);

CREATE TABLE datasets (
    dataset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_name TEXT NOT NULL,
    source TEXT,
    total_records INTEGER,
    last_updated TEXT
);

CREATE TABLE ml_models (
    model_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_id INTEGER NOT NULL,
    model_name TEXT NOT NULL,
    algorithm TEXT NOT NULL,
    accuracy REAL,
    trained_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    model_path TEXT NOT NULL,
    FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id)
);

CREATE TABLE predictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    soil_id INTEGER NOT NULL UNIQUE,
    crop_id INTEGER NOT NULL,
    model_id INTEGER NOT NULL,
    prediction_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    confidence_score REAL NOT NULL,
    FOREIGN KEY (soil_id) REFERENCES soil_data(soil_id),
    FOREIGN KEY (crop_id) REFERENCES crops(crop_id),
    FOREIGN KEY (model_id) REFERENCES ml_models(model_id)
);

CREATE TABLE reports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_id INTEGER NOT NULL,
    generated_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    summary TEXT NOT NULL,
    recommendations TEXT NOT NULL,
    FOREIGN KEY (prediction_id) REFERENCES predictions(prediction_id)
);
