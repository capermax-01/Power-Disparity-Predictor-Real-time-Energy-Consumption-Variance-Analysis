
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Database configuration
DB_PATH = BASE_DIR / "appliances_consolidated.db"
CSV_PATH = BASE_DIR / "appliances_consolidated.csv"
SAMPLE_CSV_PATH = BASE_DIR / "appliances_sample_100k.csv"
ARCHIVE_DIR = BASE_DIR / "archive"

# Model configuration
MODEL_DIR = BASE_DIR / "models"
ENERGY_MODEL_PATH = MODEL_DIR / "xgb_energy_model.pkl"
DISPARITY_MODEL_PATH = MODEL_DIR / "power_disparity_model.pkl"
SCALER_PATH = MODEL_DIR / "feature_scaler.pkl"
ENCODERS_PATH = MODEL_DIR / "label_encoders.pkl"
ENERGY_FEATURES_PATH = MODEL_DIR / "feature_names.pkl"
DISPARITY_FEATURES_PATH = MODEL_DIR / "feature_names.json"

# Training parameters
ENERGY_SAMPLE_SIZE = 100000
DISPARITY_SAMPLE_SIZE = 40000
TEST_SIZE = 0.2
RANDOM_STATE = 42
