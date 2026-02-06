# Setup & Deployment Guide

## Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- Git

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/capermax-01/Power-Disparity-Predictor-Real-time-Energy-Consumption-Variance-Analysis.git
cd energy_waste_demo
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Verify Model Artifacts
Ensure these files exist in `models/` directory:
- `power_disparity_model.pkl`
- `feature_scaler.pkl`
- `label_encoders.pkl`
- `feature_names.json`
- `model_metadata.json`

If missing, train the model:
```bash
python3.12 train_and_save_model.py
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Build for production (optional)
npm run build
```

---

## Running the Application

### Option A: Full-Stack (Recommended)

#### Terminal 1 - Backend
```bash
python3.12 serve_model.py
```
Server runs on: `http://localhost:8000`

#### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```
Application runs on: `http://localhost:5173`

#### Terminal 3 - Optional: HTTP Server for Legacy Dashboard
```bash
python3.12 -m http.server 8001
```
Legacy UI at: `http://localhost:8001/dashboard.html`

### Option B: Backend API Only (For External Apps)
```bash
python3.12 serve_model.py
```

API Documentation: `http://localhost:8000/docs`

API Base URL: `http://localhost:8000`

### Option C: Frontend with Production Backend
```bash
cd frontend
npm run dev
```
Then configure the API endpoint in `frontend/constants.tsx` to point to your production server.

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check API status |
| `/model/info` | GET | Get model metadata |
| `/appliances` | GET | List supported appliances |
| `/predict` | POST | Single prediction |
| `/predict/batch` | POST | Batch predictions |

### Example API Call
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "hour": 12,
    "day_of_week": 3,
    "day_of_month": 15,
    "month": 3,
    "is_weekend": 0,
    "appliance_id": "fridge_207",
    "appliance_category": "kitchen",
    "power_reading": 1000,
    "power_max": 1500,
    "power_std_6h": 50,
    "power_mean_6h": 950,
    "power_std_12h": 100,
    "power_mean_12h": 950,
    "power_std_24h": 150,
    "power_mean_24h": 900
  }'
```

---

## Building Frontend for Production

### Build Static Files
```bash
cd frontend
npm run build
```

This creates an optimized `dist/` folder ready for deployment.

### Deploy Frontend

#### Option 1: Serve with Python
```bash
cd frontend/dist
python3.12 -m http.server 8001
```

#### Option 2: Deploy to Netlify
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd frontend
netlify deploy --prod --dir dist
```

#### Option 3: Deploy to Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel --prod
```

---

## Environment Configuration

### Frontend Configuration
Edit `frontend/constants.tsx` or `.env.local`:
```typescript
export const API_URL = 'http://localhost:8000'; // Change for production
```

### Backend Configuration
The server runs on `0.0.0.0:8000` by default.
To use a different port, modify `serve_model.py`:
```python
# Change the port in the last lines
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)  # Custom port
```

---

## Docker Deployment

### Build Docker Image
```dockerfile
# Dockerfile
FROM python:3.12-slim as backend
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

FROM node:18-alpine as frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend .
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY --from=backend /app /app
COPY --from=frontend /app/frontend/dist /app/frontend/dist
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["python", "serve_model.py"]
```

### Run Docker Container
```bash
docker build -t energy-predictor .
docker run -p 8000:8000 energy-predictor
```

---

## Training New Model

To retrain the model with updated data:

```bash
python3.12 train_and_save_model.py
```

This will:
1. Load training data from SQLite database
2. Engineer 15 features
3. Train GradientBoostingRegressor
4. Save artifacts to `models/` directory
5. Display performance metrics

**Expected Output:**
```
================================================================================
TRAINING PIPELINE COMPLETE
================================================================================
✅ All model artifacts saved to: ./models
Files created:
  ✓ power_disparity_model.pkl
  ✓ feature_scaler.pkl
  ✓ label_encoders.pkl
  ✓ feature_names.json
  ✓ model_metadata.json
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess  # Windows

# Kill process or use different port
kill -9 <PID>  # macOS/Linux
python3.12 serve_model.py --port 8002  # Different port
```

### Model Not Loading
```bash
# Check models directory exists
ls models/

# Check model files are present
ls models/*.pkl

# Retrain if necessary
python3.12 train_and_save_model.py
```

### Frontend Connection Issues
1. Ensure backend is running: `http://localhost:8000/health`
2. Check CORS is enabled (it is by default)
3. Verify API URL in frontend configuration

### npm Install Fails
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and lock file
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### Python Dependencies Conflict
```bash
# Create fresh virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Performance Tuning

### Backend
- **Workers:** Use Gunicorn for multiple workers
  ```bash
  pip install gunicorn
  gunicorn serve_model:app -w 4 -b 0.0.0.0:8000
  ```

### Frontend
- **Build optimization:** `npm run build` creates optimized assets
- **Lazy loading:** Components are code-split automatically
- **Caching:** Browser caching enabled via build config

---

## Monitoring

### Backend Health Check
```bash
curl http://localhost:8000/health
```

### Frontend Build Analysis
```bash
cd frontend
npm run build -- --analyze  # View bundle size
```

---

## Support

For issues or questions:
1. Check API docs: `http://localhost:8000/docs`
2. Review error logs in server console
3. Check browser console for frontend errors (F12)
4. Verify database integrity: `ls -lh appliances_consolidated.db`

---

## File Structure

```
energy_waste_demo/
├── frontend/                    # React + Vite application
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/
│   │   ├── components/
│   │   └── constants.tsx       # API configuration
│   ├── public/
│   ├── dist/                   # Production build (created by npm run build)
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── models/
│   ├── power_disparity_model.pkl
│   ├── feature_scaler.pkl
│   ├── label_encoders.pkl
│   ├── feature_names.json
│   └── model_metadata.json
├── serve_model.py              # FastAPI server
├── train_and_save_model.py     # Model training
├── requirements.txt            # Python dependencies
├── README.md                   # Project overview
├── SETUP.md                    # This file
└── LICENSE                     # MIT License
```
