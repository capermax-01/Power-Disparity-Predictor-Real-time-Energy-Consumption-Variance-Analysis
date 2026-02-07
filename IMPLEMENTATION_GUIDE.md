# 🚀 Quick Implementation Guide: Energy Waste Detection

## What's New in Version 2.0

### Old System (v1.0)
```
Input → ML Model → Prediction (Power Value)
Goal: "How much power will this appliance use?"
Output: Raw number (watts)
```

### New System (v2.0) - Energy Waste Detection
```
Input → ML Model → Signal (Power Disparity)
     ↓
   Context (Occupancy, Time, Season)
     ↓
Reasoning Engine → Waste Classification → Actionable Insights
Goal: "Is this energy waste? If yes, what should we do?"
Output: Waste type + Cost + Actions + Explanation
```

---

## Backend: Adding Waste Analysis to Your FastAPI

### Step 1: Copy the Reasoning Engine
```bash
cp energy_waste_reasoning.py your_project/
```

### Step 2: Update Your FastAPI App
```python
# In your app.py
from energy_waste_reasoning import (
    EnergyWasteReasoningEngine,
    PowerDisparitySignal,
    OccupancyContext,
    OccupancyStatus,
)

# During app startup
reasoning_engine = EnergyWasteReasoningEngine(
    cost_per_kwh=8.0,  # ₹/kWh
    location_id="BUILDING_01"
)

# New endpoint
@app.post("/analyze-waste")
async def analyze_waste(input_data: WasteAnalysisInput):
    """Analyze appliance for energy waste"""
    
    # Step 1: Get ML prediction
    prediction = model.predict(features)
    
    # Step 2: Create signal
    signal = PowerDisparitySignal(
        predicted_power_w=prediction,
        confidence=0.95,
        baseline_power_w=input_data.baseline_power_w
    )
    
    # Step 3: Create context
    context = OccupancyContext(
        occupancy_status=OccupancyStatus.UNOCCUPIED,
        hour=input_data.hour,
        is_weekend=input_data.is_weekend
    )
    
    # Step 4: Analyze!
    insight = reasoning_engine.analyze(
        signal=signal,
        context=context,
        appliance_category=input_data.appliance_category,
        location_description=input_data.location_description
    )
    
    # Step 5: Return
    return insight.to_dict()
```

### Step 3: Add New Pydantic Models
```python
from pydantic import BaseModel

class WasteAnalysisInput(BaseModel):
    appliance_id: str
    appliance_category: str
    hour: int
    day_of_week: int
    month: int
    occupancy_status: str
    occupancy_confidence: float
    power_max: float
    baseline_power_w: float = 0
    location_description: str = "Unknown"

class WasteAnalysisOutput(BaseModel):
    waste_type: str
    risk_level: str
    cost_impact: dict
    recommended_actions: list
    confidence: float
```

---

## Frontend: Displaying Waste Insights

### React Component Template

```tsx
import React, { useState } from 'react'

export default function WasteAnalyzer() {
  const [result, setResult] = useState(null)
  
  async function analyzeWaste(input) {
    const response = await fetch('/api/analyze-waste', {
      method: 'POST',
      body: JSON.stringify(input)
    })
    const insight = await response.json()
    setResult(insight)
  }
  
  return (
    <div>
      {/* Input form here */}
      
      {result && (
        <div className="insight">
          <h2>
            {getEmoji(result.waste_type)} {result.waste_type}
          </h2>
          
          {/* Severity */}
          <p>Severity: <strong>{result.risk_level}</strong></p>
          
          {/* Cost Impact */}
          <div className="cost">
            <p>Daily Loss: ₹{result.cost_impact.daily_inr}</p>
            <p>Annual Loss: ₹{result.cost_impact.annual_inr}</p>
          </div>
          
          {/* Explanation */}
          <details>
            <summary>Why this was flagged</summary>
            <ul>
              {result.explainability.reasoning.map(r => (
                <li>{r}</li>
              ))}
            </ul>
          </details>
          
          {/* Actions */}
          <div className="actions">
            <h3>What to do:</h3>
            {result.recommended_actions.map(action => (
              <div key={action.priority}>
                <p><strong>{action.priority}:</strong> {action.description}</p>
                <p>Cost: ₹{action.estimated_cost} | Payback: {action.payback_days}d</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
```

---

## Integration Examples

### Example 1: Single Appliance Analysis

```python
# Scenario: Server running at 2 AM, unoccupied building
from energy_waste_reasoning import *

engine = EnergyWasteReasoningEngine(cost_per_kwh=8.0)

signal = PowerDisparitySignal(
    predicted_power_w=2800,
    confidence=0.95,
    baseline_power_w=500,
    actual_power_w=3200,
    variance_percent=540
)

context = OccupancyContext(
    occupancy_status=OccupancyStatus.UNOCCUPIED,
    occupancy_confidence=0.98,
    hour=2,
    day_of_week=3,
    is_weekend=False,
    season="winter"
)

insight = engine.analyze(
    signal=signal,
    context=context,
    appliance_category="Server",
    location_description="Data Center Floor 4",
    duration_hours=8
)

print(insight.to_human_readable())
# Output:
# 🔴 PHANTOM LOAD
# Location: Data Center Floor 4
# Severity: CRITICAL (Confidence: 95%)
# ...
```

### Example 2: Batch Building Analysis

```python
# Analyze entire floor (10 appliances)
all_insights = []
total_daily_waste = 0

for appliance in floor_appliances:
    insight = engine.analyze(
        signal=get_ml_prediction(appliance),
        context=get_current_context(appliance),
        appliance_category=appliance.category,
        location_description=f"Floor {appliance.floor} - {appliance.zone}"
    )
    
    if insight.waste_type != WasteType.NORMAL:
        all_insights.append(insight)
        total_daily_waste += insight.estimated_daily_loss_inr

# Rank by financial impact
ranked = sorted(all_insights, 
                key=lambda x: x.estimated_annual_loss_inr, 
                reverse=True)

print(f"Total daily waste on floor: ₹{total_daily_waste}")
for rank, insight in enumerate(ranked[:5], 1):
    print(f"{rank}. {insight.location}: ₹{insight.estimated_daily_loss_inr}/day")
```

### Example 3: Smart Building Integration

```python
# Real-time monitoring dashboard
import asyncio
from fastapi import FastAPI
from fastapi.sse import EventSourceResponse

app = FastAPI()

@app.get("/waste-stream")
async def waste_stream():
    """Real-time waste alerts via Server-Sent Events"""
    
    async def event_generator():
        while True:
            # Poll appliances
            for appliance in get_all_appliances():
                # Get current readings
                ml_signal = predict_disparity(appliance)
                occupancy = get_occupancy_status()
                
                # Analyze
                insight = reasoning_engine.analyze(
                    signal=ml_signal,
                    context=occupancy,
                    appliance_category=appliance.type,
                    location_description=appliance.location
                )
                
                # Only stream if waste detected
                if insight.risk_level in ["HIGH", "CRITICAL"]:
                    yield f"data: {json.dumps(insight.to_dict())}\n\n"
            
            # Check every 5 minutes
            await asyncio.sleep(300)
    
    return EventSourceResponse(event_generator())
```

---

## Testing Your Implementation

### Test Case 1: Phantom Load (Must Be HIGH Risk)
```json
{
  "appliance_id": "SERVER_1",
  "appliance_category": "server",
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
  "location_description": "Data Center",
  "duration_hours": 8
}
```

**Expected Output:**
```json
{
  "waste_type": "phantom_load",
  "risk_level": "high",
  "estimated_waste_power_w": 2800,
  "cost_impact": {
    "daily_inr": 537.6,
    "annual_inr": 196128
  },
  "confidence": 0.90+
}
```

### Test Case 2: Post-Occupancy Waste (Must Be MEDIUM Risk)
```json
{
  "appliance_id": "LIGHTS_ZONE_A",
  "hour": 20,
  "occupancy_status": "unoccupied",
  "occupancy_confidence": 0.88,
  "power_max": 500,
  "baseline_power_w": 0,
  "actual_power_w": 400,
  "duration_hours": 2
}
```

**Expected Output:**
```json
{
  "waste_type": "post_occupancy",
  "risk_level": "medium",
  "recommended_actions": [
    {
      "priority": "HIGH",
      "description": "Install occupancy-based auto-shutoff"
    }
  ]
}
```

### Test Case 3: Normal Operation (Must Be LOW Risk)
```json
{
  "appliance_id": "FRIDGE_1",
  "hour": 14,
  "occupancy_status": "occupied",
  "occupancy_confidence": 0.95,
  "power_max": 800,
  "baseline_power_w": 300,
  "actual_power_w": 320
}
```

**Expected Output:**
```json
{
  "waste_type": "normal",
  "risk_level": "low",
  "recommended_actions": [],
  "confidence": 1.0
}
```

---

## Customization

### Changing Electricity Tariff
```python
# Default: ₹8/kWh (Indian commercial rate)
engine = EnergyWasteReasoningEngine(
    cost_per_kwh=12.5,  # For Mumbai commercial
    location_id="MUMBAI_OFFICE"
)
```

### Adjusting Waste Detection Thresholds
```python
# In EnergyWasteReasoningEngine._classify_waste_type()
# Modify these values based on your building type:

HIGH_DISPARITY = 500   # watts (currently)
MEDIUM_DISPARITY = 200  # watts (currently)

# For high-sensitivity detection, lower these values
# For low-sensitivity (fewer false positives), raise them
```

### Adding Custom Waste Types
```python
class WasteType(str, Enum):
    PHANTOM_LOAD = "phantom_load"
    POST_OCCUPANCY = "post_occupancy"
    INEFFICIENT_USAGE = "inefficient_usage"
    MAINTENANCE_MODE = "maintenance_mode"  # NEW
    NORMAL = "normal"

# Then update _classify_waste_type() and _generate_recommendations()
```

---

## Deployment Checklist

- [ ] Copy `energy_waste_reasoning.py` to your project
- [ ] Update `app.py` to import and initialize reasoning engine
- [ ] Add new Pydantic models (`WasteAnalysisInput`, `WasteAnalysisOutput`)
- [ ] Implement `/analyze-waste` endpoint
- [ ] Update frontend types to include waste analysis models
- [ ] Create waste analysis form component
- [ ] Test with the three test cases above
- [ ] Update API documentation
- [ ] Set logging for waste detections
- [ ] Deploy to production

---

## Production Monitoring

### What to Monitor
```python
# Log all waste detections
logging.info(f"""
WASTE DETECTED:
  Type: {insight.waste_type}
  Location: {insight.location_description}
  Cost: ₹{insight.estimated_daily_loss_inr}/day
  Actions: {len(insight.actions)} recommended
""")

# Track false positives
if user_marked_false_positive:
    logging.warning(f"False positive: {insight.waste_type}")
    # Adjust thresholds if too frequent

# Calculate total waste
daily_total = sum([i.estimated_daily_loss_inr for i in all_insights])
monthly_total = daily_total * 30
# Alert if exceeds threshold
```

### Metrics to Track
- Total buildings analyzed
- Types of waste detected (distribution)
- Actions implemented (and actual savings realized)
- False positive rate
- User engagement (% insights acted upon)

---

## Troubleshooting

### "Model not loaded" Error
```bash
# Check if model files exist
ls models/xgb_energy_model.pkl
ls models/label_encoders.pkl
ls models/feature_names.pkl

# If missing, retrain
python train_xgb_model.py
```

### "Occupancy status Unknown" → Low Confidence
```python
# If you don't have occupancy data, you have options:
# 1. Use time-based heuristics (night = unoccupied)
# 2. Ask user to input occupancy
# 3. Integrate with calendar/SCADA

# For now:
if occupancy_status == "unknown":
    occupancy_status = "unoccupied" if is_night_hours else "occupied"
    occupancy_confidence = 0.6  # Lower confidence
```

### "Waste never detected despite obvious issues"
```python
# Check if thresholds are too high
print(f"Power disparity detected: {signal.predicted_power_w}W")
print(f"Threshold for HIGH disparity: 500W")

# if predicted < 500, won't flag as phantom load
# Adjust thresholds in _classify_waste_type()
```

---

## Next Steps

1. **Integrate real occupancy data** (BMS, sensors, calendar)
2. **Add seasonal baseline adaptation** (learn from historical data)
3. **Build dashboard** for monitoring waste over time
4. **Set up alerting** for critical waste in real-time
5. **Track actual savings** from implemented recommendations

---

## Support

For questions, check:
- `energy_waste_reasoning.py` - Main reasoning engine code
- `MODEL_POSITIONING.md` - Model explanation and requirements
- `SYSTEM_ARCHITECTURE.md` - System design details
- `app.py` - API endpoint examples

---

**Happy waste detection! 🌍 Every ₹ saved is a step toward sustainability.**
