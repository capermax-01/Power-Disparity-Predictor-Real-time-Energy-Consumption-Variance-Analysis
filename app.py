"""
FastAPI application for XGBoost energy prediction model
with integrated AI-based Energy Waste Detection & Reasoning Engine
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import joblib
import numpy as np
import xgboost as xgb
from pathlib import Path
import json
from datetime import datetime
import tempfile
import os

# Import reasoning engine
from energy_waste_reasoning import (
    EnergyWasteReasoningEngine,
    PowerDisparitySignal,
    OccupancyContext,
    OccupancyStatus,
    EnergyWasteInsight
)

# Import AI Energy Analyst
from ai_energy_analyst import AIEnergyAnalyst

# Get model directory
MODEL_DIR = Path(__file__).parent / "models"

# Initialize FastAPI app
app = FastAPI(
    title="AI-Based Energy Waste Detection & Reasoning Engine",
    description="XGBoost-based appliance power disparity detection + Reasoning Engine for actionable waste insights",
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

# Global variables for loaded model
model = None
label_encoders = None
feature_names = None

# Reasoning engine instance
reasoning_engine: Optional[EnergyWasteReasoningEngine] = None

# AI Energy Analyst instance
ai_analyst: Optional[AIEnergyAnalyst] = None


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


# ============================================================================
# WASTE ANALYSIS MODELS
# ============================================================================

class WasteAnalysisInput(BaseModel):
    """Input schema for energy waste analysis"""
    # Appliance information
    appliance_id: str = Field(..., example="FRIDGE_1", description="Appliance identifier")
    appliance_category: str = Field(..., example="kitchen", description="Category of appliance")
    location_description: str = Field(default="Unknown", example="Office Zone A", description="Human-readable location")
    
    # Time and context
    hour: int = Field(..., ge=0, le=23, example=14, description="Hour of day (0-23)")
    day_of_week: int = Field(..., ge=0, le=6, example=2, description="Day of week (0=Monday, 6=Sunday)")
    is_weekend: int = Field(..., ge=0, le=1, example=0, description="Is weekend")
    month: int = Field(..., ge=1, le=12, example=6, description="Month (1-12)")
    season: str = Field(default="unknown", example="summer", description="Season")
    
    # Power readings
    power_max: float = Field(..., gt=0, example=2500.0, description="Max power capacity")
    power_rolling_mean_24: Optional[float] = Field(default=1000.0, gt=0, description="24-hour rolling mean power")
    power_rolling_std_24: Optional[float] = Field(default=500.0, ge=0, description="24-hour rolling std dev")
    actual_power_w: Optional[float] = Field(default=None, description="Actual measured power")
    baseline_power_w: Optional[float] = Field(default=0, description="Expected baseline power")
    
    # Occupancy information
    occupancy_status: str = Field(default="unknown", example="unoccupied", description="'occupied', 'unoccupied', 'unknown'")
    occupancy_confidence: float = Field(default=0.5, ge=0, le=1, description="Confidence in occupancy classification")
    
    # Duration (for cost estimation)
    duration_hours: float = Field(default=1.0, gt=0, description="Duration of the anomaly")
    
    # Tariff
    cost_per_kwh: float = Field(default=8.0, gt=0, description="Electricity tariff in ₹/kWh")


class WasteAnalysisOutput(BaseModel):
    """Output schema for waste analysis"""
    waste_type: str = Field(..., description="Type of waste detected")
    risk_level: str = Field(..., description="Severity level")
    appliance_category: str
    location: str
    power_disparity_w: float
    estimated_waste_power_w: float
    duration_hours: float
    total_wasted_kwh: float
    cost_impact: Dict[str, float]
    explainability: Dict[str, Any]
    recommended_actions: List[Dict[str, Any]]
    confidence: float


class WasteAnalysisBatchInput(BaseModel):
    """Input schema for batch waste analysis"""
    analyses: List[WasteAnalysisInput]


class WasteAnalysisBatchOutput(BaseModel):
    """Output schema for batch waste analysis"""
    count: int
    analyses: List[WasteAnalysisOutput]
    total_daily_loss_inr: float
    total_monthly_loss_inr: float
    total_annual_loss_inr: float
    timestamp: str


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    timestamp: str


def load_model_artifacts():
    """Load model and artifacts on startup"""
    global model, label_encoders, feature_names, reasoning_engine, ai_analyst
    
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
        
        # Initialize reasoning engine
        reasoning_engine = EnergyWasteReasoningEngine(
            cost_per_kwh=8.0,
            location_id="BUILDING_01"
        )
        
        # Initialize AI Energy Analyst
        ai_analyst = AIEnergyAnalyst(cost_per_kwh=8.0)
        
        print(f"✓ Model loaded successfully")
        print(f"  Features: {len(feature_names)}")
        print(f"  Encoders: {list(label_encoders.keys())}")
        print(f"✓ Reasoning Engine initialized")
        print(f"✓ AI Energy Analyst initialized")
        
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
        "name": "AI-Based Energy Waste Detection & Reasoning Engine",
        "version": "2.0.0",
        "description": "ML-powered energy waste detection with explainable reasoning",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "predict_single": "/predict",
            "predict_batch": "/predict/batch",
            "analyze_waste_single": "/analyze-waste",
            "analyze_waste_batch": "/analyze-waste/batch",
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


# ============================================================================
# WASTE ANALYSIS ENDPOINTS
# ============================================================================

@app.post("/analyze-waste", response_model=WasteAnalysisOutput, tags=["Waste Analysis"])
async def analyze_waste(input_data: WasteAnalysisInput):
    """
    Analyze appliance for energy waste using ML signal + reasoning engine.
    
    This endpoint:
    1. Predicts power disparity using ML model
    2. Interprets signal using occupancy context
    3. Classifies waste type (phantom load, post-occupancy, inefficient usage, or normal)
    4. Calculates cost impact
    5. Generates actionable recommendations
    """
    if model is None or reasoning_engine is None:
        raise HTTPException(status_code=503, detail="Model or reasoning engine not loaded")
    
    try:
        # Step 1: Get ML prediction for power disparity
        pred_input = PredictionInput(
            appliance_id=input_data.appliance_id,
            appliance_category=input_data.appliance_category,
            hour=input_data.hour,
            day_of_week=input_data.day_of_week,
            day_of_month=15,  # Use mid-month as default
            month=input_data.month,
            quarter=(input_data.month - 1) // 3 + 1,
            is_weekend=input_data.is_weekend,
            power_max=input_data.power_max,
            power_rolling_mean_24=input_data.power_rolling_mean_24,
            power_rolling_std_24=input_data.power_rolling_std_24,
        )
        
        # Encode and predict
        features = encode_input(pred_input)
        prediction = model.predict(features)[0]
        predicted_disparity = max(0, float(prediction))
        confidence = min(1.0, max(0, 1.0 - abs(predicted_disparity - input_data.power_max) / (input_data.power_max + 1) * 0.5))
        
        # Step 2: Create power disparity signal
        signal = PowerDisparitySignal(
            predicted_power_w=predicted_disparity,
            confidence=confidence,
            baseline_power_w=input_data.baseline_power_w or 0,
            actual_power_w=input_data.actual_power_w,
            variance_percent=(predicted_disparity / (input_data.baseline_power_w + 1)) * 100
        )
        
        # Step 3: Create occupancy context
        occupancy_map = {
            "occupied": OccupancyStatus.OCCUPIED,
            "unoccupied": OccupancyStatus.UNOCCUPIED,
            "unknown": OccupancyStatus.UNKNOWN
        }
        
        context = OccupancyContext(
            occupancy_status=occupancy_map.get(input_data.occupancy_status.lower(), OccupancyStatus.UNKNOWN),
            occupancy_confidence=input_data.occupancy_confidence,
            hour=input_data.hour,
            day_of_week=input_data.day_of_week,
            is_weekend=bool(input_data.is_weekend),
            season=input_data.season.lower() or "unknown"
        )
        
        # Step 4: Run reasoning engine
        insight: EnergyWasteInsight = reasoning_engine.analyze(
            signal=signal,
            context=context,
            appliance_category=input_data.appliance_category,
            location_description=input_data.location_description,
            duration_hours=input_data.duration_hours
        )
        
        # Override cost if custom tariff provided
        if input_data.cost_per_kwh != 8.0:
            daily_loss = insight.estimated_waste_power_w / 1000.0 * 24 * input_data.cost_per_kwh
            insight.estimated_daily_loss_inr = daily_loss
            insight.estimated_monthly_loss_inr = daily_loss * 30
            insight.estimated_annual_loss_inr = daily_loss * 365
        
        # Step 5: Return JSON response
        return insight.to_dict()
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Waste analysis error: {str(e)}")


@app.post("/analyze-waste/batch", response_model=WasteAnalysisBatchOutput, tags=["Waste Analysis"])
async def analyze_waste_batch(batch_input: WasteAnalysisBatchInput):
    """Perform batch waste analysis for multiple appliances"""
    if model is None or reasoning_engine is None:
        raise HTTPException(status_code=503, detail="Model or reasoning engine not loaded")
    
    try:
        insights = []
        total_daily = 0
        total_monthly = 0
        total_annual = 0
        
        for input_data in batch_input.analyses:
            # Run analysis for each appliance
            try:
                pred_input = PredictionInput(
                    appliance_id=input_data.appliance_id,
                    appliance_category=input_data.appliance_category,
                    hour=input_data.hour,
                    day_of_week=input_data.day_of_week,
                    day_of_month=15,
                    month=input_data.month,
                    quarter=(input_data.month - 1) // 3 + 1,
                    is_weekend=input_data.is_weekend,
                    power_max=input_data.power_max,
                    power_rolling_mean_24=input_data.power_rolling_mean_24,
                    power_rolling_std_24=input_data.power_rolling_std_24,
                )
                
                features = encode_input(pred_input)
                prediction = model.predict(features)[0]
                predicted_disparity = max(0, float(prediction))
                confidence = min(1.0, max(0, 1.0 - abs(predicted_disparity - input_data.power_max) / (input_data.power_max + 1) * 0.5))
                
                signal = PowerDisparitySignal(
                    predicted_power_w=predicted_disparity,
                    confidence=confidence,
                    baseline_power_w=input_data.baseline_power_w or 0,
                    actual_power_w=input_data.actual_power_w,
                    variance_percent=(predicted_disparity / (input_data.baseline_power_w + 1)) * 100
                )
                
                occupancy_map = {
                    "occupied": OccupancyStatus.OCCUPIED,
                    "unoccupied": OccupancyStatus.UNOCCUPIED,
                    "unknown": OccupancyStatus.UNKNOWN
                }
                
                context = OccupancyContext(
                    occupancy_status=occupancy_map.get(input_data.occupancy_status.lower(), OccupancyStatus.UNKNOWN),
                    occupancy_confidence=input_data.occupancy_confidence,
                    hour=input_data.hour,
                    day_of_week=input_data.day_of_week,
                    is_weekend=bool(input_data.is_weekend),
                    season=input_data.season.lower() or "unknown"
                )
                
                insight = reasoning_engine.analyze(
                    signal=signal,
                    context=context,
                    appliance_category=input_data.appliance_category,
                    location_description=input_data.location_description,
                    duration_hours=input_data.duration_hours
                )
                
                if input_data.cost_per_kwh != 8.0:
                    daily_loss = insight.estimated_waste_power_w / 1000.0 * 24 * input_data.cost_per_kwh
                    insight.estimated_daily_loss_inr = daily_loss
                    insight.estimated_monthly_loss_inr = daily_loss * 30
                    insight.estimated_annual_loss_inr = daily_loss * 365
                
                insights.append(insight.to_dict())
                
                # Accumulate totals (only for non-normal waste)
                if insight.waste_type.value != "normal":
                    total_daily += insight.estimated_daily_loss_inr
                    total_monthly += insight.estimated_monthly_loss_inr
                    total_annual += insight.estimated_annual_loss_inr
            
            except Exception as e:
                # Log error but continue processing
                print(f"Error analyzing {input_data.appliance_id}: {str(e)}")
                continue
        
        return {
            "count": len(insights),
            "analyses": insights,
            "total_daily_loss_inr": round(total_daily, 2),
            "total_monthly_loss_inr": round(total_monthly, 2),
            "total_annual_loss_inr": round(total_annual, 0),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Batch waste analysis error: {str(e)}")


@app.get("/model/waste-reasoning", tags=["Model"])
async def waste_reasoning_info():
    """Get information about the reasoning engine"""
    if reasoning_engine is None:
        raise HTTPException(status_code=503, detail="Reasoning engine not loaded")
    
    return {
        "name": "AI-Based Energy Waste Detection & Reasoning Engine",
        "version": "1.0.0",
        "description": "Converts ML power disparity signals into explainable waste insights",
        "waste_types": ["phantom_load", "post_occupancy", "inefficient_usage", "normal"],
        "risk_levels": ["low", "medium", "high", "critical"],
        "occupancy_modes": ["occupied", "unoccupied", "unknown"],
        "default_tariff_inr_per_kwh": 8.0,
        "cost_calculation": "waste_power_kw * 24 * tariff",
        "features": {
            "occupancy_based_classification": True,
            "time_pattern_analysis": True,
            "cost_impact_calculation": True,
            "actionable_recommendations": True,
            "explainability_reasoning": True
        }
    }
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


# ============================================================================
# BUILDING-LEVEL ANALYSIS & COMPREHENSIVE REPORTING (NEW)
# ============================================================================

# Import new agents
try:
    from data_ingestion_agent import DataIngestionAgent, DataSourceType
    from pattern_analysis_agent import PatternAnalysisAgent
    from learning_adaptation_agent import LearningAdaptationAgent
    from alert_recommendation_system import AlertGenerator, AlertSeverity
    data_ingestion = DataIngestionAgent()
    pattern_analyzer = PatternAnalysisAgent()
    learning_agent = LearningAdaptationAgent("BUILDING_01")
    alert_generator = AlertGenerator(cost_per_kwh_inr=8.0)
    print("✓ Data ingestion agents initialized")
except Exception as e:
    import traceback
    print(f"⚠ Warning: Could not load agents: {e}")
    traceback.print_exc()
    data_ingestion = None
    pattern_analyzer = None
    learning_agent = None
    alert_generator = None


class BuildingAnalysisInput(BaseModel):
    """Building-level analysis (all devices)"""
    analyses: List[WasteAnalysisInput] = Field(..., description="List of appliances to analyze")
    building_id: str = Field(default="BUILDING_01")
    location_floor: str = Field(default="All Floors")
    tariff_inr_per_kwh: float = Field(default=8.0, gt=0)


class AlertFilterInput(BaseModel):
    """Filters for alert retrieval"""
    floor: Optional[str] = None
    device_category: Optional[str] = None
    min_severity: Optional[str] = None
    status: Optional[str] = None
    min_annual_cost_inr: Optional[float] = None


class BuildingReportOutput(BaseModel):
    """Building safety report output"""
    building_id: str
    report_date: str
    summary: Dict[str, Any]
    cost_impact: Dict[str, Any]
    top_waste_leaks: List[Dict[str, Any]]
    waste_by_category: Dict[str, float]
    waste_by_floor: Dict[str, float]
    waste_by_type: Dict[str, float]
    recommendations: Dict[str, Any]
    trends: Dict[str, float]


@app.post("/analyze-building", tags=["Building Analysis"])
async def analyze_building(input_data: BuildingAnalysisInput):
    """
    Analyze entire building for energy waste.
    Aggregates insights, generates alerts, and provides building-level recommendations.
    
    This endpoint:
    1. Analyzes all appliances in the building
    2. Detects patterns and anomalies
    3. Generates prioritized alerts ranked by cost impact
    4. Creates building report with top waste leaks
    5. Suggests facility-wide improvements
    """
    if model is None or reasoning_engine is None:
        raise HTTPException(status_code=503, detail="Model or reasoning engine not loaded")
    
    try:
        analyses = []
        alerts_generated = []
        total_daily_loss = 0
        total_monthly_loss = 0
        total_annual_loss = 0
        
        # Analyze each appliance
        for appliance in input_data.analyses:
            try:
                # Get ML prediction
                pred_input = PredictionInput(
                    appliance_id=appliance.appliance_id,
                    appliance_category=appliance.appliance_category,
                    hour=appliance.hour,
                    day_of_week=appliance.day_of_week,
                    day_of_month=15,
                    month=appliance.month,
                    quarter=(appliance.month - 1) // 3 + 1,
                    is_weekend=appliance.is_weekend,
                    power_max=appliance.power_max,
                    power_rolling_mean_24=appliance.power_rolling_mean_24,
                    power_rolling_std_24=appliance.power_rolling_std_24,
                )
                
                features = encode_input(pred_input)
                prediction = model.predict(features)[0]
                predicted_disparity = max(0, float(prediction))
                confidence = min(1.0, max(0, 1.0 - abs(predicted_disparity - appliance.power_max) / (appliance.power_max + 1) * 0.5))
                
                signal = PowerDisparitySignal(
                    predicted_power_w=predicted_disparity,
                    confidence=confidence,
                    baseline_power_w=appliance.baseline_power_w or 0,
                    actual_power_w=appliance.actual_power_w,
                    variance_percent=(predicted_disparity / (appliance.baseline_power_w + 1)) * 100
                )
                
                occupancy_map = {
                    "occupied": OccupancyStatus.OCCUPIED,
                    "unoccupied": OccupancyStatus.UNOCCUPIED,
                    "unknown": OccupancyStatus.UNKNOWN
                }
                
                context = OccupancyContext(
                    occupancy_status=occupancy_map.get(appliance.occupancy_status.lower(), OccupancyStatus.UNKNOWN),
                    occupancy_confidence=appliance.occupancy_confidence,
                    hour=appliance.hour,
                    day_of_week=appliance.day_of_week,
                    is_weekend=bool(appliance.is_weekend),
                    season=appliance.season.lower() or "unknown"
                )
                
                insight = reasoning_engine.analyze(
                    signal=signal,
                    context=context,
                    appliance_category=appliance.appliance_category,
                    location_description=appliance.location_description,
                    duration_hours=appliance.duration_hours
                )
                
                # Override cost if custom tariff provided
                if input_data.tariff_inr_per_kwh != 8.0:
                    daily_loss = insight.estimated_waste_power_w / 1000.0 * 24 * input_data.tariff_inr_per_kwh
                    insight.estimated_daily_loss_inr = daily_loss
                    insight.estimated_monthly_loss_inr = daily_loss * 30
                    insight.estimated_annual_loss_inr = daily_loss * 365
                
                analyses.append(insight.to_dict())
                
                # Generate alert if significant waste
                if insight.waste_type.value != "normal":
                    alert = alert_generator.generate_alert_from_insight(
                        device_id=appliance.appliance_id,
                        device_category=appliance.appliance_category,
                        waste_type=insight.waste_type.value,
                        risk_level=insight.risk_level.value,
                        location_floor=appliance.location_description,
                        location_zone=None,
                        power_disparity_w=insight.power_disparity_w,
                        duration_hours=appliance.duration_hours,
                        occupancy_mismatch=insight.occupancy_mismatch,
                        evidence=insight.reasoning_chain
                    )
                    
                    # Generate recommendations
                    recommendations = alert_generator.generate_recommendations(alert)
                    alert.recommendation_ids = [r.recommendation_id for r in recommendations]
                    
                    alerts_generated.append(alert.to_dict())
                    
                    total_daily_loss += insight.estimated_daily_loss_inr
                    total_monthly_loss += insight.estimated_monthly_loss_inr
                    total_annual_loss += insight.estimated_annual_loss_inr
            
            except Exception as e:
                print(f"Error analyzing {appliance.appliance_id}: {str(e)}")
                continue
        
        # Sort alerts by annual cost (highest first)
        alerts_generated = sorted(alerts_generated, key=lambda a: a['cost_impact']['annual_inr'], reverse=True)
        
        # Top 3 waste leaks
        top_waste = alerts_generated[:3]
        
        return {
            "building_id": input_data.building_id,
            "analysis_date": datetime.now().isoformat(),
            "appliances_analyzed": len(analyses),
            "total_appliances": len(input_data.analyses),
            "alerts_generated": len(alerts_generated),
            "top_waste_leaks": top_waste,
            "all_alerts": alerts_generated,
            "cost_summary": {
                "daily_loss_inr": round(total_daily_loss, 2),
                "monthly_loss_inr": round(total_monthly_loss, 2),
                "annual_loss_inr": round(total_annual_loss, 0)
            },
            "recommendations_available": sum(len(a.get('recommendations', [])) for a in alerts_generated)
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Building analysis error: {str(e)}")


@app.get("/alerts", tags=["Alerts"])
async def list_alerts(floor: Optional[str] = None,
                     device_category: Optional[str] = None,
                     min_severity: Optional[str] = None,
                     status: Optional[str] = None,
                     min_annual_cost_inr: Optional[float] = None):
    """
    Retrieve alerts with optional filtering.
    
    Query Parameters:
    - floor: Filter by location (e.g., "Floor 3", "Ground")
    - device_category: Filter by appliance type (e.g., "hvac", "lighting")
    - min_severity: Minimum severity ("low", "medium", "high", "critical")
    - status: Alert status ("open", "acknowledged", "investigating", "resolved")
    - min_annual_cost_inr: Minimum annual cost impact
    """
    if alert_generator is None:
        raise HTTPException(status_code=503, detail="Alert system not initialized")
    
    try:
        # Convert min_severity string to enum if provided
        min_sev = None
        if min_severity:
            severity_map = {
                "low": AlertSeverity.LOW,
                "medium": AlertSeverity.MEDIUM,
                "high": AlertSeverity.HIGH,
                "critical": AlertSeverity.CRITICAL
            }
            min_sev = severity_map.get(min_severity.lower())
        
        # Filter alerts
        filtered = alert_generator.filter_alerts(
            floor=floor,
            device_category=device_category,
            min_severity=min_sev,
            status=status,
            min_annual_cost_inr=min_annual_cost_inr
        )
        
        # Sort by annual cost impact (highest first)
        filtered = sorted(filtered, key=lambda a: a.annual_cost_loss_inr, reverse=True)
        
        return {
            "total": len(filtered),
            "alerts": [a.to_dict() for a in filtered],
            "filters_applied": {
                "floor": floor,
                "device_category": device_category,
                "min_severity": min_severity,
                "status": status,
                "min_cost_inr": min_annual_cost_inr
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error retrieving alerts: {str(e)}")


@app.post("/alerts/{alert_id}/acknowledge", tags=["Alerts"])
async def acknowledge_alert(alert_id: str, assigned_to: Optional[str] = None):
    """Acknowledge an alert and optionally assign it"""
    if alert_generator is None:
        raise HTTPException(status_code=503, detail="Alert system not initialized")
    
    if alert_id not in alert_generator.alerts:
        raise HTTPException(status_code=404, detail=f"Alert not found: {alert_id}")
    
    alert = alert_generator.alerts[alert_id]
    alert.status = "acknowledged"
    alert.assigned_to = assigned_to
    alert.updated_at = datetime.now()
    
    return {
        "alert_id": alert_id,
        "status": "acknowledged",
        "assigned_to": assigned_to,
        "updated_at": alert.updated_at.isoformat()
    }


@app.get("/recommendations", tags=["Recommendations"])
async def list_recommendations(alert_id: Optional[str] = None, status: Optional[str] = None):
    """
    Get recommendations with optional filtering.
    
    Query Parameters:
    - alert_id: Filter by alert
    - status: Filter by status ("proposed", "approved", "in_progress", "completed")
    """
    if alert_generator is None:
        raise HTTPException(status_code=503, detail="Recommendation system not initialized")
    
    recs = list(alert_generator.recommendations.values())
    
    if alert_id:
        recs = [r for r in recs if r.alert_id == alert_id]
    
    if status:
        recs = [r for r in recs if r.status == status]
    
    # Sort by payback period (quickest ROI first)
    recs = sorted(recs, key=lambda r: r.payback_period_months)
    
    return {
        "total": len(recs),
        "recommendations": [r.to_dict() for r in recs]
    }


@app.post("/recommendations/{rec_id}/approve", tags=["Recommendations"])
async def approve_recommendation(rec_id: str, approved_by: str):
    """Approve a recommendation for implementation"""
    if alert_generator is None:
        raise HTTPException(status_code=503, detail="Recommendation system not initialized")
    
    if rec_id not in alert_generator.recommendations:
        raise HTTPException(status_code=404, detail=f"Recommendation not found: {rec_id}")
    
    rec = alert_generator.recommendations[rec_id]
    rec.status = "approved"
    rec.approved_by = approved_by
    rec.approval_date = datetime.now()
    
    return {
        "recommendation_id": rec_id,
        "status": "approved",
        "approved_by": approved_by,
        "estimated_savings_inr": round(rec.estimated_annual_savings_inr, 0),
        "payback_months": round(rec.payback_period_months, 1)
    }


@app.get("/building-report", response_model=BuildingReportOutput, tags=["Reports"])
async def get_building_report(building_id: str = "BUILDING_01"):
    """
    Get comprehensive building energy waste report.
    Includes top waste leaks, cost summary, and recommended improvements.
    """
    if alert_generator is None:
        raise HTTPException(status_code=503, detail="Alert system not initialized")
    
    try:
        report = alert_generator.build_building_report(building_id)
        return report.to_dict()
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating report: {str(e)}")


@app.post("/upload-csv", tags=["Data Ingestion"])
async def upload_csv_file(file: UploadFile = File(...)):
    """
    Upload smart meter CSV data for AI-powered energy waste analysis.
    
    Expected CSV columns:
    - timestamp (ISO format)
    - device_id
    - device_category
    - power_w (watts)
    - occupancy_status (optional: "occupied", "unoccupied")
    - location_floor (optional)
    - location_zone (optional)
    
    Returns:
    - Ingestion summary
    - AI-generated energy waste report with actionable insights
    """
    if data_ingestion is None or ai_analyst is None:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    try:
        import tempfile
        import os
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
            contents = await file.read()
            tmp_file.write(contents)
            tmp_path = tmp_file.name
        
        try:
            # Step 1: Ingest the data
            ingestion_result = data_ingestion.ingest_csv(tmp_path)
            
            # Step 2: Run AI Energy Analysis
            analysis_report = ai_analyst.analyze(ingestion_result.readings)
            
            return {
                "file": file.filename,
                "status": "analyzed",
                "ingestion_summary": ingestion_result.to_dict(),
                "energy_analysis": ai_analyst.report_to_dict(analysis_report)
            }
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Analysis error: {str(e)}")


@app.post("/learning/feedback", tags=["Learning"])
async def submit_learning_feedback(device_id: str, feedback_type: str, severity: str):
    """
    Submit feedback to help system learn and adapt.
    
    Args:
    - device_id: Device the feedback is about
    - feedback_type: "adjustment_needed", "false_alarm", "missed_detection"
    - severity: "true_positive", "false_positive", "false_negative"
    """
    if learning_agent is None:
        raise HTTPException(status_code=503, detail="Learning system not initialized")
    
    try:
        feedback_data = {
            "feedback_type": feedback_type,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }
        
        learning_agent.adapt_thresholds(device_id, feedback_data)
        
        return {
            "status": "feedback_recorded",
            "device_id": device_id,
            "learning_metrics": learning_agent.get_learning_summary()
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Feedback error: {str(e)}")


@app.get("/learning/summary", tags=["Learning"])
async def get_learning_summary():
    """Get summary of what the system has learned"""
    if learning_agent is None:
        raise HTTPException(status_code=503, detail="Learning system not initialized")
    
    return learning_agent.get_learning_summary()


@app.get("/docs", include_in_schema=False)
async def get_docs():
    """Swagger UI documentation"""
    pass


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("STARTING ENERGY PREDICTION API")
    print("="*70)
    print("\nAPI Documentation: http://localhost:8001/docs")
    print("API Health Check: http://localhost:8001/health")
    print("="*70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
