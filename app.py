
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from config import MODEL_DIR

# Models and artifacts
models = {}

class EnergyPredictionInput(BaseModel):
    appliance_id: str = Field(..., example="FRIDGE_1")
    appliance_category: str = Field(..., example="kitchen")
    hour: int = Field(..., ge=0, le=23)
    day_of_week: int = Field(..., ge=0, le=6)
    day_of_month: int = Field(..., ge=1, le=31)
    month: int = Field(..., ge=1, le=12)
    quarter: Optional[int] = None
    is_weekend: int = Field(..., ge=0, le=1)
    power_max: float = Field(..., gt=0)
    power_rolling_mean_24: float = 1000.0
    power_rolling_std_24: float = 500.0

class DisparityPredictionInput(BaseModel):
    appliance_id: str = Field(..., example="FRIDGE_1")
    appliance_category: str = Field(..., example="kitchen")
    hour: int = Field(..., ge=0, le=23)
    day_of_week: int = Field(..., ge=0, le=6)
    day_of_month: int = Field(..., ge=1, le=31)
    month: int = Field(..., ge=1, le=12)
    is_weekend: int = Field(..., ge=0, le=1)
    power_reading: float = Field(..., gt=0)
    power_max: float = Field(..., gt=0)
    power_std_6h: float = 0.0
    power_mean_6h: float = 0.0
    power_std_12h: float = 0.0
    power_mean_12h: float = 0.0
    power_std_24h: float = 0.0
    power_mean_24h: float = 0.0

def encode_features(data: List[Union[EnergyPredictionInput, DisparityPredictionInput]], model_type: str) -> pd.DataFrame:
    df = pd.DataFrame([item.dict() for item in data])

    # Common categorical encoding
    if "encoders" in models:
        for col in ["appliance_id", "appliance_category"]:
            if col in models["encoders"]:
                le = models["encoders"][col]
                # Handle unknown categories
                df[f"{col}_encoded"] = df[col].apply(
                    lambda x: le.transform([x])[0] if x in le.classes_ else 0
                )

    if model_type == "energy":
        # Calculate quarter if not provided
        if df["quarter"].isnull().any():
            df["quarter"] = (df["month"] - 1) // 3 + 1

        # Calculate power_ratio
        df["power_ratio"] = df["power_rolling_mean_24"] / (df["power_max"] + 1)

        # Return features in correct order
        return df[models["energy_features"]]

    elif model_type == "disparity":
        # Feature columns as expected by the model
        feature_cols = [
            'hour', 'day_of_week', 'day_of_month', 'month', 'is_weekend',
            'appliance_id_encoded', 'appliance_category_encoded',
            'power_reading', 'power_max',
            'power_std_6h', 'power_mean_6h',
            'power_std_12h', 'power_mean_12h',
            'power_std_24h', 'power_mean_24h'
        ]
        return df[feature_cols]

    return df

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load Energy model (XGBoost)
    try:
        energy_model_path = MODEL_DIR / "xgb_energy_model.pkl"
        energy_features_path = MODEL_DIR / "feature_names.pkl"
        if energy_model_path.exists():
            models["energy"] = joblib.load(energy_model_path)
            models["energy_features"] = joblib.load(energy_features_path)
            print("✓ Energy model loaded")
        else:
            print("⚠ Energy model artifacts missing")
    except Exception as e:
        print(f"✗ Error loading Energy model: {e}")

    # Load Disparity model (GradientBoosting)
    try:
        disparity_model_path = MODEL_DIR / "power_disparity_model.pkl"
        disparity_scaler_path = MODEL_DIR / "feature_scaler.pkl"
        if disparity_model_path.exists():
            models["disparity"] = joblib.load(disparity_model_path)
            models["disparity_scaler"] = joblib.load(disparity_scaler_path)
            print("✓ Disparity model loaded")
        else:
            print("⚠ Disparity model artifacts missing")
    except Exception as e:
        print(f"✗ Error loading Disparity model: {e}")

    # Load common encoders
    try:
        encoders_path = MODEL_DIR / "label_encoders.pkl"
        if encoders_path.exists():
            models["encoders"] = joblib.load(encoders_path)
            print("✓ Categorical encoders loaded")
        else:
            print("⚠ Label encoders missing")
    except Exception as e:
        print(f"✗ Error loading encoders: {e}")

    yield
    # Clean up if needed
    models.clear()

app = FastAPI(
    title="Unified Energy API",
    description="Unified API for Energy Consumption and Power Disparity Prediction",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "online",
        "models_loaded": [k for k in models.keys() if not k.endswith("_features") and not k.endswith("_scaler")],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/model/info", tags=["System"])
async def model_info():
    return {
        "energy_model": {
            "loaded": "energy" in models,
            "type": "XGBoost Regressor",
            "features": models.get("energy_features", [])
        },
        "disparity_model": {
            "loaded": "disparity" in models,
            "type": "GradientBoosting Regressor"
        }
    }

@app.post("/predict/energy", tags=["Predictions"])
async def predict_energy(inputs: Union[EnergyPredictionInput, List[EnergyPredictionInput]]):
    if "energy" not in models:
        raise HTTPException(status_code=503, detail="Energy model not loaded")

    is_batch = isinstance(inputs, list)
    data_list = inputs if is_batch else [inputs]
    
    try:
        start_time = datetime.now()
        features_df = encode_features(data_list, "energy")
        predictions = models["energy"].predict(features_df)
        
        results = []
        for i, pred in enumerate(predictions):
            pred_val = max(0, float(pred))
            power_max = data_list[i].power_max
            confidence = min(100, max(0, 100 - abs(pred_val - power_max) / power_max * 50))

            results.append({
                "appliance_id": data_list[i].appliance_id,
                "predicted_power_w": round(pred_val, 2),
                "confidence": round(confidence, 2)
            })
        
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            "results": results if is_batch else results[0],
            "count": len(results),
            "latency_ms": round(latency_ms, 2),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

@app.post("/predict/disparity", tags=["Predictions"])
async def predict_disparity(inputs: Union[DisparityPredictionInput, List[DisparityPredictionInput]]):
    if "disparity" not in models:
        raise HTTPException(status_code=503, detail="Disparity model not loaded")

    is_batch = isinstance(inputs, list)
    data_list = inputs if is_batch else [inputs]
    
    try:
        start_time = datetime.now()
        features_df = encode_features(data_list, "disparity")
        
        # Scaling
        features_scaled = models["disparity_scaler"].transform(features_df)
        predictions = models["disparity"].predict(features_scaled)

        results = []
        for i, pred in enumerate(predictions):
            pred_val = max(0, float(pred))
            power_reading = data_list[i].power_reading
            power_max = data_list[i].power_max

            confidence = min(100, max(0, 100 * (1 - abs(pred_val / (power_max + 1)))))
            cv = (pred_val / power_reading * 100) if power_reading > 0 else 0
            
            risk_level = "HIGH" if cv > 80 else ("MEDIUM" if cv > 40 else "LOW")
            
            results.append({
                "appliance_id": data_list[i].appliance_id,
                "predicted_disparity_w": round(pred_val, 2),
                "confidence": round(confidence, 2),
                "risk_level": risk_level
            })

        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        return {
            "results": results if is_batch else results[0],
            "count": len(results),
            "latency_ms": round(latency_ms, 2),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

@app.post("/simulate", tags=["Simulation"])
async def simulate_hourly(appliance_id: str, category: str, date: str = "2021-06-15"):
    if "energy" not in models:
        raise HTTPException(status_code=503, detail="Energy model not loaded")
    
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        day_of_week = date_obj.weekday()
        day_of_month = date_obj.day
        month = date_obj.month
        is_weekend = 1 if day_of_week >= 5 else 0
        
        # Prepare batch for 24 hours
        simulation_inputs = [
            EnergyPredictionInput(
                appliance_id=appliance_id,
                appliance_category=category,
                hour=h,
                day_of_week=day_of_week,
                day_of_month=day_of_month,
                month=month,
                is_weekend=is_weekend,
                power_max=2500.0,
                power_rolling_mean_24=1000.0,
                power_rolling_std_24=500.0
            ) for h in range(24)
        ]

        features_df = encode_features(simulation_inputs, "energy")
        predictions = models["energy"].predict(features_df)

        hourly_results = [
            {"hour": h, "predicted_power_w": round(max(0, float(predictions[h])), 2)}
            for h in range(24)
        ]

        total_energy_kwh = sum(p["predicted_power_w"] for p in hourly_results) / 1000
        
        return {
            "appliance_id": appliance_id,
            "category": category,
            "date": date,
            "hourly_predictions": hourly_results,
            "total_energy_kwh": round(total_energy_kwh, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Simulation error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
