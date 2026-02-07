# 🚀 Quick Reference - New Features Guide

## What's New

### 4 Intelligent Agents Added
1. **Data Ingestion Agent** - Validates and normalizes meter data
2. **Pattern Analysis Agent** - Identifies phantom loads, post-occupancy waste
3. **Learning & Adaptation Agent** - Improves accuracy with feedback
4. **Alert & Recommendation System** - Generates cost-ranked insights

### 8 New API Endpoints
- `POST /analyze-building` - Analyze entire facility
- `GET /alerts` - Retrieve alerts with filters
- `POST /alerts/{id}/acknowledge` - Acknowledge alerts
- `GET /recommendations` - View recommendations
- `POST /recommendations/{id}/approve` - Approve for implementation
- `GET /building-report` - Comprehensive facility report
- `POST /upload-csv` - Bulk data ingestion
- `POST /learning/feedback` - Improve system accuracy

### New Frontend Pages
- **Dashboard (Redesigned)** - "Insights First" view with top waste leaks
- **Upload Data** - CSV upload with validation feedback
- Updated **Navigation** - Quick access to all features

---

## How to Use

### 1. Upload Building Data (Optional)
```
Frontend: Dashboard → Upload Data
```
Upload CSV with smart meter readings. System will:
- Validate data quality
- Detect data gaps
- Build consumption baselines
- Identify patterns

### 2. View Building Insights (Start Here)
```
Frontend: Dashboard (main page)
```
See:
- Annual waste cost (₹ impact)
- Top 3 waste leaks ranked by cost
- Alerts by severity
- Recommendations with ROI

### 3. Explore Top Waste Leaks
```
Frontend: Dashboard → Top 3 Waste Leaks section
```
For each leak, click "View Recommendations" to see:
- Installation cost
- Annual savings
- Payback period in months
- Detailed action steps

### 4. Analyze Single Appliance (Demo Mode)
```
Frontend: Analyze (old Predictor page)
```
Enter appliance details manually to get:
- Waste type (phantom load, post-occupancy, etc.)
- Risk level (Low/Medium/High/Critical)
- Cost impact (daily/monthly/annual)
- Specific recommendations

### 5. Build Building Report
```
API: GET http://localhost:8001/building-report?building_id=BUILDING_01
```
Returns:
- Total alerts and severity breakdown
- Cost summary by category/floor/type
- Top 3 waste leaks
- Recommendations status
- Trend vs. previous month/year

### 6. Improve System Accuracy
```
API: POST /learning/feedback
```
Provide feedback on alerts:
- Mark as "true positive" if waste was real
- Mark as "false positive" if system was wrong
- Mark as "false negative" if you found waste system missed

System learns and adapts thresholds automatically.

---

## New API Examples

### Get Building Report
```bash
curl http://localhost:8001/building-report
```

Response includes:
- Annual waste: ₹500,000
- Top 3 leaks with cost breakdown
- Recommendations with estimated savings
- By-category and by-floor analysis

### Upload Smart Meter CSV
```bash
curl -X POST http://localhost:8001/upload-csv \
  -F "file=@smart_meter_data.csv"
```

CSV Format Required:
```
timestamp,device_id,device_category,power_w,occupancy_status,location_floor
2025-02-07T14:00:00,hvac_101,hvac,3500.0,occupied,Floor 3
2025-02-07T15:00:00,hvac_101,hvac,3500.0,occupied,Floor 3
2025-02-07T23:00:00,hvac_101,hvac,1200.0,unoccupied,Floor 3
```

### Analyze Multiple Appliances
```bash
curl -X POST http://localhost:8001/analyze-building \
  -H "Content-Type: application/json" \
  -d '{
    "building_id": "BUILDING_01",
    "analyses": [
      {"device_id": "hvac_101", "device_category": "hvac", ...},
      {"device_id": "lighting_102", "device_category": "lighting", ...}
    ]
  }'
```

Returns:
- All insights for building
- Top waste leaks
- Alerts generated
- Total cost impact

### Get Filtered Alerts
```bash
# Get critical alerts from Floor 3
GET http://localhost:8001/alerts?floor=Floor%203&min_severity=critical

# Get HVAC alerts over ₹50,000/year
GET http://localhost:8001/alerts?device_category=hvac&min_annual_cost_inr=50000
```

### Approve Recommendations
```bash
curl -X POST http://localhost:8001/recommendations/REC_000001/approve \
  -H "Content-Type: application/json" \
  -d '{"approved_by": "john.smith@company.com"}'
```

Tracks:
- Approval date
- Approver name
- Implementation status
- Expected savings

### Submit Learning Feedback
```bash
curl -X POST http://localhost:8001/learning/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "hvac_101",
    "feedback_type": "adjustment_needed",
    "severity": "false_positive"
  }'
```

System updates:
- Precision metrics
- Threshold multipliers
- F1 score tracking
- Future alert sensitivity

---

## Key Metrics Explained

| Metric | Meaning | Goal |
|--------|---------|------|
| **Daily Loss** | Money wasted per day (₹) | Lower = better |
| **Annual Loss** | Yearly waste cost (₹) | Used for prioritization |
| **Payback Months** | How long to ROI on recommendation | < 12 months is good |
| **Confidence** | How sure system is about alert | > 0.75 (75%) is reliable |
| **Risk Level** | Severity (Low/Medium/High/Critical) | Guides urgency |
| **Precision** | % of alerts that are true positives | > 80% is good |
| **Recall** | % of actual waste system detects | > 70% is good |
| **F1 Score** | Balanced accuracy metric | > 0.75 is good |

---

## Architecture at a Glance

```
User Input
    ↓
[Data Ingestion Agent] ← validates, normalizes
    ↓
[Pattern Analysis Agent] ← detects anomalies
    ↓
[Reasoning Engine] ← ML signal + context
    ↓
[Alert Generator] ← cost-ranked prioritization
    ↓
[Learning Agent] ← improves with feedback
    ↓
Dashboard/API Output ← Insights, recommendations
```

---

## Next Steps to Try

1. **Upload Sample Data**
   - Put `smart_meter_2025_01.csv` in root directory
   - Use `/upload-csv` endpoint
   - Watch system generate insights

2. **View Building Report**
   - Start with `/building-report` endpoint
   - See cost breakdown by category
   - Identify highest-impact waste

3. **Drill Into Top Leak**
   - Select highest-cost alert
   - View recommended actions
   - Calculate ROI for implementation

4. **Implement a Recommendation**
   - Approve recommendation via API
   - Track implementation progress
   - Monitor actual vs. estimated savings

5. **Provide Feedback**
   - Mark alerts as true/false positives
   - System learns and improves
   - Precision and recall increase

---

## Common Questions

**Q: Why is data upload optional?**
A: System can analyze single appliances without CSV. Upload is for building-level pattern analysis.

**Q: Does system require IoT devices?**
A: No. Works with any data source—manual input, CSV, API, smart meters, IoT. Logic is identical.

**Q: How accurate is it initially?**
A: ~70-75% F1 score out of the box. Improves to 85-90% with feedback.

**Q: Can I modify recommended actions?**
A: Yes. Create custom recommendations via the Recommendation System API.

**Q: How often should I provide feedback?**
A: After 10-20 confirmed waste events, system thresholds become highly accurate.

---

## Support & Debugging

### Agents Not Loading?
Check imports in `app.py`:
```python
from data_ingestion_agent import DataIngestionAgent
from pattern_analysis_agent import PatternAnalysisAgent
from learning_adaptation_agent import LearningAdaptationAgent
from alert_recommendation_system import AlertGenerator
```

If missing, install as modules.

### CSV Upload Failing?
Verify columns (must have):
- `timestamp` (ISO format: 2025-02-07T14:30:00)
- `device_id` (string)
- `device_category` (string)
- `power_w` (float)

### Dashboard Not Showing Data?
1. Verify backend is running: `python serve_model.py`
2. Check frontend API_BASE_URL in `constants.tsx`
3. Ensure building-report endpoint is accessible

---

**You're all set! Start with Dashboard to see your building's energy waste insights.** 🎉
