"""
FastAPI Backend - Power Disparity Prediction Model Server
Serves predictions from the saved model with full REST API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional
import joblib
import json
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration
MODEL_DIR = Path(__file__).parent / "models"
app = FastAPI(
    title="Power Disparity Predictor API",
    description="Real-time power consumption disparity prediction",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model state
model = None
scaler = None
label_encoders = None
feature_names = None
model_ready = False

# Pydantic models
class PredictionRequest(BaseModel):
    hour: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0-6)")
    day_of_month: int = Field(..., ge=1, le=31, description="Day of month")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    is_weekend: int = Field(..., ge=0, le=1, description="Weekend flag (0/1)")
    appliance_id: str = Field(..., description="Appliance identifier")
    appliance_category: str = Field(..., description="Appliance category")
    power_reading: float = Field(..., gt=0, description="Current power reading (W)")
    power_max: float = Field(..., gt=0, description="Maximum power rating (W)")
    power_std_6h: float = Field(default=0, ge=0, description="6h rolling std dev")
    power_mean_6h: float = Field(default=0, ge=0, description="6h rolling mean")
    power_std_12h: float = Field(default=0, ge=0, description="12h rolling std dev")
    power_mean_12h: float = Field(default=0, ge=0, description="12h rolling mean")
    power_std_24h: float = Field(default=0, ge=0, description="24h rolling std dev")
    power_mean_24h: float = Field(default=0, ge=0, description="24h rolling mean")

class BatchPredictionRequest(BaseModel):
    predictions: List[PredictionRequest]

class PredictionResponse(BaseModel):
    predicted_disparity_w: float
    confidence: float
    risk_level: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    ready_for_predictions: bool

def load_model_artifacts():
    """Load saved model and artifacts"""
    global model, scaler, label_encoders, feature_names, model_ready
    
    try:
        if not MODEL_DIR.exists():
            print(f"❌ Model directory not found: {MODEL_DIR}")
            return False
        
        model_file = MODEL_DIR / "power_disparity_model.pkl"
        scaler_file = MODEL_DIR / "feature_scaler.pkl"
        encoders_file = MODEL_DIR / "label_encoders.pkl"
        features_file = MODEL_DIR / "feature_names.json"
        
        if not model_file.exists():
            print(f"❌ Model file not found: {model_file}")
            return False
        
        model = joblib.load(model_file)
        scaler = joblib.load(scaler_file)
        label_encoders = joblib.load(encoders_file)
        
        with open(features_file, 'r') as f:
            feature_names = json.load(f)
        
        model_ready = True
        
        print("✅ Model loaded successfully!")
        print(f"   Features: {len(feature_names)}")
        print(f"   Model Type: GradientBoostingRegressor")
        print(f"   Status: Ready for predictions")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

@app.on_event("startup")
async def startup():
    """Load model on server startup"""
    print("\n" + "="*80)
    print("POWER DISPARITY PREDICTION SERVER - STARTING")
    print("="*80)
    load_model_artifacts()
    print("="*80 + "\n")

@app.get("/", tags=["Info"])
async def root():
    """API root endpoint"""
    return {
        "api": "Power Disparity Prediction",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "health": "GET /health",
            "predict": "POST /predict",
            "batch_predict": "POST /predict/batch",
            "model_info": "GET /model/info"
        }
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "ready_for_predictions": model_ready
    }

@app.get("/model/info", tags=["Model"])
async def model_info():
    """Get model information"""
    if not model_ready:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_type": "GradientBoostingRegressor",
        "features": feature_names,
        "n_features": len(feature_names),
        "encoders": list(label_encoders.keys()),
        "status": "production",
        "capabilities": [
            "Predict power disparity (variance)",
            "Estimate consumption unpredictability",
            "Risk assessment for unstable loads",
            "Batch prediction support"
        ]
    }

def encode_input(request: PredictionRequest):
    """Encode categorical features"""
    try:
        # Encode appliance_id
        if 'appliance_id' in label_encoders:
            try:
                appliance_encoded = label_encoders['appliance_id'].transform([request.appliance_id])[0]
            except:
                # Use 0 if unknown
                appliance_encoded = 0
        else:
            appliance_encoded = 0
        
        # Encode appliance_category
        if 'appliance_category' in label_encoders:
            try:
                category_encoded = label_encoders['appliance_category'].transform([request.appliance_category])[0]
            except:
                category_encoded = 0
        else:
            category_encoded = 0
        
        # Create feature vector in correct order
        features = np.array([[
            request.hour,
            request.day_of_week,
            request.day_of_month,
            request.month,
            request.is_weekend,
            appliance_encoded,
            category_encoded,
            request.power_reading,
            request.power_max,
            request.power_std_6h,
            request.power_mean_6h,
            request.power_std_12h,
            request.power_mean_12h,
            request.power_std_24h,
            request.power_mean_24h
        ]])
        
        return features
    except Exception as e:
        raise ValueError(f"Error encoding features: {str(e)}")

@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict(request: PredictionRequest):
    """Single prediction endpoint"""
    if not model_ready:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Encode input
        features = encode_input(request)
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Make prediction
        prediction = model.predict(features_scaled)[0]
        
        # Ensure non-negative
        predicted_disparity = max(0, float(prediction))
        
        # Calculate confidence (0-100%)
        confidence = min(100, max(0, 100 * (1 - abs(predicted_disparity / (request.power_max + 1)))))
        
        # Determine risk level
        cv = (predicted_disparity / request.power_reading * 100) if request.power_reading > 0 else 0
        
        if cv > 80:
            risk_level = "HIGH"
        elif cv > 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return PredictionResponse(
            predicted_disparity_w=round(predicted_disparity, 2),
            confidence=round(confidence, 2),
            risk_level=risk_level,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

@app.post("/predict/batch", tags=["Predictions"])
async def batch_predict(batch_request: BatchPredictionRequest):
    """Batch prediction endpoint"""
    if not model_ready:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        results = []
        
        for request in batch_request.predictions:
            features = encode_input(request)
            features_scaled = scaler.transform(features)
            prediction = model.predict(features_scaled)[0]
            predicted_disparity = max(0, float(prediction))
            
            confidence = min(100, max(0, 100 * (1 - abs(predicted_disparity / (request.power_max + 1)))))
            cv = (predicted_disparity / request.power_reading * 100) if request.power_reading > 0 else 0
            
            if cv > 80:
                risk_level = "HIGH"
            elif cv > 40:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            results.append({
                "appliance_id": request.appliance_id,
                "predicted_disparity_w": round(predicted_disparity, 2),
                "confidence": round(confidence, 2),
                "risk_level": risk_level
            })
        
        return {
            "count": len(results),
            "predictions": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Batch prediction error: {str(e)}")

@app.get("/appliances", tags=["Reference"])
async def get_appliances():
    """Get list of known appliances and categories"""
    if not label_encoders or 'appliance_id' not in label_encoders:
        return {"appliances": [], "categories": []}
    
    appliances = label_encoders['appliance_id'].classes_.tolist()
    categories = label_encoders['appliance_category'].classes_.tolist() if 'appliance_category' in label_encoders else []
    
    return {
        "appliances": appliances,
        "categories": categories,
        "total_appliances": len(appliances),
        "total_categories": len(categories)
    }

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*80)
    print("STARTING POWER DISPARITY PREDICTION API")
    print("="*80)
    print("\nWeb Interface: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("\n" + "="*80 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
