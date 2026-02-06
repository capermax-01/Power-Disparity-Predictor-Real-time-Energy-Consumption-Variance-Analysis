# Setup & Deployment Guide

## Prerequisites
- Python 3.12+
- pip (Python package manager)

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/energy-waste-prediction.git
cd energy-waste-prediction
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the System

### Option A: Complete System (Backend + Dashboard)

#### Terminal 1 - Start Backend API
```bash
python3.12 serve_model.py
```
Server will run on: `http://localhost:8000`

#### Terminal 2 - Start HTTP Server
```bash
python3.12 -m http.server 8001
```
Dashboard will be at: `http://localhost:8001/dashboard.html`

### Option B: API Only (For External Applications)
```bash
python3.12 serve_model.py
```

Then make predictions via REST API:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "hour": 12,
    "day_of_week": 3,
    "day_of_month": 15,
    "month": 3,
    "is_weekend": 0,
    "appliance_id": "fridge_207",
    "appliance_category": "kitchen",
    "power_reading": 1000,
    "power_max": 1500,
    "power_std_6h": 50,
    "power_mean_6h": 950,
    "power_std_12h": 100,
    "power_mean_12h": 950,
    "power_std_24h": 150,
    "power_mean_24h": 900
  }'
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check API status |
| `/model/info` | GET | Get model metadata |
| `/appliances` | GET | List supported appliances |
| `/predict` | POST | Single prediction |
| `/predict/batch` | POST | Batch predictions |

## API Documentation
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Training New Model

To retrain the model with updated data:
```bash
python3.12 train_and_save_model.py
```

This will:
- Load training data from SQLite database
- Engineer 15 features
- Train GradientBoostingRegressor
- Save all artifacts to `models/` directory

## Database
The system uses SQLite database: `appliances_consolidated.db`

This database contains 213.4M records from 42 different appliances across 5 categories:
- Kitchen (Fridge, Oven, Microwave, etc.)
- Multimedia (TV, Computer, Printer, etc.)
- Washing (Washer, Dryer, etc.)
- Cooling (AC units)
- Other appliances

## Model Performance
- **R² Score**: 96.74%
- **RMSE**: 0.0184W
- **MAE**: 0.0078W
- **Training Samples**: 10,755
- **Features**: 15 engineered

## Troubleshooting

### Port Already in Use
If port 8000 or 8001 is already in use:

For Backend:
```bash
python3.12 serve_model.py --port 8002
```

For Dashboard:
```bash
python3.12 -m http.server 8002
```

### Model Not Loading
Ensure you have these files in `models/`:
- `power_disparity_model.pkl`
- `feature_scaler.pkl`
- `label_encoders.pkl`
- `feature_names.json`
- `model_metadata.json`

If missing, run:
```bash
python3.12 train_and_save_model.py
```

### Missing Dependencies
Reinstall all requirements:
```bash
pip install --upgrade -r requirements.txt
```

## File Structure
```
energy-waste-prediction/
├── dashboard.html                  # Web UI
├── serve_model.py                  # FastAPI backend
├── train_and_save_model.py         # Model training
├── models/                         # Trained model artifacts
│   ├── power_disparity_model.pkl
│   ├── feature_scaler.pkl
│   ├── label_encoders.pkl
│   ├── feature_names.json
│   └── model_metadata.json
├── appliances_consolidated.db      # SQLite database
├── requirements.txt                # Dependencies
├── README.md                       # Project documentation
└── SETUP.md                        # This file
```

## Support
For issues or questions, please open an issue on GitHub.

## License
MIT License - See LICENSE file for details
