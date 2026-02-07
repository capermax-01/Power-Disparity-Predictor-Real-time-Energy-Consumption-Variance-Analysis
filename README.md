# Power Disparity Predictor - Real-time Energy Consumption Variance Analysis

A complete full-stack ML application for predicting and analyzing power consumption disparity across appliances using Python backend (FastAPI + XGBoost) and React/Vite frontend.

## 🎯 Project Overview

- **Backend:** FastAPI server with 96.74% R² accuracy model prediction
- **Frontend:** Modern React + Vite UI with real-time predictions and AI reasoning
- **Database:** SQLite with 213.4M records from 42 appliances
- **Model:** XGBoost Regressor with 12 engineered features
- **Deployment:** Full-stack Docker-ready application

## 📁 Project Structure

```
energy_waste_demo/
├── frontend/                         # React + Vite frontend application
│   ├── src/                          # Frontend source code
│   ├── index.html                    # Entry HTML
│   ├── vite.config.ts               # Vite configuration
│   ├── tsconfig.json                # TypeScript configuration
│   └── package.json                 # Frontend dependencies
├── models/                           # Trained ML model artifacts
│   ├── xgb_energy_model.pkl         # Trained XGBoost model
│   ├── label_encoders.pkl           # Category encoders
│   ├── feature_names.pkl            # Feature metadata
│   └── model_metadata.json          # Model information
├── app.py                            # Main FastAPI server with Reasoning Engine
├── train_xgb_model.py                # Model training pipeline
├── energy_waste_reasoning.py         # AI Reasoning Engine logic
├── ai_energy_analyst.py              # CSV Data Analysis agent
├── consolidate_appliances.py         # Database consolidation utility
├── comprehensive_disparity_analysis.py # Data analysis script
├── requirements.txt                 # Python dependencies
├── LICENSE                          # MIT License
└── README.md                        # This file
```

## ⚡ Quick Start (Both Backend & Frontend)

### Prerequisites
- **Python 3.12+**
- **Node.js 18+** and npm
- **Git**

### 1. Clone Repository
```bash
git clone https://github.com/capermax-01/Power-Disparity-Predictor-Real-time-Energy-Consumption-Variance-Analysis.git
cd energy_waste_demo
```

### 2. Backend Setup & Run
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI backend (runs on http://localhost:8001)
python app.py
```

### 3. Frontend Setup & Run (NEW TERMINAL)
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server (runs on http://localhost:5173)
npm run dev
```

### 4. Access Application
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8001
- **API Docs:** http://localhost:8001/docs

---

## Installation

### 1. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt
```

### 2. Data Consolidation (Already Done)

The appliance data has been consolidated into a SQLite database:

```bash
python consolidate_appliances.py
```

This creates:
- `appliances_consolidated.db` - 213M records from 42 appliances

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

## Deploying the API

### 1. Start FastAPI Server

```bash
# Development server
python app.py

# Or with specific host/port
uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

## API Endpoints

### 1. Health Check
`GET /health`

### 2. Single Prediction
`POST /predict`

### 3. Energy Waste Analysis (AI-Powered Reasoning)
`POST /analyze-waste`

### 4. Batch Waste Analysis
`POST /analyze-waste/batch`

---

## 🤖 AI-Based Energy Waste Detection & Reasoning Engine

### Overview
The application includes an intelligent reasoning engine that analyzes power consumption patterns and identifies invisible energy waste using explainable AI.

### Waste Detection Capabilities

The reasoning engine identifies **4 types of energy waste:**

1. **Phantom Load** - Devices consuming power while powered off
2. **Post-Occupancy Waste** - Appliances left running after people leave
3. **Inefficient Usage** - Misuse or suboptimal settings
4. **Normal Operation** - No waste detected

### Key Features

✅ **Data Source Agnostic** - Consumes normalized power data from any source  
✅ **Explainable AI** - Every decision includes reasoning and confidence  
✅ **Cost Impact** - Automatic calculation of daily/monthly/annual waste costs  
✅ **Actionable Recommendations** - Specific, tailored action items  
✅ **Risk Scoring** - Low/Medium/High/Critical severity levels  

---

## 📚 Documentation

For detailed integration instructions and architecture explanation, see:
- **[DATA_SOURCE_FLEXIBILITY.md](DATA_SOURCE_FLEXIBILITY.md)** - How the system scales from demo to production
- **[FRONTEND.md](FRONTEND.md)** - Frontend UI guide
- **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)** - System design overview
- **[API_REFERENCE.md](API_REFERENCE.md)** - Detailed API documentation

## Model Details

### Model Type
- **Algorithm:** XGBoost Regression
- **Estimators:** 200
- **Max Depth:** 8
- **Learning Rate:** 0.05

### Features (12 total)
1. **hour** (0-23)
2. **day_of_week** (0-6)
3. **day_of_month** (1-31)
4. **month** (1-12)
5. **quarter** (1-4)
6. **is_weekend** (0-1)
7. **appliance_id_encoded**
8. **appliance_category_encoded**
9. **power_max**
10. **power_ratio**
11. **power_rolling_mean_24**
12. **power_rolling_std_24**

## Troubleshooting

### Model not loading
```
Check that models/ directory exists and contains:
- xgb_energy_model.pkl
- label_encoders.pkl
- feature_names.pkl
```

### Database connection issues
```bash
# Verify database exists
ls appliances_consolidated.db
```

## License

This project is for demonstration purposes.
