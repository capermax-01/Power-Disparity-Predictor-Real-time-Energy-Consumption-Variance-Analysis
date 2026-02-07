# Unified Energy Prediction System

A refactored, high-performance machine learning pipeline for predicting appliance energy consumption and power disparity.

## Project Structure

```
energy_waste_demo/
├── research/                         # Research and analysis scripts
│   ├── comprehensive_disparity_analysis.py
│   └── predict_power_disparity.py
├── models/                           # Trained model artifacts
│   ├── xgb_energy_model.pkl         # Energy Prediction (XGBoost)
│   ├── power_disparity_model.pkl    # Power Disparity (GradientBoosting)
│   ├── label_encoders.pkl           # Categorical encoders
│   ├── feature_scaler.pkl           # Disparity model scaler
│   └── feature_names.pkl            # Feature lists
├── app.py                           # Unified FastAPI application
├── config.py                        # Centralized configuration
├── consolidate_data.py              # Data consolidation pipeline
├── train_energy.py                  # Energy model training
├── train_disparity.py               # Disparity model training
├── query_db.py                      # Database query utility
├── dashboard.html                   # Interactive monitoring dashboard
├── requirements.txt                 # Dependencies
└── README.md                        # This file
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the API

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Access the documentation at `http://localhost:8000/docs`.

### 3. Open the Dashboard

Open `dashboard.html` in any modern web browser to interact with the API.

## API Endpoints

### Energy Prediction
- `POST /predict/energy`: Predict power consumption (single or batch).
- `POST /simulate`: 24-hour energy consumption simulation.

### Power Disparity
- `POST /predict/disparity`: Predict power variance and stability risk (single or batch).

### System
- `GET /health`: System health and model status.
- `GET /model/info`: Detailed model architecture and features.

## Refactoring Highlights

- **Unified API**: Merged multiple servers into a single FastAPI app with `lifespan` management.
- **Vectorized Performance**: Batch predictions are now processed using NumPy/Pandas arrays, eliminating slow loops.
- **Centralized Config**: All paths and parameters are managed in `config.py`.
- **Debugged Logic**: Fixed target leakage in the energy model feature engineering.
- **Improved Maintainability**: Cleaned up the root directory and standardized script naming.
