"""
FastAPI application for XGBoost energy prediction model
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import joblib
import numpy as np
import xgboost as xgb
from pathlib import Path
import json
from datetime import datetime

# Get model directory
MODEL_DIR = Path(__file__).parent / "models"

# Initialize FastAPI app
app = FastAPI(
    title="Energy Consumption Predictor",
    description="XGBoost-based appliance energy consumption prediction API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for loaded model
model = None
label_encoders = None
feature_names = None


class PredictionInput(BaseModel):
    """Input schema for prediction"""
    appliance_id: str = Field(..., example="FRIDGE_1")
    appliance_category: str = Field(..., example="kitchen")
    hour: int = Field(..., ge=0, le=23, example=14)
    day_of_week: int = Field(..., ge=0, le=6, example=2)
    day_of_month: int = Field(..., ge=1, le=31, example=15)
    month: int = Field(..., ge=1, le=12, example=6)
    quarter: int = Field(..., ge=1, le=4, example=2)
    is_weekend: int = Field(..., ge=0, le=1, example=0)
    power_max: float = Field(..., gt=0, example=2500.0)
    power_rolling_mean_24: Optional[float] = Field(default=1000.0, gt=0)
    power_rolling_std_24: Optional[float] = Field(default=500.0, ge=0)


class BatchPredictionInput(BaseModel):
    """Input schema for batch predictions"""
    predictions: List[PredictionInput]


class PredictionOutput(BaseModel):
    """Output schema for predictions"""
    predicted_power_w: float
    confidence: float
    timestamp: str


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    timestamp: str


def load_model_artifacts():
    """Load model and artifacts on startup"""
    global model, label_encoders, feature_names
    
    try:
        model_path = MODEL_DIR / "xgb_energy_model.pkl"
        encoders_path = MODEL_DIR / "label_encoders.pkl"
        features_path = MODEL_DIR / "feature_names.pkl"
        
        if not model_path.exists():
            print(f"⚠ Model not found at {model_path}")
            return False
        
        model = joblib.load(model_path)
        label_encoders = joblib.load(encoders_path)
        feature_names = joblib.load(features_path)
        
        print(f"✓ Model loaded successfully")
        print(f"  Features: {len(feature_names)}")
        print(f"  Encoders: {list(label_encoders.keys())}")
        
        return True
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return False


@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    if load_model_artifacts():
        print("✓ API ready for predictions")
    else:
        print("⚠ API starting but model not loaded")


@app.get("/", tags=["Info"])
async def root():
    """Root endpoint"""
    return {
        "name": "Energy Consumption Predictor API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "predict_single": "/predict",
            "predict_batch": "/predict/batch",
            "model_info": "/model/info"
        }
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/model/info", tags=["Model"])
async def model_info():
    """Get model information"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_type": "XGBoost Regressor",
        "n_estimators": model.n_estimators,
        "max_depth": model.max_depth,
        "features": feature_names,
        "n_features": len(feature_names),
        "encoders": list(label_encoders.keys()),
        "status": "ready"
    }


def encode_input(input_data: PredictionInput) -> np.ndarray:
    """Encode input data for prediction"""
    try:
        # Encode categorical features
        appliance_id_encoded = label_encoders['appliance_id'].transform(
            [input_data.appliance_id]
        )[0]
        
        try:
            appliance_category_encoded = label_encoders['appliance_category'].transform(
                [input_data.appliance_category]
            )[0]
        except:
            # If category not in encoder, use most common (0)
            appliance_category_encoded = 0
        
        # Calculate power_ratio
        power_ratio = input_data.power_rolling_mean_24 / (input_data.power_max + 1)
        
        # Create feature vector in correct order
        features = np.array([[
            input_data.hour,
            input_data.day_of_week,
            input_data.day_of_month,
            input_data.month,
            input_data.quarter,
            input_data.is_weekend,
            appliance_id_encoded,
            appliance_category_encoded,
            input_data.power_max,
            power_ratio,
            input_data.power_rolling_mean_24,
            input_data.power_rolling_std_24
        ]])
        
        return features
    except Exception as e:
        raise ValueError(f"Error encoding features: {str(e)}")


@app.post("/predict", response_model=PredictionOutput, tags=["Predictions"])
async def predict(input_data: PredictionInput):
    """Predict energy consumption for a single appliance"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Encode input
        features = encode_input(input_data)
        
        # Make prediction
        prediction = model.predict(features)[0]
        
        # Ensure positive prediction
        predicted_power = max(0, float(prediction))
        
        # Simple confidence score (0-100)
        # Based on prediction within typical range
        confidence = min(100, max(0, 100 - abs(predicted_power - input_data.power_max) / input_data.power_max * 50))
        
        return PredictionOutput(
            predicted_power_w=round(predicted_power, 2),
            confidence=round(confidence, 2),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")


@app.post("/predict/batch", tags=["Predictions"])
async def predict_batch(batch_input: BatchPredictionInput):
    """Predict energy consumption for multiple appliances"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        results = []
        
        for input_data in batch_input.predictions:
            # Encode input
            features = encode_input(input_data)
            
            # Make prediction
            prediction = model.predict(features)[0]
            predicted_power = max(0, float(prediction))
            confidence = min(100, max(0, 100 - abs(predicted_power - input_data.power_max) / input_data.power_max * 50))
            
            results.append({
                "appliance_id": input_data.appliance_id,
                "predicted_power_w": round(predicted_power, 2),
                "confidence": round(confidence, 2)
            })
        
        return {
            "count": len(results),
            "predictions": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Batch prediction error: {str(e)}")


@app.post("/simulate", tags=["Simulation"])
async def simulate_hourly(appliance_id: str, category: str, date: str = "2021-06-15"):
    """Simulate predictions for an entire day (24 hours)"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        from datetime import datetime as dt
        
        date_obj = dt.strptime(date, "%Y-%m-%d")
        day_of_week = date_obj.weekday()
        day_of_month = date_obj.day
        month = date_obj.month
        quarter = (month - 1) // 3 + 1
        is_weekend = 1 if day_of_week >= 5 else 0
        
        hourly_predictions = []
        
        for hour in range(24):
            input_data = PredictionInput(
                appliance_id=appliance_id,
                appliance_category=category,
                hour=hour,
                day_of_week=day_of_week,
                day_of_month=day_of_month,
                month=month,
                quarter=quarter,
                is_weekend=is_weekend,
                power_max=2500.0,
                power_rolling_mean_24=1000.0,
                power_rolling_std_24=500.0
            )
            
            features = encode_input(input_data)
            prediction = model.predict(features)[0]
            
            hourly_predictions.append({
                "hour": hour,
                "predicted_power_w": round(max(0, float(prediction)), 2)
            })
        
        return {
            "appliance_id": appliance_id,
            "category": category,
            "date": date,
            "hourly_predictions": hourly_predictions,
            "total_energy_kwh": round(sum([p["predicted_power_w"] for p in hourly_predictions]) / 1000, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Simulation error: {str(e)}")


@app.get("/docs", include_in_schema=False)
async def get_docs():
    """Swagger UI documentation"""
    pass


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("STARTING ENERGY PREDICTION API")
    print("="*70)
    print("\nAPI Documentation: http://localhost:8000/docs")
    print("API Health Check: http://localhost:8000/health")
    print("="*70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
