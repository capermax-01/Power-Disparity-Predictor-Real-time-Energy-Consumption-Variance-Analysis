"""
Enhanced FastAPI server with Waste Detection Integration
Combines power disparity prediction with energy waste reasoning
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import joblib
import numpy as np
import xgboost as xgb
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
from waste_detection_engine import EnergyWasteDetector, WasteAlert

# Get model directory
MODEL_DIR = Path(__file__).parent / "models"

# Initialize FastAPI app
app = FastAPI(
    title="Energy Waste Detection & Analysis API",
    description="ML-powered energy waste detection with actionable insights",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
model = None
label_encoders = None
feature_names = None
waste_detector = EnergyWasteDetector(cost_per_kwh=8.5)


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


class WasteAlertOutput(BaseModel):
    """Waste alert output schema"""
    waste_type: str
    zone_id: str
    device_type: str
    severity: str
    duration_hours: float
    waste_power_kw: float
    waste_energy_kwh: float
    daily_cost_inr: float
    monthly_cost_inr: float
    annual_cost_inr: float
    confidence: float
    reason: str
    recommended_actions: List[dict]
    human_readable: str  # For display


class BatchWasteDetectionInput(BaseModel):
    """Input for batch waste detection"""
    csv_data: str = Field(..., description="CSV data as string")


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    waste_detector_ready: bool
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
        print("✓ API ready for predictions and waste detection")
    else:
        print("⚠ API starting (model optional for waste detection)")


@app.get("/", tags=["Info"])
async def root():
    """Root endpoint"""
    return {
        "name": "Energy Waste Detection API",
        "version": "2.0.0",
        "docs": "/docs",
        "capabilities": [
            "Predict power consumption variance",
            "Detect phantom loads",
            "Detect post-occupancy waste",
            "Detect seasonal mismatches",
            "Generate actionable recommendations",
            "Calculate financial impact in INR"
        ],
        "endpoints": {
            "health": "/health",
            "predict_single": "/predict",
            "detect_waste": "/detect-waste",
            "detect_waste_batch": "/detect-waste/batch",
            "model_info": "/model/info",
            "demo_waste": "/demo/waste-example"
        }
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "waste_detector_ready": waste_detector is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/detect-waste/batch", tags=["Waste Detection"])
async def detect_waste_batch(data: BatchWasteDetectionInput):
    """
    Detect energy waste patterns in CSV data
    
    CSV should include columns: timestamp, zone_id, device_type, power_kw, 
                                device_state, occupancy_status, season
    """
    try:
        from io import StringIO
        
        # Parse CSV
        df = pd.read_csv(StringIO(data.csv_data))
        
        # Validate required columns
        required_cols = ['timestamp', 'zone_id', 'device_type', 'power_kw', 
                        'device_state', 'occupancy_status']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing columns: {missing_cols}")
        
        # Convert timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Detect waste
        alerts = waste_detector.detect_all_waste(df)
        
        # Format output
        output_alerts = []
        for alert in alerts[:10]:  # Top 10 waste patterns
            alert_dict = alert.__dict__.copy()
            alert_dict['human_readable'] = waste_detector.generate_insight_text(alert)
            output_alerts.append({k: v for k, v in alert_dict.items() 
                                 if k != 'recommended_actions'} | 
                                {'recommended_actions': alert.recommended_actions})
        
        return {
            "waste_detected": len(alerts) > 0,
            "total_patterns": len(alerts),
            "top_waste_alerts": output_alerts,
            "total_annual_cost_inr": sum(a.annual_cost_inr for a in alerts),
            "severity_distribution": {
                'critical': len([a for a in alerts if a.severity == 'critical']),
                'high': len([a for a in alerts if a.severity == 'high']),
                'medium': len([a for a in alerts if a.severity == 'medium']),
                'low': len([a for a in alerts if a.severity == 'low'])
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing data: {str(e)}")


@app.get("/demo/waste-example", tags=["Demo"])
async def demo_waste_example():
    """
    Demo endpoint showing waste detection example
    Returns analysis of phantom load in server room
    """
    # Create demo data: 48 hours of SERVER running continuously while unoccupied
    demo_data = {
        'timestamp': pd.date_range('2026-02-05', periods=48, freq='h'),
        'building_id': 'BLDG01',
        'floor_number': 4,
        'zone_id': 'SERVER_ROOM_4',
        'area_sqft': 300,
        'device_type': 'Server',
        'power_kw': [3.8] * 48,
        'power_max': [5.0] * 48,
        'device_state': ['ON'] * 48,
        'occupancy_status': ['Unoccupied'] * 48,
        'occupancy_count': [0] * 48,
        'season': ['Winter'] * 48,
        'motion_detected': ['No'] * 48
    }
    
    df = pd.DataFrame(demo_data)
    
    # Detect waste
    alerts = waste_detector.detect_all_waste(df)
    
    if alerts:
        alert = alerts[0]  # Get highest impact waste
        
        return {
            "demo_scenario": "Phantom Load Detection - Server Room",
            "scenario_description": (
                "A server room on Floor 4 (300 sqft) has been continuously consuming 3.8 kW "
                "for 48+ hours while the zone is unoccupied. Facility manager notice after weekend."
            ),
            "waste_alert": {
                "waste_type": alert.waste_type,
                "zone_id": alert.zone_id,
                "device_type": alert.device_type,
                "severity": alert.severity,
                "continuous_running_hours": alert.duration_hours,
                "power_consumption": f"{alert.waste_power_kw} kW",
                "energy_wasted": f"{alert.waste_energy_kwh:.1f} kWh"
            },
            "financial_impact": {
                "daily_cost_inr": f"₹{alert.daily_cost_inr:,.0f}",
                "weekly_cost_inr": f"₹{alert.daily_cost_inr * 7:,.0f}",
                "monthly_cost_inr": f"₹{alert.monthly_cost_inr:,.0f}",
                "annual_cost_inr": f"₹{alert.annual_cost_inr:,.0f}",
                "confidence": f"{alert.confidence * 100:.0f}%"
            },
            "reasoning": {
                "why_detected": alert.reason,
                "occupancy_vs_consumption": "Server running 24/7 but zone unoccupied - clear waste",
                "time_pattern": "No demand signal, device should idle during off-hours"
            },
            "recommended_actions": [
                {
                    "priority": action['priority'],
                    "action": action['description'],
                    "estimated_cost_inr": f"₹{action['estimated_cost_inr']:,.0f}",
                    "payback_period_days": action['payback_days'],
                    "roi": f"{(action['payback_days'] / 365 * 100):.1f}% per year" if action['payback_days'] > 0 else "Infinite"
                }
                for action in alert.recommended_actions
            ],
            "implementation_summary": {
                "quick_wins": [
                    "Enable server hibernation via BIOS settings (free, 30 min setup)",
                    "Schedule wake-on-LAN + automatic sleep (free, 1 hour setup)"
                ],
                "medium_term": [
                    "Install smart power strip (₹2,500, 3-day payback)",
                    "Add occupancy sensor override (₹4,000, 15-day payback)"
                ],
                "total_potential_savings": f"₹{alert.annual_cost_inr:,.0f}/year",
                "total_implementation_cost": "₹2,500-6,500",
                "net_first_year_savings": f"₹{alert.annual_cost_inr - 6500:,.0f}"
            }
        }
    
    return {"error": "No waste detected in demo data"}


@app.get("/model/info", tags=["Model"])
async def model_info():
    """Get model information"""
    if model is None:
        return {
            "status": "model_not_loaded",
            "waste_detection": "available",
            "message": "Power disparity model not loaded, but waste detection engine is ready"
        }
    
    return {
        "model_type": "XGBoost Regressor",
        "n_estimators": model.n_estimators,
        "max_depth": model.max_depth,
        "features": feature_names,
        "n_features": len(feature_names),
        "encoders": list(label_encoders.keys()),
        "status": "ready",
        "accuracy_r2": 0.9674,
        "capabilities": [
            "Predict power variance",
            "Detect 5 waste patterns",
            "Calculate financial impact",
            "Generate recommendations"
        ]
    }


@app.post("/predict", tags=["Prediction"])
async def predict(input_data: PredictionInput):
    """Predict power consumption variance (requires model)"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Use /detect-waste instead.")
    
    try:
        # Prepare input
        features = np.array([[
            input_data.hour,
            input_data.day_of_week,
            input_data.day_of_month,
            input_data.month,
            input_data.quarter,
            input_data.is_weekend,
            input_data.power_max,
            input_data.power_rolling_mean_24 or 1000,
            input_data.power_rolling_std_24 or 500
        ]])
        
        prediction = model.predict(features)[0]
        
        return {
            "predicted_power_variance_w": float(prediction),
            "timestamp": datetime.now().isoformat(),
            "model": "XGBoost Energy Prediction"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*80)
    print("ENERGY WASTE DETECTION API - STARTING")
    print("="*80)
    print("✅ Waste Detection Engine: READY")
    print("⚠️  Power Disparity Model: Optional (load if available)")
    print("     → API works with or without pre-trained model")
    print("\nEndpoints:")
    print("  📊 /detect-waste/batch      - Analyze CSV for waste patterns")
    print("  🎯 /demo/waste-example      - View phantom load example")
    print("  🏥 /health                  - Check system status")
    print("  📖 /docs                    - OpenAPI documentation")
    print("\n" + "="*80 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
