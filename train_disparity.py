"""
Train, validate, and save the Power Disparity Prediction Model
Complete production-ready model pipeline
"""

import sqlite3
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
from pathlib import Path
import json
import warnings
from config import DB_PATH, MODEL_DIR, DISPARITY_SAMPLE_SIZE, TEST_SIZE, RANDOM_STATE

warnings.filterwarnings('ignore')

class ModelTrainer:
    def __init__(self, db_path=DB_PATH, model_dir=MODEL_DIR):
        self.db_path = db_path
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        self.model = None
        self.scaler = None
        self.label_encoders = {}
        self.feature_names = []
        
    def load_training_data(self):
        """Load data from consolidated database"""
        print("="*80)
        print("LOADING TRAINING DATA")
        print("="*80)
        
        conn = sqlite3.connect(str(self.db_path))
        query = """
            SELECT appliance_id, appliance_category, timestamp, power_reading, power_max
            FROM appliance_readings
            WHERE power_reading > 0 AND power_max > 0
            ORDER BY appliance_id, timestamp
            LIMIT 40000
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        print(f"✓ Loaded {len(df):,} records")
        print(f"✓ Unique appliances: {df['appliance_id'].nunique()}")
        
        return df
    
    def engineer_features(self, df):
        """Engineer all features for the model"""
        print("\n" + "="*80)
        print("ENGINEERING FEATURES")
        print("="*80)
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        
        # Temporal features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['day_of_month'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Encode categoricals
        for col in ['appliance_id', 'appliance_category']:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df[col + '_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
            else:
                df[col + '_encoded'] = self.label_encoders[col].transform(df[col].astype(str))
        
        # Sort for rolling operations
        df = df.sort_values(['appliance_id', 'timestamp']).reset_index(drop=True)
        
        # Rolling statistics
        for window in [6, 12, 24]:
            df[f'power_std_{window}h'] = df.groupby('appliance_id')['power_reading'].transform(
                lambda x: x.rolling(window=window, min_periods=1).std()
            ).fillna(0)
            
            df[f'power_mean_{window}h'] = df.groupby('appliance_id')['power_reading'].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean()
            ).fillna(0)
        
        print("✓ Features engineered successfully")
        
        return df
    
    def create_target(self, df):
        """Create disparity target variable"""
        df['disparity_target'] = df.groupby('appliance_id')['power_reading'].transform(
            lambda x: x.rolling(window=12, min_periods=1).std().shift(-1)
        ).fillna(0)
        
        # Remove invalid samples
        df = df[df['disparity_target'] > 0]
        df = df[np.isfinite(df['disparity_target'])]
        
        print(f"✓ Target variable created, {len(df):,} valid samples")
        
        return df
    
    def prepare_data(self, df):
        """Prepare features and target"""
        feature_cols = [
            'hour', 'day_of_week', 'day_of_month', 'month', 'is_weekend',
            'appliance_id_encoded', 'appliance_category_encoded',
            'power_reading', 'power_max',
            'power_std_6h', 'power_mean_6h',
            'power_std_12h', 'power_mean_12h',
            'power_std_24h', 'power_mean_24h'
        ]
        
        self.feature_names = feature_cols
        
        X = df[feature_cols].fillna(0)
        y = df['disparity_target']
        
        # Remove infinities
        X = X.replace([np.inf, -np.inf], 0)
        
        print(f"✓ Data prepared: {X.shape[0]} samples, {X.shape[1]} features")
        
        return X, y, feature_cols
    
    def train_model(self, X, y):
        """Train the disparity prediction model"""
        print("\n" + "="*80)
        print("TRAINING MODEL")
        print("="*80)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = GradientBoostingRegressor(
            n_estimators=150,
            max_depth=6,
            learning_rate=0.08,
            subsample=0.8,
            random_state=42
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"✓ Model trained successfully!")
        print(f"\nPerformance Metrics:")
        print(f"  R² Score: {r2:.4f}")
        print(f"  RMSE: {rmse:.4f}W")
        print(f"  MAE: {mae:.4f}W")
        
        metrics = {
            'r2_score': float(r2),
            'rmse': float(rmse),
            'mae': float(mae),
            'n_samples_train': int(len(X_train)),
            'n_samples_test': int(len(X_test))
        }
        
        return metrics
    
    def save_model(self):
        """Save model and all artifacts"""
        print("\n" + "="*80)
        print("SAVING MODEL")
        print("="*80)
        
        # Save model
        model_path = self.model_dir / "power_disparity_model.pkl"
        joblib.dump(self.model, model_path)
        print(f"✓ Model saved: {model_path}")
        
        # Save scaler
        scaler_path = self.model_dir / "feature_scaler.pkl"
        joblib.dump(self.scaler, scaler_path)
        print(f"✓ Scaler saved: {scaler_path}")
        
        # Save encoders
        encoders_path = self.model_dir / "label_encoders.pkl"
        joblib.dump(self.label_encoders, encoders_path)
        print(f"✓ Encoders saved: {encoders_path}")
        
        # Save feature names
        features_path = self.model_dir / "feature_names.json"
        with open(features_path, 'w') as f:
            json.dump(self.feature_names, f)
        print(f"✓ Features saved: {features_path}")
        
        # Save metadata
        metadata = {
            'model_type': 'GradientBoostingRegressor',
            'features': self.feature_names,
            'n_features': len(self.feature_names),
            'encoders': list(self.label_encoders.keys()),
            'status': 'production'
        }
        
        metadata_path = self.model_dir / "model_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✓ Metadata saved: {metadata_path}")
        
        print(f"\n✅ All model artifacts saved to: {self.model_dir}")
        
        return model_path
    
    def run_complete_training(self):
        """Execute full training pipeline"""
        print("\n" + "#"*80)
        print("# POWER DISPARITY MODEL - COMPLETE TRAINING PIPELINE")
        print("#"*80)
        
        # Load data
        df = self.load_training_data()
        
        # Engineer features
        df = self.engineer_features(df)
        
        # Create target
        df = self.create_target(df)
        
        # Prepare data
        X, y, feature_cols = self.prepare_data(df)
        
        # Train
        metrics = self.train_model(X, y)
        
        # Save
        self.save_model()
        
        print("\n" + "="*80)
        print("✅ TRAINING PIPELINE COMPLETE")
        print("="*80)
        
        return metrics


def main():
    trainer = ModelTrainer()
    metrics = trainer.run_complete_training()
    
    print("\n" + "="*80)
    print("MODEL READY FOR DEPLOYMENT")
    print("="*80)
    print(f"""
Model saved to: {model_dir}

Files created:
  ✓ power_disparity_model.pkl (Main model)
  ✓ feature_scaler.pkl (Feature scaling)
  ✓ label_encoders.pkl (Category encoding)
  ✓ feature_names.json (Feature list)
  ✓ model_metadata.json (Metadata)

Next steps:
  1. Start the backend: python serve_model.py
  2. Open the UI: Open dashboard.html in browser
  3. Make predictions via the web interface
""")


if __name__ == "__main__":
    main()
