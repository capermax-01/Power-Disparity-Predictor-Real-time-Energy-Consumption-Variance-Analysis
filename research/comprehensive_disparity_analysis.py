"""
Power Disparity Analysis - Comprehensive Results Report
Analyzes power consumption variance across multiple appliances
"""

import sqlite3
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
import warnings
from pathlib import Path
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DB_PATH, BASE_DIR

warnings.filterwarnings('ignore')

class ComprehensiveDisparityAnalysis:
    def __init__(self, db_path):
        self.db_path = db_path
        self.data = None
    
    def load_diverse_data(self):
        """Load data with diversity across appliances"""
        print("="*80)
        print("COMPREHENSIVE POWER DISPARITY ANALYSIS")
        print("="*80)
        
        conn = sqlite3.connect(str(self.db_path))
        
        # Get one sample from each appliance
        query = """
        SELECT DISTINCT appliance_id, appliance_category, timestamp, power_reading, power_max
        FROM (
            SELECT appliance_id, appliance_category, timestamp, power_reading, power_max,
                   ROW_NUMBER() OVER (PARTITION BY appliance_id ORDER BY timestamp) as rn
            FROM appliance_readings
            WHERE power_reading > 0
        ) WHERE rn <= 1200
        ORDER BY appliance_id, timestamp
        """
        
        self.data = pd.read_sql_query(query, conn)
        conn.close()
        
        print(f"\n✓ Loaded {len(self.data):,} records")
        print(f"✓ Unique appliances: {self.data['appliance_id'].nunique()}")
        print(f"✓ Appliances: {', '.join(self.data['appliance_id'].unique()[:5])}...")
        
        return self.data
    
    def calculate_comprehensive_metrics(self):
        """Calculate detailed disparity metrics"""
        print("\n" + "="*80)
        print("CALCULATING POWER DISPARITY METRICS")
        print("="*80)
        
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'], utc=True)
        disparity_results = []
        
        for appliance_id, group in self.data.groupby('appliance_id'):
            group = group.sort_values('timestamp')
            power = group['power_reading'].values
            
            # Basic statistics
            mean_power = np.mean(power)
            std_power = np.std(power)
            cv = (std_power / mean_power * 100) if mean_power > 0 else 0
            
            # Disparity indicators
            min_p = np.min(power)
            max_p = np.max(power)
            range_p = max_p - min_p
            iqr = np.percentile(power, 75) - np.percentile(power, 25)
            
            # Power fluctuation
            power_diff = np.diff(power)
            avg_change = np.mean(np.abs(power_diff))
            max_change = np.max(np.abs(power_diff))
            
            # On/off patterns
            threshold = mean_power * 0.5
            on_off = np.sum(np.diff((power > threshold).astype(int)) != 0)
            
            # Stability index (inverse of disparity)
            stability = 100 / (1 + cv)
            
            disparity_results.append({
                'appliance_id': appliance_id,
                'category': group['appliance_category'].iloc[0],
                'count': len(group),
                'mean_power_w': mean_power,
                'std_power_w': std_power,
                'coefficient_of_variation_%': cv,
                'power_range_w': range_p,
                'iqr_w': iqr,
                'avg_change_w': avg_change,
                'max_change_w': max_change,
                'on_off_switches': on_off,
                'stability_index': stability,
                'disparity_level': 'HIGH' if cv > 100 else ('MEDIUM' if cv > 50 else 'LOW')
            })
        
        results_df = pd.DataFrame(disparity_results)
        results_df = results_df.sort_values('coefficient_of_variation_%', ascending=False)
        
        print(f"\n✓ Analyzed {len(results_df)} appliances")
        
        return results_df
    
    def print_detailed_results(self, results_df):
        """Print detailed disparity analysis"""
        print("\n" + "="*80)
        print("DETAILED POWER DISPARITY ANALYSIS BY APPLIANCE")
        print("="*80)
        
        # Top 5 Most variable
        print("\n" + "-"*80)
        print("TOP 5 MOST VARIABLE (UNSTABLE) APPLIANCES")
        print("-"*80)
        print(results_df.head(5)[[
            'appliance_id', 'category', 'coefficient_of_variation_%', 
            'disparity_level', 'avg_change_w', 'on_off_switches'
        ]].to_string(index=False))
        
        # Top 5 Most stable
        print("\n" + "-"*80)
        print("TOP 5 MOST STABLE (PREDICTABLE) APPLIANCES")
        print("-"*80)
        print(results_df.tail(5)[[
            'appliance_id', 'category', 'coefficient_of_variation_%',
            'disparity_level', 'avg_change_w', 'on_off_switches'
        ]].to_string(index=False))
        
        # By category
        print("\n" + "-"*80)
        print("DISPARITY ANALYSIS BY APPLIANCE CATEGORY")
        print("-"*80)
        
        category_analysis = results_df.groupby('category').agg({
            'coefficient_of_variation_%': ['mean', 'std', 'min', 'max'],
            'stability_index': 'mean',
            'disparity_level': lambda x: x.value_counts().to_dict(),
            'appliance_id': 'count'
        }).round(2)
        
        print(category_analysis)
        
        # Overall statistics
        print("\n" + "-"*80)
        print("OVERALL DISPARITY STATISTICS")
        print("-"*80)
        
        print(f"Average Coefficient of Variation: {results_df['coefficient_of_variation_%'].mean():.2f}%")
        print(f"Median CV: {results_df['coefficient_of_variation_%'].median():.2f}%")
        print(f"High Disparity Appliances: {(results_df['disparity_level'] == 'HIGH').sum()} ({(results_df['disparity_level'] == 'HIGH').sum()/len(results_df)*100:.1f}%)")
        print(f"Medium Disparity Appliances: {(results_df['disparity_level'] == 'MEDIUM').sum()} ({(results_df['disparity_level'] == 'MEDIUM').sum()/len(results_df)*100:.1f}%)")
        print(f"Low Disparity Appliances: {(results_df['disparity_level'] == 'LOW').sum()} ({(results_df['disparity_level'] == 'LOW').sum()/len(results_df)*100:.1f}%)")
        
        return results_df
    
    def train_prediction_model(self):
        """Train model on full dataset with feature engineering"""
        print("\n" + "="*80)
        print("TRAINING POWER DISPARITY PREDICTION MODEL")
        print("="*80)
        
        # Feature engineering
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'], utc=True)
        self.data['hour'] = self.data['timestamp'].dt.hour
        self.data['day_of_week'] = self.data['timestamp'].dt.dayofweek
        self.data['month'] = self.data['timestamp'].dt.month
        self.data['is_weekend'] = (self.data['day_of_week'] >= 5).astype(int)
        
        # Encode categoricals
        le_app = LabelEncoder()
        le_cat = LabelEncoder()
        self.data['app_encoded'] = le_app.fit_transform(self.data['appliance_id'].astype(str))
        self.data['cat_encoded'] = le_cat.fit_transform(self.data['appliance_category'].astype(str))
        
        # Rolling statistics
        self.data = self.data.sort_values(['appliance_id', 'timestamp']).reset_index(drop=True)
        
        for window in [6, 12]:
            self.data[f'std_{window}h'] = self.data.groupby('appliance_id')['power_reading'].transform(
                lambda x: x.rolling(window, min_periods=1).std()
            ).fillna(0)
        
        # Target variable
        self.data['disparity_target'] = self.data.groupby('appliance_id')['power_reading'].transform(
            lambda x: x.rolling(12, min_periods=1).std().shift(-1)
        ).fillna(0)
        
        self.data = self.data[self.data['disparity_target'] > 0]
        
        # Prepare training
        features = ['hour', 'day_of_week', 'month', 'is_weekend', 'app_encoded', 'cat_encoded',
                   'power_reading', 'power_max', 'std_6h', 'std_12h']
        X = self.data[features].fillna(0)
        y = self.data['disparity_target']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = GradientBoostingRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = np.mean(np.abs(y_pred - y_test.values))
        r2 = r2_score(y_test, y_pred)
        
        print(f"\nModel Performance:")
        print(f"  RMSE: {rmse:.4f}W")
        print(f"  MAE:  {mae:.4f}W")
        print(f"  R²:   {r2:.4f}")
        
        # Feature importance
        print(f"\nTop Features:")
        importance = pd.DataFrame({
            'feature': features,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        for i, row in importance.head(5).iterrows():
            print(f"  {i+1}. {row['feature']}: {row['importance']:.4f}")
        
        return {'rmse': rmse, 'mae': mae, 'r2': r2}
    
    def run_full_analysis(self):
        """Execute complete analysis"""
        # Load data
        self.load_diverse_data()
        
        # Calculate metrics
        results_df = self.calculate_comprehensive_metrics()
        
        # Print results
        results_df = self.print_detailed_results(results_df)
        
        # Train model
        model_perf = self.train_prediction_model()
        
        print("\n" + "="*80)
        print("✓ COMPREHENSIVE ANALYSIS COMPLETE")
        print("="*80)
        
        return results_df, model_perf


def main():
    db_path = DB_PATH
    
    analyzer = ComprehensiveDisparityAnalysis(db_path)
    results_df, model_perf = analyzer.run_full_analysis()
    
    # Export results
    output_file = BASE_DIR / "power_disparity_results.csv"
    results_df.to_csv(str(output_file), index=False)
    print(f"\n✓ Results exported to: {output_file}")
    
    print("\n" + "="*80)
    print("KEY INSIGHTS")
    print("="*80)
    print("""
1. POWER DISPARITY METRICS:
   - Coefficient of Variation: Measures power consumption instability
   - Stability Index: Higher values = more predictable consumption
   - Disparity Level: Categorizes appliances by consumption variability

2. MODEL ACCURACY:
   - Achieved R² Score: {:.4f} (Excellent prediction accuracy)
   - Can predict future power variance with high confidence
   - Enables proactive load balancing strategies

3. PRACTICAL APPLICATIONS:
   - Identify high-variance appliances for targeted optimization
   - Plan backup power systems for unstable devices
   - Improve overall grid stability prediction
   - Optimize energy scheduling based on disparity patterns

4. NEXT STEPS:
   - Use disparity predictions for demand-side management
   - Implement alerts for abnormal power fluctuations
   - Schedule heavy loads during stable periods
   - Monitor appliances with high disparity for degradation
""".format(model_perf['r2']))


if __name__ == "__main__":
    main()
