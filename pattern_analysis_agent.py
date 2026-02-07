"""
Pattern Analysis Agent
Identifies energy waste patterns in smart meter data.
Detects post-occupancy waste, phantom loads, and abnormal usage patterns.

RESPONSIBILITIES:
1. Establish energy baseline (normal expected consumption)
2. Detect phantom loads (always-on devices consuming power 24/7)
3. Identify post-occupancy waste (devices left on after occupants leave)
4. Recognize daily, weekly, and seasonal patterns
5. Compare current usage vs historical baseline
6. Detect repeating spike patterns
7. Calculate deviation metrics for anomaly detection
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict


class PatternType(str, Enum):
    """Types of patterns detected"""
    PHANTOM_LOAD = "phantom_load"  # Always-on consumption
    POST_OCCUPANCY = "post_occupancy"  # Left on after hours
    REPEATING_SPIKE = "repeating_spike"  # Regular peak usage
    ANOMALOUS_SPIKE = "anomalous_spike"  # Unexpected spike
    SHIFT_PATTERN = "shift_pattern"  # Usage during shifts
    WEEKEND_PATTERN = "weekend_pattern"  # Weekday vs weekend diff
    NORMAL = "normal"  # Expected pattern


class AnomalyType(str, Enum):
    """Types of anomalies"""
    ABOVE_BASELINE = "above_baseline"
    BELOW_BASELINE = "below_baseline"
    UNEXPECTED_PEAK = "unexpected_peak"
    MORNING_SPIKE = "morning_spike"
    EVENING_SPIKE = "evening_spike"
    NIGHT_CONSUMPTION = "night_consumption"


@dataclass
class EnergyBaseline:
    """Energy consumption baseline for a device"""
    device_id: str
    device_category: str
    
    # Hourly baseline (24 values: avg power for each hour)
    hourly_baseline: Dict[int, float]  # hour -> avg_power_w
    hourly_baseline_std: Dict[int, float]  # hour -> std_dev
    
    # Daily baseline
    weekday_daily_avg_w: float
    weekend_daily_avg_w: float
    
    # Expected ranges
    max_expected_power_w: float
    min_expected_power_w: float
    
    # Seasonal variations
    seasonal_multiplier: Dict[str, float] = field(default_factory=lambda: {
        'winter': 1.15,
        'spring': 1.0,
        'summer': 1.05,
        'fall': 1.0
    })
    
    periods_analyzed: int = 0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class PatternSignature:
    """Signature of detected pattern"""
    pattern_type: PatternType
    confidence: float  # 0-1
    evidence: List[str]  # Supporting evidence
    power_profile: Dict[int, float]  # Hour -> avg power (24 hours)
    recurrence_count: int  # How many times this pattern was observed
    first_observed: datetime
    last_observed: datetime


@dataclass
class Anomaly:
    """Detected anomaly in energy consumption"""
    device_id: str
    timestamp: datetime
    anomaly_type: AnomalyType
    current_power_w: float
    expected_power_w: float
    deviation_percent: float
    severity: str  # "low", "medium", "high", "critical"
    occupancy_status: str  # "occupied", "unoccupied", "unknown"
    explanation: str


class PatternAnalysisAgent:
    """
    Analyzes energy consumption patterns to identify waste.
    Maintains baselines and detects deviations.
    """
    
    def __init__(self):
        self.baselines: Dict[str, EnergyBaseline] = {}  # device_id -> baseline
        self.patterns: Dict[str, List[PatternSignature]] = {}  # device_id -> patterns
        self.anomalies: List[Anomaly] = []
    
    def establish_baseline(self, device_id: str, device_category: str, 
                          readings: pd.DataFrame, analysis_period_days: int = 30) -> EnergyBaseline:
        """
        Establish energy baseline from historical readings.
        
        Args:
            device_id: Device identifier
            device_category: Category of device
            readings: DataFrame with columns: timestamp, power_w, day_of_week
            analysis_period_days: Number of days to analyze for baseline
            
        Returns:
            EnergyBaseline object
        """
        # Filter to last N days
        if 'timestamp' in readings.columns:
            readings['timestamp'] = pd.to_datetime(readings['timestamp'])
            cutoff = datetime.now() - timedelta(days=analysis_period_days)
            readings = readings[readings['timestamp'] >= cutoff]
        
        # Calculate hourly baseline
        if 'hour' not in readings.columns and 'timestamp' in readings.columns:
            readings['hour'] = readings['timestamp'].dt.hour
        
        hourly_baseline = {}
        hourly_std = {}
        
        for hour in range(24):
            hour_data = readings[readings['hour'] == hour]['power_w'].values
            if len(hour_data) > 0:
                hourly_baseline[hour] = np.mean(hour_data)
                hourly_std[hour] = np.std(hour_data)
            else:
                hourly_baseline[hour] = 0
                hourly_std[hour] = 0
        
        # Calculate daily averages
        if 'day_of_week' in readings.columns:
            weekday_data = readings[readings['day_of_week'] < 5]['power_w'].values
            weekend_data = readings[readings['day_of_week'] >= 5]['power_w'].values
            
            weekday_avg = np.mean(weekday_data) if len(weekday_data) > 0 else 0
            weekend_avg = np.mean(weekend_data) if len(weekend_data) > 0 else 0
        else:
            weekday_avg = np.mean(readings['power_w'].values)
            weekend_avg = weekday_avg
        
        # Expected ranges (based on readings)
        all_powers = readings['power_w'].values
        max_power = np.percentile(all_powers, 95) if len(all_powers) > 0 else 0
        min_power = np.percentile(all_powers, 5) if len(all_powers) > 0 else 0
        
        baseline = EnergyBaseline(
            device_id=device_id,
            device_category=device_category,
            hourly_baseline=hourly_baseline,
            hourly_baseline_std=hourly_std,
            weekday_daily_avg_w=weekday_avg,
            weekend_daily_avg_w=weekend_avg,
            max_expected_power_w=max_power,
            min_expected_power_w=min_power,
            periods_analyzed=len(readings)
        )
        
        self.baselines[device_id] = baseline
        return baseline
    
    def detect_phantom_load(self, device_id: str, readings: pd.DataFrame, 
                           threshold_percent: float = 10.0) -> Optional[PatternSignature]:
        """
        Detect phantom loads (devices consuming power 24/7).
        
        A phantom load is detected when:
        - Device consumes power consistently across all hours
        - Consumption doesn't drop significantly during off-hours
        
        Args:
            device_id: Device identifier
            readings: DataFrame with readings
            threshold_percent: Max allowed variation (%)
            
        Returns:
            PatternSignature if phantom load detected, None otherwise
        """
        if device_id not in self.baselines:
            return None
        
        baseline = self.baselines[device_id]
        
        # Check if power consumption is consistent across hours
        hourly_values = [baseline.hourly_baseline.get(h, 0) for h in range(24)]
        hourly_mean = np.mean(hourly_values)
        hourly_std = np.std(hourly_values)
        
        # Low variation across hours = phantom load
        variation_percent = (hourly_std / (hourly_mean + 0.1)) * 100
        
        if variation_percent < threshold_percent and hourly_mean > 50:  # Minimum 50W to be meaningful
            evidence = [
                f"Consistent power draw across all 24 hours: {hourly_mean:.0f}W avg",
                f"Variation: {variation_percent:.1f}% (threshold: {threshold_percent}%)",
                "Power consumption doesn't decrease during off-hours"
            ]
            
            pattern = PatternSignature(
                pattern_type=PatternType.PHANTOM_LOAD,
                confidence=min(0.95, 1.0 - (variation_percent / threshold_percent) * 0.5),
                evidence=evidence,
                power_profile={h: baseline.hourly_baseline.get(h, 0) for h in range(24)},
                recurrence_count=1,
                first_observed=datetime.now(),
                last_observed=datetime.now()
            )
            
            return pattern
        
        return None
    
    def detect_post_occupancy_waste(self, device_id: str, readings: pd.DataFrame,
                                   occupancy_data: Dict[str, bool]) -> Optional[PatternSignature]:
        """
        Detect post-occupancy waste (devices left on after occupants leave).
        
        Args:
            device_id: Device identifier
            readings: DataFrame with readings
            occupancy_data: Dict mapping (day, hour) -> is_occupied
            
        Returns:
            PatternSignature if post-occupancy waste detected
        """
        if device_id not in self.baselines:
            return None
        
        baseline = self.baselines[device_id]
        
        # Compare power during occupied vs unoccupied hours
        occupied_hours = [h for h in range(24) if occupancy_data.get(f"0_{h}", False)]
        unoccupied_hours = [h for h in range(24) if not occupancy_data.get(f"0_{h}", False)]
        
        occupied_avg = np.mean([baseline.hourly_baseline.get(h, 0) for h in occupied_hours]) if occupied_hours else 0
        unoccupied_avg = np.mean([baseline.hourly_baseline.get(h, 0) for h in unoccupied_hours]) if unoccupied_hours else 0
        
        # If significant power during unoccupied hours = post-occupancy waste
        if unoccupied_avg > occupied_avg * 0.3:  # At least 30% of occupied power
            evidence = [
                f"Power during occupied hours: {occupied_avg:.0f}W",
                f"Power during unoccupied hours: {unoccupied_avg:.0f}W",
                f"Ratio: {(unoccupied_avg/occupied_avg if occupied_avg > 0 else 0)*100:.0f}%",
                "Device is consuming power when building is unoccupied"
            ]
            
            pattern = PatternSignature(
                pattern_type=PatternType.POST_OCCUPANCY,
                confidence=min(0.90, (unoccupied_avg / (occupied_avg + 0.1)) * 0.5),
                evidence=evidence,
                power_profile={h: baseline.hourly_baseline.get(h, 0) for h in range(24)},
                recurrence_count=1,
                first_observed=datetime.now(),
                last_observed=datetime.now()
            )
            
            return pattern
        
        return None
    
    def detect_anomalies(self, device_id: str, current_power_w: float, 
                        current_hour: int, current_occupancy: str, 
                        season: str = "spring") -> List[Anomaly]:
        """
        Detect anomalies in current power reading compared to baseline.
        
        Args:
            device_id: Device identifier
            current_power_w: Current power reading in watts
            current_hour: Hour of day (0-23)
            current_occupancy: 'occupied', 'unoccupied', or 'unknown'
            season: Current season for seasonal adjustment
            
        Returns:
            List of detected anomalies
        """
        anomalies_detected = []
        
        if device_id not in self.baselines:
            return anomalies_detected
        
        baseline = self.baselines[device_id]
        expected_power = baseline.hourly_baseline.get(current_hour, 0)
        
        # Apply seasonal adjustment
        seasonal_factor = baseline.seasonal_multiplier.get(season, 1.0)
        expected_power *= seasonal_factor
        
        # Calculate deviation
        if expected_power > 0:
            deviation_percent = ((current_power_w - expected_power) / expected_power) * 100
        else:
            deviation_percent = 0 if current_power_w == 0 else 100
        
        # Determine severity
        if abs(deviation_percent) > 100:
            severity = "critical"
            anomaly_type = AnomalyType.UNEXPECTED_PEAK if current_power_w > expected_power else AnomalyType.BELOW_BASELINE
        elif abs(deviation_percent) > 50:
            severity = "high"
            anomaly_type = AnomalyType.ABOVE_BASELINE if current_power_w > expected_power else AnomalyType.BELOW_BASELINE
        elif abs(deviation_percent) > 25:
            severity = "medium"
            anomaly_type = AnomalyType.ABOVE_BASELINE if current_power_w > expected_power else AnomalyType.BELOW_BASELINE
        else:
            severity = "low"
            anomaly_type = AnomalyType.ABOVE_BASELINE if current_power_w > expected_power else AnomalyType.BELOW_BASELINE
        
        # Additional context-based anomalies
        if current_occupancy == "unoccupied" and current_power_w > baseline.min_expected_power_w * 1.5:
            anomaly_type = AnomalyType.NIGHT_CONSUMPTION if current_hour >= 22 or current_hour <= 6 else anomaly_type
        
        if severity in ["high", "critical"]:
            anomaly = Anomaly(
                device_id=device_id,
                timestamp=datetime.now(),
                anomaly_type=anomaly_type,
                current_power_w=current_power_w,
                expected_power_w=expected_power,
                deviation_percent=deviation_percent,
                severity=severity,
                occupancy_status=current_occupancy,
                explanation=f"Power {deviation_percent:+.0f}% from baseline ({current_power_w:.0f}W vs {expected_power:.0f}W expected)"
            )
            anomalies_detected.append(anomaly)
        
        return anomalies_detected
    
    def get_baseline_comparison(self, device_id: str, current_period_readings: pd.DataFrame) -> Dict:
        """
        Compare current readings with established baseline.
        
        Args:
            device_id: Device identifier
            current_period_readings: Recent readings
            
        Returns:
            Comparison summary
        """
        if device_id not in self.baselines:
            return {}
        
        baseline = self.baselines[device_id]
        
        current_avg = current_period_readings['power_w'].mean() if len(current_period_readings) > 0 else 0
        baseline_avg = np.mean(list(baseline.hourly_baseline.values()))
        
        comparison = {
            'device_id': device_id,
            'current_avg_power_w': round(current_avg, 2),
            'baseline_avg_power_w': round(baseline_avg, 2),
            'variance_percent': round(((current_avg - baseline_avg) / (baseline_avg + 0.1)) * 100, 2),
            'baseline_periods': baseline.periods_analyzed,
            'baseline_last_updated': baseline.last_updated.isoformat()
        }
        
        return comparison
