# 🚀 API Quick Reference Guide

## Base URL
```
http://localhost:8001
```

## Interactive API Documentation
```
http://localhost:8001/docs  (Swagger UI)
http://localhost:8001/redoc (ReDoc)
```

---

## 🔍 WASTE ANALYSIS ENDPOINTS (New in v2.0)

### 1. Analyze Single Appliance for Energy Waste
**Endpoint:** `POST /analyze-waste`

**Description:** Analyze a single appliance for energy waste using ML signal + reasoning engine.

**Request Body:**
```json
{
  "appliance_id": "SERVER_1",
  "appliance_category": "server",
  "location_description": "Data Center Floor 4",
  "hour": 2,
  "day_of_week": 3,
  "is_weekend": 0,
  "month": 6,
  "season": "summer",
  "power_max": 3500,
  "baseline_power_w": 500,
  "actual_power_w": 3200,
  "occupancy_status": "unoccupied",
  "occupancy_confidence": 0.95,
  "duration_hours": 8,
  "cost_per_kwh": 8.0
}
```

**Response:**
```json
{
  "waste_type": "phantom_load",
  "risk_level": "high",
  "appliance_category": "server",
  "location": "Data Center Floor 4",
  "detected_at": "2026-02-07T15:30:00.000Z",
  "power_disparity_w": 2800,
  "estimated_waste_power_w": 2800,
  "duration_hours": 8,
  "total_wasted_kwh": 22.4,
  "cost_impact": {
    "daily_inr": 537.6,
    "monthly_inr": 16128,
    "annual_inr": 196128
  },
  "explainability": {
    "occupancy_mismatch": true,
    "time_pattern": "night_hours",
    "signal_strength": "strong",
    "reasoning": [
      "ML detected 2800W power deviation (confidence: 95%)",
      "Building is unoccupied at this time",
      "This occurs during off-hours (10 PM - 6 AM)",
      "High power consumption during unoccupancy = Phantom load",
      "This translates to continuous financial loss"
    ]
  },
  "recommended_actions": [
    {
      "priority": "CRITICAL",
      "description": "Install smart power strip or occupancy-based disconnect for server",
      "estimated_cost": 3000,
      "payback_days": 9,
      "confidence": 0.95
    },
    {
      "priority": "HIGH",
      "description": "Enable sleep/idle mode on server with 15-min shutdown timer",
      "estimated_cost": 0,
      "payback_days": 0,
      "confidence": 0.9
    }
  ],
  "confidence": 0.92
}
```

**Status Codes:**
- `200`: Success - waste analysis complete
- `400`: Bad request - invalid input data
- `503`: Service unavailable - model not loaded

---

### 2. Analyze Multiple Appliances (Batch)
**Endpoint:** `POST /analyze-waste/batch`

**Description:** Analyze multiple appliances and get aggregated waste summary.

**Request Body:**
```json
{
  "analyses": [
    {
      "appliance_id": "SERVER_1",
      "appliance_category": "server",
      "hour": 2,
      "day_of_week": 3,
      "is_weekend": 0,
      "month": 6,
      "power_max": 3500,
      "occupancy_status": "unoccupied"
    },
    {
      "appliance_id": "LIGHTS_ZONE_A",
      "appliance_category": "lighting",
      "hour": 20,
      "day_of_week": 3,
      "power_max": 500,
      "occupancy_status": "unoccupied"
    }
  ]
}
```

**Response:**
```json
{
  "count": 2,
  "analyses": [
    {
      "waste_type": "phantom_load",
      "risk_level": "high",
      "cost_impact": { "daily_inr": 537.6, ... }
    },
    {
      "waste_type": "post_occupancy",
      "risk_level": "medium",
      "cost_impact": { "daily_inr": 45.3, ... }
    }
  ],
  "total_daily_loss_inr": 582.9,
  "total_monthly_loss_inr": 17487,
  "total_annual_loss_inr": 212640,
  "timestamp": "2026-02-07T15:30:00.000Z"
}
```

---

### 3. Get Reasoning Engine Information
**Endpoint:** `GET /model/waste-reasoning`

**Description:** Returns information about the reasoning engine configuration and capabilities.

**Response:**
```json
{
  "name": "AI-Based Energy Waste Detection & Reasoning Engine",
  "version": "1.0.0",
  "description": "Converts ML power disparity signals into explainable waste insights",
  "waste_types": [
    "phantom_load",
    "post_occupancy",
    "inefficient_usage",
    "normal"
  ],
  "risk_levels": [
    "low",
    "medium",
    "high",
    "critical"
  ],
  "occupancy_modes": [
    "occupied",
    "unoccupied",
    "unknown"
  ],
  "default_tariff_inr_per_kwh": 8.0,
  "cost_calculation": "waste_power_kw * 24 * tariff",
  "features": {
    "occupancy_based_classification": true,
    "time_pattern_analysis": true,
    "cost_impact_calculation": true,
    "actionable_recommendations": true,
    "explainability_reasoning": true
  }
}
```

---

## ⚡ PREDICTION ENDPOINTS (Original, Still Available)

### 4. Predict Single Appliance Power Disparity
**Endpoint:** `POST /predict`

**Description:** Get ML prediction for power disparity (original functionality preserved).

**Request Body:**
```json
{
  "appliance_id": "FRIDGE_207",
  "appliance_category": "kitchen",
  "hour": 14,
  "day_of_week": 2,
  "day_of_month": 15,
  "month": 6,
  "quarter": 2,
  "is_weekend": 0,
  "power_max": 2500.0,
  "power_rolling_mean_24": 1000.0,
  "power_rolling_std_24": 500.0
}
```

**Response:**
```json
{
  "predicted_power_w": 1250.5,
  "confidence": 92.3,
  "timestamp": "2026-02-07T15:30:00.000Z"
}
```

---

### 5. Predict Multiple Appliances (Batch)
**Endpoint:** `POST /predict/batch`

**Request Body:**
```json
{
  "predictions": [
    { ... prediction 1 ... },
    { ... prediction 2 ... }
  ]
}
```

**Response:**
```json
{
  "count": 2,
  "predictions": [
    {
      "appliance_id": "FRIDGE_207",
      "predicted_power_w": 1250.5,
      "confidence": 92.3
    }
  ],
  "timestamp": "2026-02-07T15:30:00.000Z"
}
```

---

## 🏥 HEALTH & INFO ENDPOINTS

### 6. Health Check
**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2026-02-07T15:30:00.000Z"
}
```

---

### 7. Model Information
**Endpoint:** `GET /model/info`

**Response:**
```json
{
  "model_type": "XGBoost Regressor",
  "n_estimators": 100,
  "max_depth": 8,
  "features": [
    "hour",
    "day_of_week",
    "month",
    ...
  ],
  "n_features": 15,
  "encoders": [
    "appliance_id",
    "appliance_category"
  ],
  "status": "ready"
}
```

---

### 8. API Root
**Endpoint:** `GET /`

**Response:**
```json
{
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
```

---

## 📊 Field definitions

### WasteAnalysisInput Fields

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `appliance_id` | string | ✓ | Appliance identifier | "SERVER_1" |
| `appliance_category` | string | ✓ | Type of appliance | "server", "lighting", "hvac" |
| `location_description` | string | | Human-readable location | "Data Center Floor 4" |
| `hour` | integer (0-23) | ✓ | Hour of day | 14 |
| `day_of_week` | integer (0-6) | ✓ | 0=Mon, 6=Sun | 2 |
| `is_weekend` | integer (0-1) | ✓ | Is weekend? | 0 |
| `month` | integer (1-12) | ✓ | Month | 6 |
| `season` | string | | Season | "summer", "winter" |
| `power_max` | float (>0) | ✓ | Max capacity (watts) | 3500 |
| `baseline_power_w` | float (>=0) | | Expected normal power | 500 |
| `actual_power_w` | float (>=0) | | Measured power | 3200 |
| `occupancy_status` | string | | Status | "occupied", "unoccupied", "unknown" |
| `occupancy_confidence` | float (0-1) | | How sure? | 0.95 |
| `duration_hours` | float (>0) | | How long? | 8 |
| `cost_per_kwh` | float (>0) | | Tariff in ₹/kWh | 8.0 |

### WasteAnalysisOutput Fields

| Field | Type | Description |
|-------|------|-------------|
| `waste_type` | string | "phantom_load", "post_occupancy", "inefficient_usage", "normal" |
| `risk_level` | string | "low", "medium", "high", "critical" |
| `power_disparity_w` | float | ML prediction (watts) |
| `estimated_waste_power_w` | float | Adjusted waste power |
| `cost_impact` | object | Daily, monthly, annual loss in ₹ |
| `explainability` | object | Reasoning chain, signal strength, etc. |
| `recommended_actions` | array | Prioritized corrective actions |
| `confidence` | float (0-1) | Diagnosis confidence |

---

## 🎯 Waste Type Decision Tree

```
IF power_disparity > 500W AND occupancy_status == "UNOCCUPIED"
   AND duration > 6 hours
   → PHANTOM_LOAD (cost: daily × 365)

ELSE IF power_disparity > 500W AND hour > 18 AND occupancy_status == "UNOCCUPIED"
   AND duration > 2 hours
   → POST_OCCUPANCY (cost: moderate)

ELSE IF 200W < power_disparity < 500W AND occupancy_status == "OCCUPIED"
   AND is_working_hours
   → INEFFICIENT_USAGE (cost: situation-dependent)

ELSE
   → NORMAL (no action needed)
```

---

## 💬 Example API Calls

### cURL: Single Waste Analysis
```bash
curl -X POST "http://localhost:8001/analyze-waste" \
  -H "Content-Type: application/json" \
  -d '{
    "appliance_id": "SERVER_1",
    "appliance_category": "server",
    "hour": 2,
    "day_of_week": 3,
    "month": 6,
    "is_weekend": 0,
    "power_max": 3500,
    "baseline_power_w": 500,
    "occupancy_status": "unoccupied",
    "occupancy_confidence": 0.95,
    "location_description": "Data Center",
    "duration_hours": 8
  }'
```

### Python: Batch Analysis
```python
import requests

api_url = "http://localhost:8001/analyze-waste/batch"

batch_input = {
    "analyses": [
        {
            "appliance_id": "SERVER_1",
            "appliance_category": "server",
            "hour": 2,
            ...
        },
        {
            "appliance_id": "LIGHTS_A",
            "appliance_category": "lighting",
            "hour": 20,
            ...
        }
    ]
}

response = requests.post(api_url, json=batch_input)
insights = response.json()

print(f"Total annual waste: ₹{insights['total_annual_loss_inr']}")
for analysis in insights['analyses']:
    print(f"- {analysis['appliance_id']}: {analysis['waste_type']}")
```

### JavaScript: Frontend Call
```javascript
const analyzeWaste = async (input) => {
  const response = await fetch('/api/analyze-waste', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input)
  })
  
  const insight = await response.json()
  
  // Display results
  console.log(`Waste Type: ${insight.waste_type}`)
  console.log(`Annual Cost: ₹${insight.cost_impact.annual_inr}`)
  console.log(`Recommendations: ${insight.recommended_actions.length}`)
}
```

---

## ❌ Common Errors & Solutions

### Error: 503 Service Unavailable
**Cause:** Model not loaded
**Solution:** 
```bash
# Check model files exist
ls models/xgb_energy_model.pkl
ls models/label_encoders.pkl

# If missing, train model
python train_xgb_model.py
```

### Error: 400 Bad Request - "Invalid occupancy_status"
**Cause:** Invalid value provided
**Solution:** Use one of: "occupied", "unoccupied", "unknown"

### Error: 400 Bad Request - "Encoding features error"
**Cause:** Unknown appliance_id or category
**Solution:** Check label encoders in model, use known values

### Issue: Low Confidence Score
**Cause:** Conflicting signals or unknown occupancy
**Solution:** Provide occupancy_confidence > 0.8, use known appliances

---

## 🔧 Configuration

### Change Electricity Tariff (Global)
Currently hardcoded to ₹8/kWh. To change:

Edit `app.py`:
```python
reasoning_engine = EnergyWasteReasoningEngine(
    cost_per_kwh=10.0,  # Change here
    location_id="BUILDING_01"
)
```

### Per-Request Tariff Override
Pass `cost_per_kwh` in request:
```json
{
  "cost_per_kwh": 12.5,
  ...
}
```

---

## 📈 Performance Tips

- **Single request:** <50ms response time
- **Batch requests:** Use `/analyze-waste/batch` for 100+ appliances
- **Cache results:** Store insights for 5 minutes before re-analyzing
- **Parallel calls:** API is thread-safe, supports concurrent requests

---

## 🔐 Security

- No authentication required (add OAuth2 in production)
- Input validation on all fields
- No sensitive data stored
- CORS enabled for frontend integration

---

## 📚 Documentation References

- **System Design:** `SYSTEM_ARCHITECTURE.md`
- **Frontend Guide:** `FRONTEND.md`
- **Data Source Flexibility:** `DATA_SOURCE_FLEXIBILITY.md`
- **API Swagger:** http://localhost:8001/docs

---

*API Reference for v2.0 - Energy Waste Detection & Reasoning Engine*
