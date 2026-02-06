"""
Train XGBoost model on consolidated appliance energy data
"""

import sqlite3
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class ApplianceEnergyPredictor:
    def __init__(self, db_path, model_output_dir):
        self.db_path = db_path
        self.model_output_dir = Path(model_output_dir)
        self.model_output_dir.mkdir(exist_ok=True)
        
        self.model = None
        self.scalers = {}
        self.label_encoders = {}
        self.feature_names = None
        
    def load_data_from_db(self, sample_size=100000):
        """Load data from SQLite database"""
        print(f"Loading {sample_size:,} records from database...")
        
        conn = sqlite3.connect(str(self.db_path))
        query = f"""
            SELECT appliance_id, appliance_category, timestamp, power_reading, power_max
            FROM appliance_readings
            WHERE power_reading IS NOT NULL AND power_reading > 0
            LIMIT {sample_size}
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        print(f"✓ Loaded {len(df):,} records")
        return df
    
    def engineer_features(self, df):
        """Create features for the model"""
        print("\nEngineering features...")
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        
        # Extract temporal features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['day_of_month'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['quarter'] = df['timestamp'].dt.quarter
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Encode categorical features
        for col in ['appliance_id', 'appliance_category']:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df[col + '_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
            else:
                df[col + '_encoded'] = self.label_encoders[col].transform(df[col].astype(str))
        
        # Handle power_max
        df['power_max'] = df['power_max'].fillna(df['power_reading'].mean())
        df['power_ratio'] = df['power_reading'] / (df['power_max'] + 1)
        
        # Rolling statistics
        df = df.sort_values('timestamp').reset_index(drop=True)
        df['power_rolling_mean_24'] = df.groupby('appliance_id')['power_reading'].transform(
            lambda x: x.rolling(window=24, min_periods=1).mean()
        )
        df['power_rolling_std_24'] = df.groupby('appliance_id')['power_reading'].transform(
            lambda x: x.rolling(window=24, min_periods=1).std()
        ).fillna(0)
        
        print("✓ Features engineered")
        return df
    
    def prepare_training_data(self, df):
        """Prepare data for model training"""
        print("\nPreparing training data...")
        
        # Select features
        feature_cols = [
            'hour', 'day_of_week', 'day_of_month', 'month', 'quarter', 'is_weekend',
            'appliance_id_encoded', 'appliance_category_encoded',
            'power_max', 'power_ratio', 'power_rolling_mean_24', 'power_rolling_std_24'
        ]
        
        self.feature_names = feature_cols
        
        X = df[feature_cols].copy()
        y = df['power_reading'].copy()
        
        # Handle missing values
        X = X.fillna(0)
        
        print(f"✓ Features: {len(feature_cols)}")
        print(f"  Shape: {X.shape}")
        
        return X, y
    
    def train_model(self, X, y, test_size=0.2):
        """Train XGBoost model"""
        print("\nTraining XGBoost model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        print(f"Train set: {X_train.shape}")
        print(f"Test set: {X_test.shape}")
        
        # Create and train XGBoost model
        self.model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='reg:squarederror',
            random_state=42,
            n_jobs=-1,
            eval_metric='rmse',
            early_stopping_rounds=20
        )
        
        # Train with early stopping
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"\n{'='*60}")
        print("MODEL PERFORMANCE")
        print(f"{'='*60}")
        print(f"RMSE: {rmse:.4f}")
        print(f"MAE:  {mae:.4f}")
        print(f"R²:   {r2:.4f}")
        print(f"{'='*60}")
        
        return {
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'n_samples': len(X_train) + len(X_test)
        }
    
    def save_model(self):
        """Save model and encoders"""
        print("\nSaving model...")
        
        model_path = self.model_output_dir / "xgb_energy_model.pkl"
        encoders_path = self.model_output_dir / "label_encoders.pkl"
        features_path = self.model_output_dir / "feature_names.pkl"
        metadata_path = self.model_output_dir / "model_metadata.txt"
        
        # Save model
        joblib.dump(self.model, model_path)
        print(f"✓ Model saved: {model_path}")
        
        # Save label encoders
        joblib.dump(self.label_encoders, encoders_path)
        print(f"✓ Encoders saved: {encoders_path}")
        
        # Save feature names
        joblib.dump(self.feature_names, features_path)
        print(f"✓ Feature names saved: {features_path}")
        
        # Save metadata
        with open(metadata_path, 'w') as f:
            f.write("XGBoost Energy Prediction Model\n")
            f.write("="*50 + "\n\n")
            f.write(f"Features: {len(self.feature_names)}\n")
            f.write(f"Feature List:\n")
            for feat in self.feature_names:
                f.write(f"  - {feat}\n")
            f.write(f"\nLabel Encoders:\n")
            for enc_name in self.label_encoders.keys():
                f.write(f"  - {enc_name}\n")
        
        print(f"✓ Metadata saved: {metadata_path}")
        
        return model_path, encoders_path, features_path
    
    def feature_importance(self, top_n=10):
        """Display feature importance"""
        print(f"\nTop {top_n} Important Features:")
        print("="*50)
        
        importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(importance.head(top_n).to_string(index=False))
        
        return importance
    
    def run_training_pipeline(self):
        """Run complete training pipeline"""
        print("\n" + "="*70)
        print("XGBOOST TRAINING PIPELINE")
        print("="*70)
        
        # Load data
        df = self.load_data_from_db(sample_size=100000)
        
        # Engineer features
        df = self.engineer_features(df)
        
        # Prepare data
        X, y = self.prepare_training_data(df)
        
        # Train model
        metrics = self.train_model(X, y)
        
        # Save model
        self.save_model()
        
        # Feature importance
        importance = self.feature_importance(top_n=10)
        
        print("\n" + "="*70)
        print("✓ TRAINING PIPELINE COMPLETED")
        print("="*70)
        
        return metrics, importance


def main():
    db_path = r"C:\Users\ASUS\OneDrive\Desktop\energy_waste_demo\appliances_consolidated.db"
    output_dir = r"C:\Users\ASUS\OneDrive\Desktop\energy_waste_demo\models"
    
    predictor = ApplianceEnergyPredictor(db_path, output_dir)
    metrics, importance = predictor.run_training_pipeline()
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE - MODEL READY FOR DEPLOYMENT")
    print("="*70)
    print(f"\nModel saved in: {output_dir}")
    print("\nUse FastAPI app with:")
    print("  - xgb_energy_model.pkl")
    print("  - label_encoders.pkl")
    print("  - feature_names.pkl")


if __name__ == "__main__":
    main()
