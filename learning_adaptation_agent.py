"""
Learning & Adaptation Agent
Learns from historical data and adapts thresholds over time.
Improves accuracy by understanding building-specific patterns and seasonal variations.

RESPONSIBILITIES:
1. Learn seasonal consumption trends (winter vs summer different HVAC use)
2. Identify occupancy patterns (shift patterns, peak hours)
3. Adapt anomaly detection thresholds based on building behavior
4. Track false positive/negative rates and improve over time
5. Reduce alert fatigue through intelligent filtering
6. Predict expected consumption based on external factors (weather, day type)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict


class DayType(str, Enum):
    """Types of days with different consumption patterns"""
    NORMAL_WEEKDAY = "normal_weekday"
    NORMAL_WEEKEND = "normal_weekend"
    HOLIDAY = "holiday"
    SPECIAL_EVENT = "special_event"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"


class WeatherImpact(str, Enum):
    """Impact of weather on energy consumption"""
    COLD_NO_HVAC = "cold_no_hvac"  # Heating should be on
    COLD_HVAC_OFF = "cold_hvac_off"  # Anomalous - heating missing
    HOT_NO_HVAC = "hot_no_hvac"  # Cooling should be on
    HOT_HVAC_OFF = "hot_hvac_off"  # Anomalous - cooling missing
    MILD = "mild"  # No major HVAC impact


@dataclass
class SeasonalProfile:
    """Consumption profile for a specific season"""
    season: str  # 'winter', 'spring', 'summer', 'fall'
    hvac_multiplier: float  # Heating/cooling energy multiplier
    baseline_adjustment: float  # Overall consumption adjustment
    avg_daily_consumption_kwh: float
    peak_hours: List[int]  # Peak consumption hours
    off_peak_hours: List[int]  # Minimal consumption hours
    confidence: float  # How confident we are in this profile


@dataclass
class OccupancyPattern:
    """Detected occupancy pattern of building"""
    name: str  # "9-5 office", "24/7 facility", etc.
    occupied_hours_weekday: List[int]  # Hours when occupied on weekdays
    occupied_hours_weekend: List[int]  # Hours when occupied on weekends
    peak_occupancy_hours: List[int]  # When most people present
    confidence: float


@dataclass
class AdaptationMetrics:
    """Metrics tracking learning progress"""
    total_alerts_generated: int = 0
    validated_true_positives: int = 0  # User confirmed waste
    validated_false_positives: int = 0  # User said "no waste here"
    validated_false_negatives: int = 0  # Waste user detected that system missed
    
    current_precision: float = 0.8  # TP / (TP + FP)
    current_recall: float = 0.7  # TP / (TP + FN)
    
    @property
    def f1_score(self) -> float:
        """F1 score balancing precision and recall"""
        if self.current_precision + self.current_recall == 0:
            return 0
        return 2 * (self.current_precision * self.current_recall) / (self.current_precision + self.current_recall)


@dataclass
class ThresholdProfile:
    """Adaptive threshold for anomaly detection"""
    device_id: str
    device_category: str
    
    # Deviation thresholds for different times
    peak_hour_threshold_percent: float = 50.0  # +/- 50% during peak
    off_peak_threshold_percent: float = 25.0   # +/- 25% during off-peak
    night_threshold_percent: float = 15.0      # +/- 15% at night
    
    # Seasonal adjustments
    seasonal_thresholds: Dict[str, float] = field(default_factory=dict)
    
    # Alert frequency dampening
    min_hours_between_alerts: int = 24  # Don't alert more than once per day per device
    min_deviation_for_alert: float = 50.0  # Watts - ignore very small anomalies
    
    last_updated: datetime = field(default_factory=datetime.now)
    last_alert_time: Optional[datetime] = None


class LearningAdaptationAgent:
    """
    Learns from building-specific patterns and adapts detection parameters.
    Reduces false positives and improves accuracy over time.
    """
    
    def __init__(self, building_id: str):
        self.building_id = building_id
        
        # Learned profiles
        self.seasonal_profiles: Dict[str, SeasonalProfile] = {}
        self.occupancy_patterns: Dict[str, OccupancyPattern] = {}
        self.threshold_profiles: Dict[str, ThresholdProfile] = {}
        
        # Adaptation metrics
        self.metrics: AdaptationMetrics = AdaptationMetrics()
        
        # Historical feedback (user confirmations)
        self.feedback_history: List[Dict] = []
        
        # Day type calendar
        self.day_type_calendar: Dict[datetime.date, DayType] = {}
    
    def learn_seasonal_pattern(self, device_id: str, device_category: str,
                              readings_by_season: Dict[str, pd.DataFrame]) -> Dict[str, SeasonalProfile]:
        """
        Learn seasonal consumption patterns.
        
        Args:
            device_id: Device identifier
            device_category: Category of device
            readings_by_season: Dict with keys 'winter', 'spring', 'summer', 'fall'
                               Each contains DataFrame with power_w and hour columns
        
        Returns:
            Dictionary of SeasonalProfile objects
        """
        seasonal_profiles = {}
        
        for season, readings in readings_by_season.items():
            if readings.empty:
                continue
            
            # Calculate metrics
            total_kwh = readings['power_w'].sum() / 1000 / len(readings)  # Approximate daily
            avg_power = readings['power_w'].mean()
            
            # Find peak and off-peak hours
            if 'hour' in readings.columns:
                hourly_avg = readings.groupby('hour')['power_w'].mean()
                peak_threshold = hourly_avg.quantile(0.75)
                off_peak_threshold = hourly_avg.quantile(0.25)
                
                peak_hours = hourly_avg[hourly_avg >= peak_threshold].index.tolist()
                off_peak_hours = hourly_avg[hourly_avg <= off_peak_threshold].index.tolist()
            else:
                peak_hours = [9, 10, 11, 14, 15, 16]  # Default office hours
                off_peak_hours = [0, 1, 2, 3, 4, 5]  # Default night hours
            
            # Seasonal adjustments
            hvac_multiplier = {
                'winter': 1.3,
                'spring': 0.9,
                'summer': 1.4,
                'fall': 0.95
            }.get(season, 1.0)
            
            profile = SeasonalProfile(
                season=season,
                hvac_multiplier=hvac_multiplier,
                baseline_adjustment=avg_power / 1000,  # kW
                avg_daily_consumption_kwh=total_kwh,
                peak_hours=peak_hours,
                off_peak_hours=off_peak_hours,
                confidence=0.8
            )
            
            seasonal_profiles[season] = profile
        
        self.seasonal_profiles.update(seasonal_profiles)
        return seasonal_profiles
    
    def learn_occupancy_pattern(self, building_readings: pd.DataFrame,
                               occupancy_data: pd.DataFrame) -> OccupancyPattern:
        """
        Learn building occupancy pattern from data.
        
        Args:
            building_readings: All building power readings
            occupancy_data: Occupancy sensor data with timestamp and occupancy_status
            
        Returns:
            OccupancyPattern object
        """
        # Correlate power consumption with occupancy
        if 'hour' not in building_readings.columns:
            building_readings['hour'] = pd.to_datetime(building_readings.get('timestamp')).dt.hour
        
        if 'day_of_week' not in building_readings.columns:
            building_readings['day_of_week'] = pd.to_datetime(building_readings.get('timestamp')).dt.dayofweek
        
        # Identify occupied hours (when consumption spikes with people)
        weekday_data = building_readings[building_readings['day_of_week'] < 5]
        weekend_data = building_readings[building_readings['day_of_week'] >= 5]
        
        def find_occupied_hours(data: pd.DataFrame) -> List[int]:
            if data.empty:
                return list(range(8, 18))  # Default office hours
            
            hourly_avg = data.groupby('hour')['power_w'].mean()
            threshold = hourly_avg.quantile(0.5)  # Median is occupied threshold
            return hourly_avg[hourly_avg >= threshold].index.tolist()
        
        occupied_weekday = find_occupied_hours(weekday_data)
        occupied_weekend = find_occupied_hours(weekend_data)
        
        # Peak hours are busiest within occupied time
        peak_hours = occupied_weekday[len(occupied_weekday)//3:2*len(occupied_weekday)//3] or occupied_weekday
        
        pattern = OccupancyPattern(
            name=self._infer_building_type(occupied_weekday, occupied_weekend),
            occupied_hours_weekday=occupied_weekday,
            occupied_hours_weekend=occupied_weekend,
            peak_occupancy_hours=peak_hours,
            confidence=0.85
        )
        
        self.occupancy_patterns['building'] = pattern
        return pattern
    
    def _infer_building_type(self, weekday_hours: List[int], weekend_hours: List[int]) -> str:
        """Infer building type from occupancy pattern"""
        weekday_count = len(weekday_hours)
        weekend_count = len(weekend_hours)
        
        if weekday_count >= 12 and weekend_count >= 8:
            return "24/7 Facility"
        elif weekday_count >= 8 and weekend_count <= 2:
            return "Office (9-5)"
        elif weekday_count >= 10 and weekend_count >= 6:
            return "Retail/Commercial"
        else:
            return "Variable Pattern"
    
    def create_adaptive_threshold(self, device_id: str, device_category: str) -> ThresholdProfile:
        """
        Create device-specific threshold profile that adapts based on building behavior.
        
        Args:
            device_id: Device identifier
            device_category: Category of device
            
        Returns:
            ThresholdProfile configured for this device
        """
        # Base thresholds by device category
        base_thresholds = {
            'hvac': {'peak': 60, 'off_peak': 30, 'night': 20},
            'lighting': {'peak': 70, 'off_peak': 40, 'night': 10},
            'kitchen': {'peak': 50, 'off_peak': 25, 'night': 15},
            'office': {'peak': 45, 'off_peak': 20, 'night': 10},
            'default': {'peak': 50, 'off_peak': 25, 'night': 15}
        }
        
        thresholds = base_thresholds.get(device_category.lower(), base_thresholds['default'])
        
        profile = ThresholdProfile(
            device_id=device_id,
            device_category=device_category,
            peak_hour_threshold_percent=thresholds['peak'],
            off_peak_threshold_percent=thresholds['off_peak'],
            night_threshold_percent=thresholds['night']
        )
        
        self.threshold_profiles[device_id] = profile
        return profile
    
    def adapt_thresholds(self, device_id: str, feedback: Dict) -> None:
        """
        Adapt thresholds based on user feedback.
        
        Args:
            device_id: Device identifier
            feedback: {'is_valid': bool, 'severity': 'true_positive'|'false_positive'|'false_negative', ...}
        """
        self.feedback_history.append({
            'device_id': device_id,
            'timestamp': datetime.now(),
            **feedback
        })
        
        # Update metrics
        if feedback.get('severity') == 'true_positive':
            self.metrics.validated_true_positives += 1
        elif feedback.get('severity') == 'false_positive':
            self.metrics.validated_false_positives += 1
        elif feedback.get('severity') == 'false_negative':
            self.metrics.validated_false_negatives += 1
        
        # Recalculate precision/recall
        total_positives = self.metrics.validated_true_positives + self.metrics.validated_false_positives
        if total_positives > 0:
            self.metrics.current_precision = self.metrics.validated_true_positives / total_positives
        
        total_actual = self.metrics.validated_true_positives + self.metrics.validated_false_negatives
        if total_actual > 0:
            self.metrics.current_recall = self.metrics.validated_true_positives / total_actual
        
        # Adapt thresholds if precision too low (too many false positives)
        if device_id in self.threshold_profiles and self.metrics.current_precision < 0.6:
            profile = self.threshold_profiles[device_id]
            # Increase thresholds to be more conservative
            profile.peak_hour_threshold_percent *= 1.1
            profile.off_peak_threshold_percent *= 1.1
            profile.last_updated = datetime.now()
    
    def should_alert(self, device_id: str, severity: str) -> bool:
        """
        Determine if alert should be issued based on adaptive rules.
        Prevents alert fatigue.
        
        Args:
            device_id: Device identifier
            severity: Alert severity level
            
        Returns:
            True if alert should be issued
        """
        if device_id not in self.threshold_profiles:
            return True
        
        profile = self.threshold_profiles[device_id]
        now = datetime.now()
        
        # Respect minimum time between alerts
        if profile.last_alert_time:
            hours_since_last = (now - profile.last_alert_time).total_seconds() / 3600
            if hours_since_last < profile.min_hours_between_alerts:
                return False
        
        # Only alert if F1 score is good enough
        if self.metrics.f1_score < 0.5:
            return False
        
        # Higher severity overrides dampening
        if severity == 'critical':
            return True
        
        return True
    
    def predict_expected_consumption(self, device_id: str, device_category: str,
                                    target_datetime: datetime,
                                    weather_temp_c: Optional[float] = None) -> float:
        """
        Predict expected power consumption for a future time.
        
        Args:
            device_id: Device identifier
            device_category: Device category (e.g., 'hvac', 'lighting')
            target_datetime: Target date/time for prediction
            weather_temp_c: Current outdoor temperature for HVAC prediction
            
        Returns:
            Predicted power in watts
        """
        # Get season
        month = target_datetime.month
        season = {
            12: 'winter', 1: 'winter', 2: 'winter',
            3: 'spring', 4: 'spring', 5: 'spring',
            6: 'summer', 7: 'summer', 8: 'summer',
            9: 'fall', 10: 'fall', 11: 'fall'
        }[month]
        
        # Get seasonal profile if available
        if season in self.seasonal_profiles:
            profile = self.seasonal_profiles[season]
            base_power = profile.baseline_adjustment * 1000  # Convert back to W
            
            # Adjust if HVAC and weather is extreme
            if device_category.lower() == 'hvac' and weather_temp_c:
                if weather_temp_c < 5:
                    return base_power * 1.4
                elif weather_temp_c > 30:
                    return base_power * 1.5
            
            return base_power
        
        # Fallback: return reasonable default
        defaults = {
            'hvac': 2000,
            'lighting': 1000,
            'kitchen': 1500,
            'office': 500
        }
        
        return defaults.get(device_category.lower(), 1000)
    
    def get_learning_summary(self) -> Dict:
        """Get summary of learning progress"""
        return {
            'building_id': self.building_id,
            'seasonal_profiles_learned': len(self.seasonal_profiles),
            'occupancy_patterns': list(self.occupancy_patterns.keys()),
            'adaptive_thresholds': len(self.threshold_profiles),
            'total_feedback': len(self.feedback_history),
            'metrics': {
                'total_alerts': self.metrics.total_alerts_generated,
                'true_positives': self.metrics.validated_true_positives,
                'false_positives': self.metrics.validated_false_positives,
                'false_negatives': self.metrics.validated_false_negatives,
                'precision': round(self.metrics.current_precision, 3),
                'recall': round(self.metrics.current_recall, 3),
                'f1_score': round(self.metrics.f1_score, 3)
            }
        }
