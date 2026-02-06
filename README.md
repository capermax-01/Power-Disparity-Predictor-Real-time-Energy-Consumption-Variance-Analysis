# Energy Consumption Prediction System

A complete machine learning pipeline for predicting appliance energy consumption using XGBoost and FastAPI.

## Project Structure

```
energy_waste_demo/
├── archive/                          # Original appliance CSV files
├── models/                           # Trained model artifacts
│   ├── xgb_energy_model.pkl         # Trained XGBoost model
│   ├── label_encoders.pkl           # Categorical encoders
│   └── feature_names.pkl            # Feature names
├── appliances_consolidated.db        # SQLite database with all appliance data
├── appliances_sample_100k.csv        # Sample of consolidated data
├── consolidate_appliances.py         # Script to consolidate archive CSVs
├── train_xgb_model.py               # Script to train XGBoost model
├── app.py                           # FastAPI application
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## Installation

### 1. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or manually install
pip install xgboost==1.7.6 fastapi==0.104.0 uvicorn==0.24.0 scikit-learn==1.3.0 joblib==1.3.0 pandas==2.0.0 numpy==1.24.0
```

### 2. Data Consolidation (Already Done)

The appliance data has been consolidated into a SQLite database:

```bash
python consolidate_appliances.py
```

This creates:
- `appliances_consolidated.db` - 213M records from 42 appliances
- `appliances_sample_100k.csv` - Sample data for analysis

**Database Summary:**
- **Total Records:** 213,395,522
- **Unique Appliances:** 42
- **Categories:** Kitchen, Multimedia, Washing, Other, Cooling
- **Time Range:** June 2020 - September 2021

## Training the Model

### 1. Train XGBoost Model

```bash
python train_xgb_model.py
```

**Process:**
1. Loads 100,000 records from database
2. Engineers 12 features from raw data
3. Trains XGBoost regressor with 200 estimators
4. Evaluates performance on test set
5. Saves model artifacts to `models/` directory

**Features Engineered:**
- Temporal: hour, day_of_week, day_of_month, month, quarter, is_weekend
- Categorical: appliance_id_encoded, appliance_category_encoded
- Power-based: power_max, power_ratio
- Statistical: power_rolling_mean_24, power_rolling_std_24

**Expected Performance:**
- RMSE: ~50-100W
- MAE: ~30-60W
- R²: 0.75-0.85

## Deploying the API

### 1. Start FastAPI Server

```bash
# Development server
python app.py

# Or with specific host/port
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Output:**
```
====================================================================
STARTING ENERGY PREDICTION API
====================================================================

API Documentation: http://localhost:8000/docs
API Health Check: http://localhost:8000/health
====================================================================
```

### 2. Access the API

**Swagger UI Documentation:**
```
http://localhost:8000/docs
```

**Health Check:**
```
http://localhost:8000/health
```

## API Endpoints

### 1. Health Check
```
GET /health
```
Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2026-02-06T12:00:00"
}
```

### 2. Model Information
```
GET /model/info
```
Response:
```json
{
  "model_type": "XGBoost Regressor",
  "n_estimators": 200,
  "max_depth": 8,
  "n_features": 12,
  "features": ["hour", "day_of_week", ...],
  "status": "ready"
}
```

### 3. Single Prediction
```
POST /predict
```

**Request:**
```json
{
  "appliance_id": "fridge_207",
  "appliance_category": "kitchen",
  "hour": 14,
  "day_of_week": 2,
  "day_of_month": 15,
  "month": 6,
  "quarter": 2,
  "is_weekend": 0,
  "power_max": 1500.0,
  "power_rolling_mean_24": 1000.0,
  "power_rolling_std_24": 200.0
}
```

**Response:**
```json
{
  "predicted_power_w": 1045.32,
  "confidence": 92.50,
  "timestamp": "2026-02-06T12:00:00"
}
```

### 4. Batch Prediction
```
POST /predict/batch
```

**Request:**
```json
{
  "predictions": [
    {
      "appliance_id": "fridge_207",
      "appliance_category": "kitchen",
      "hour": 14,
      ...
    },
    {
      "appliance_id": "washing_machine_32",
      "appliance_category": "washing",
      "hour": 15,
      ...
    }
  ]
}
```

**Response:**
```json
{
  "count": 2,
  "predictions": [
    {
      "appliance_id": "fridge_207",
      "predicted_power_w": 1045.32,
      "confidence": 92.50
    },
    {
      "appliance_id": "washing_machine_32",
      "predicted_power_w": 2150.45,
      "confidence": 88.20
    }
  ],
  "timestamp": "2026-02-06T12:00:00"
}
```

### 5. Daily Simulation
```
POST /simulate?appliance_id=fridge_207&category=kitchen&date=2021-06-15
```

**Response:**
```json
{
  "appliance_id": "fridge_207",
  "category": "kitchen",
  "date": "2021-06-15",
  "hourly_predictions": [
    {"hour": 0, "predicted_power_w": 950.25},
    {"hour": 1, "predicted_power_w": 945.30},
    ...
  ],
  "total_energy_kwh": 22.45
}
```

## Example Usage

### Using Python Requests

```python
import requests
import json

# API endpoint
url = "http://localhost:8000/predict"

# Prediction request
data = {
    "appliance_id": "fridge_207",
    "appliance_category": "kitchen",
    "hour": 14,
    "day_of_week": 2,
    "day_of_month": 15,
    "month": 6,
    "quarter": 2,
    "is_weekend": 0,
    "power_max": 1500.0,
    "power_rolling_mean_24": 1000.0,
    "power_rolling_std_24": 200.0
}

# Make request
response = requests.post(url, json=data)
prediction = response.json()

print(f"Predicted Power: {prediction['predicted_power_w']}W")
print(f"Confidence: {prediction['confidence']}%")
```

### Using cURL

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "appliance_id": "fridge_207",
    "appliance_category": "kitchen",
    "hour": 14,
    "day_of_week": 2,
    "day_of_month": 15,
    "month": 6,
    "quarter": 2,
    "is_weekend": 0,
    "power_max": 1500.0,
    "power_rolling_mean_24": 1000.0,
    "power_rolling_std_24": 200.0
  }'
```

## Model Details

### Model Type
- **Algorithm:** XGBoost Regression
- **Estimators:** 200
- **Max Depth:** 8
- **Learning Rate:** 0.05
- **Subsample:** 0.8
- **Colsample by Tree:** 0.8
- **Early Stopping:** Yes (20 rounds)

### Features (12 total)
1. **hour** (0-23) - Hour of day
2. **day_of_week** (0-6) - Day of week
3. **day_of_month** (1-31) - Day of month
4. **month** (1-12) - Month
5. **quarter** (1-4) - Quarter of year
6. **is_weekend** (0-1) - Weekend flag
7. **appliance_id_encoded** - Encoded appliance ID
8. **appliance_category_encoded** - Encoded category
9. **power_max** - Maximum power rating (W)
10. **power_ratio** - Current/Max power ratio
11. **power_rolling_mean_24** - 24h rolling average (W)
12. **power_rolling_std_24** - 24h rolling std dev (W)

### Target Variable
- **power_reading** - Actual power consumption (Watts)

## Deployment Options

### 1. Local Development
```bash
python app.py
```

### 2. Production with Gunicorn
```bash
pip install gunicorn
gunicorn app:app -w 4 -b 0.0.0.0:8000
```

### 3. Docker Deployment
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
COPY models/ models/
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4. Cloud Deployment (AWS, GCP, Azure)
- Containerize with Docker
- Deploy to AWS Lambda, Google Cloud Run, or Azure Container Instances
- Use the Swagger docs for API integration testing

## Performance Metrics

### Training Performance
- **Dataset:** 100,000 samples
- **Train/Test Split:** 80/20
- **Training Time:** ~2-3 minutes
- **Model Size:** ~5-10 MB

### API Performance
- **Inference Time:** <50ms per prediction
- **Throughput:** ~20+ predictions/second
- **Concurrent Requests:** Supports 100+ concurrent connections

## Troubleshooting

### Model not loading
```
Check that models/ directory exists and contains:
- xgb_energy_model.pkl
- label_encoders.pkl
- feature_names.pkl
```

### Prediction errors
- Ensure all required fields are provided
- Check that appliance_id and category are valid strings
- Verify numeric fields are within expected ranges

### Database connection issues
```bash
# Verify database exists
ls appliances_consolidated.db

# Or check database size
wc -c appliances_consolidated.db
```

## Next Steps

1. ✅ Consolidated appliance data (213M records)
2. ✅ Created XGBoost model
3. ✅ Built FastAPI application
4. 📋 Deploy to production
5. 📋 Set up monitoring and logging
6. 📋 Implement model versioning
7. 📋 Add batch prediction endpoint
8. 📋 Create dashboard for monitoring

## Support

For issues or questions:
1. Check the API documentation: `http://localhost:8000/docs`
2. Review error messages in API response
3. Check model training logs
4. Verify database integrity

## License

This project is for demonstration purposes.
