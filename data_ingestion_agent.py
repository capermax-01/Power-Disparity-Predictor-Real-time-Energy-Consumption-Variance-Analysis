"""
Data Ingestion Agent
Handles smart meter data upload, validation, normalization, and storage.
Converts raw meter readings into standardized format for pattern analysis.

RESPONSIBILITIES:
1. Parse CSV/API data from smart meters
2. Validate data quality (missing values, outliers, data types)
3. Normalize power readings (convert kW to W, handle different intervals)
4. Handle occupancy data (schedules, badge logs, sensor data)
5. Store time-series data for pattern analysis
6. Detect and flag data anomalies
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import pandas as pd
import numpy as np
import json
from pathlib import Path


class DataSourceType(str, Enum):
    """Types of data sources"""
    SMART_METER = "smart_meter"
    SUB_METER = "sub_meter"
    IOT_SENSOR = "iot_sensor"
    SCADA_BMS = "scada_bms"
    API_STREAM = "api_stream"
    CSV_UPLOAD = "csv_upload"


class DataQualityIssue(str, Enum):
    """Types of data quality issues"""
    MISSING_VALUE = "missing_value"
    OUTLIER = "outlier"
    DUPLICATE = "duplicate"
    INVALID_TIMESTAMP = "invalid_timestamp"
    INVALID_POWER = "invalid_power"
    INCOMPLETE_RECORD = "incomplete_record"


@dataclass
class MeterReading:
    """Single meter reading from a device"""
    timestamp: datetime
    device_id: str
    device_category: str
    location_floor: Optional[str] = None
    location_zone: Optional[str] = None
    power_w: float = 0.0  # Always in Watts
    energy_kwh: Optional[float] = None  # Cumulative energy
    temperature_c: Optional[float] = None
    humidity_percent: Optional[float] = None
    occupancy_status: Optional[str] = None  # "occupied", "unoccupied", "unknown"
    occupancy_confidence: float = 0.5
    data_source: DataSourceType = DataSourceType.CSV_UPLOAD
    validity: bool = True
    quality_flags: List[DataQualityIssue] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'device_id': self.device_id,
            'device_category': self.device_category,
            'location_floor': self.location_floor,
            'location_zone': self.location_zone,
            'power_w': round(self.power_w, 2),
            'energy_kwh': round(self.energy_kwh, 4) if self.energy_kwh else None,
            'temperature_c': round(self.temperature_c, 2) if self.temperature_c else None,
            'humidity_percent': round(self.humidity_percent, 2) if self.humidity_percent else None,
            'occupancy_status': self.occupancy_status,
            'occupancy_confidence': round(self.occupancy_confidence, 2),
            'data_source': self.data_source.value,
            'valid': self.validity,
            'quality_issues': [flag.value for flag in self.quality_flags]
        }


@dataclass
class DataIngestionResult:
    """Result of data ingestion"""
    total_records: int
    valid_records: int
    invalid_records: int
    readings: List[MeterReading]
    quality_summary: Dict[str, int]  # Count of each issue type
    data_gaps: List[Tuple[datetime, datetime]]  # Time ranges with missing data
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'total_records': self.total_records,
            'valid_records': self.valid_records,
            'invalid_records': self.invalid_records,
            'validity_percent': round(self.valid_records / self.total_records * 100, 2) if self.total_records > 0 else 0,
            'quality_passes': sum(1 for flag in self.quality_summary.values() if flag == 0),
            'quality_issues': self.quality_summary,
            'data_gaps': [(start.isoformat(), end.isoformat()) for start, end in self.data_gaps],
            'ingestion_timestamp': self.timestamp.isoformat()
        }


class DataIngestionAgent:
    """
    Handles data ingestion from various sources.
    Validates, normalizes, and prepares data for pattern analysis.
    """
    
    def __init__(self, max_power_w: float = 50000.0, min_power_w: float = 0.0):
        """
        Initialize data ingestion agent.
        
        Args:
            max_power_w: Maximum reasonable power reading (W)
            min_power_w: Minimum reasonable power reading (W)
        """
        self.max_power_w = max_power_w
        self.min_power_w = min_power_w
        self.readings: Dict[str, List[MeterReading]] = {}  # device_id -> readings
    
    def ingest_csv(self, csv_path: str, source_type: DataSourceType = DataSourceType.CSV_UPLOAD) -> DataIngestionResult:
        """
        Ingest data from CSV file.
        Expected columns: timestamp, device_id/appliance_id, device_category/appliance_category, power_w/power_reading, occupancy_status, 
                         location_floor (optional), location_zone (optional)
        
        Args:
            csv_path: Path to CSV file
            source_type: Type of data source
            
        Returns:
            DataIngestionResult with ingestion summary and readings
        """
        try:
            # Read CSV
            df = pd.read_csv(csv_path)
            
            # Map column names (support multiple naming conventions)
            column_mapping = {
                'timestamp': 'timestamp',
                'device_id': ['device_id', 'appliance_id'],
                'device_category': ['device_category', 'appliance_category'],
                'power_w': ['power_w', 'power_reading'],
            }
            
            # Create standardized column names
            standardized_df = df.copy()
            for target_col, possible_cols in column_mapping.items():
                if target_col == 'timestamp':
                    if 'timestamp' not in standardized_df.columns:
                        raise ValueError("Missing required column: timestamp")
                else:
                    found = False
                    for possible_col in possible_cols:
                        if possible_col in standardized_df.columns:
                            standardized_df = standardized_df.rename(columns={possible_col: target_col})
                            found = True
                            break
                    if not found:
                        raise ValueError(f"Missing required column (tried: {possible_cols})")
            
            df = standardized_df
            
            readings = []
            quality_issues: Dict[str, int] = {issue.value: 0 for issue in DataQualityIssue}
            
            for idx, row in df.iterrows():
                record_issues: List[DataQualityIssue] = []  # Track issues for this record
                try:
                    # Parse timestamp
                    try:
                        timestamp = pd.to_datetime(row['timestamp'])
                    except:
                        quality_issues[DataQualityIssue.INVALID_TIMESTAMP.value] += 1
                        record_issues.append(DataQualityIssue.INVALID_TIMESTAMP)
                        continue
                    
                    # Extract basic fields
                    device_id = str(row['device_id']).strip()
                    device_category = str(row['device_category']).strip()
                    
                    # Validate and normalize power reading
                    try:
                        power_w = float(row['power_w'])
                        if power_w < self.min_power_w or power_w > self.max_power_w:
                            quality_issues[DataQualityIssue.OUTLIER.value] += 1
                            record_issues.append(DataQualityIssue.OUTLIER)
                            power_w = np.clip(power_w, self.min_power_w, self.max_power_w)
                    except:
                        quality_issues[DataQualityIssue.INVALID_POWER.value] += 1
                        record_issues.append(DataQualityIssue.INVALID_POWER)
                        continue
                    
                    # Extract optional fields
                    location_floor = str(row.get('location_floor', '')).strip() or None
                    location_zone = str(row.get('location_zone', '')).strip() or None
                    occupancy_status = str(row.get('occupancy_status', 'unknown')).strip().lower()
                    occupancy_confidence = float(row.get('occupancy_confidence', 0.5))
                    energy_kwh = float(row.get('energy_kwh', 0)) if 'energy_kwh' in row and row.get('energy_kwh') else None
                    
                    # Validate occupancy status
                    if occupancy_status not in ['occupied', 'unoccupied', 'unknown']:
                        occupancy_status = 'unknown'
                    
                    occupancy_confidence = np.clip(occupancy_confidence, 0, 1)
                    
                    # Create reading - validity is true if no issues detected
                    reading = MeterReading(
                        timestamp=timestamp,
                        device_id=device_id,
                        device_category=device_category,
                        location_floor=location_floor,
                        location_zone=location_zone,
                        power_w=power_w,
                        energy_kwh=energy_kwh,
                        occupancy_status=occupancy_status,
                        occupancy_confidence=occupancy_confidence,
                        data_source=source_type,
                        validity=len(record_issues) == 0,
                        quality_flags=record_issues
                    )
                    
                    readings.append(reading)
                    
                except Exception as e:
                    quality_issues[DataQualityIssue.INCOMPLETE_RECORD.value] += 1
                    continue
            
            # Detect data gaps
            data_gaps = self._detect_data_gaps(readings)
            
            # Store readings
            for reading in readings:
                if reading.device_id not in self.readings:
                    self.readings[reading.device_id] = []
                self.readings[reading.device_id].append(reading)
            
            valid_count = sum(1 for r in readings if r.validity)
            
            return DataIngestionResult(
                total_records=len(df),
                valid_records=valid_count,
                invalid_records=len(df) - valid_count,
                readings=readings,
                quality_summary=quality_issues,
                data_gaps=data_gaps
            )
            
        except Exception as e:
            raise Exception(f"CSV ingestion error: {str(e)}")
    
    def ingest_json_array(self, json_data: List[Dict], source_type: DataSourceType = DataSourceType.API_STREAM) -> DataIngestionResult:
        """
        Ingest data from JSON array (from API).
        
        Args:
            json_data: List of reading dictionaries
            source_type: Type of data source
            
        Returns:
            DataIngestionResult
        """
        # Convert to DataFrame and use CSV ingestion logic
        df = pd.DataFrame(json_data)
        
        # Temporary CSV save and load
        temp_path = Path("/tmp/temp_json_ingest.csv")
        df.to_csv(temp_path, index=False)
        
        result = self.ingest_csv(str(temp_path), source_type=source_type)
        temp_path.unlink()  # Clean up temp file
        
        return result
    
    def normalize_occupancy_schedule(self, building_schedule: Dict) -> Dict[str, bool]:
        """
        Normalize occupancy schedule to hourly boolean values.
        
        Args:
            building_schedule: Dict with keys like "monday", "weekend", etc.
                              Values are lists of occupied hours
        
        Returns:
            Dictionary mapping (day, hour) -> is_occupied
        """
        occupancy_map = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day_idx, day_name in enumerate(days):
            occupied_hours = building_schedule.get(day_name, [])
            
            for hour in range(24):
                key = f"{day_idx}_{hour}"
                occupancy_map[key] = hour in occupied_hours
        
        return occupancy_map
    
    def _detect_data_gaps(self, readings: List[MeterReading], expected_interval_minutes: int = 60) -> List[Tuple[datetime, datetime]]:
        """
        Detect gaps in time-series data.
        Assumes readings should be at regular intervals.
        
        Args:
            readings: List of readings sorted by timestamp
            expected_interval_minutes: Expected interval between readings
            
        Returns:
            List of (start, end) tuples for data gaps
        """
        if len(readings) < 2:
            return []
        
        # Sort by timestamp
        sorted_readings = sorted(readings, key=lambda r: r.timestamp)
        
        gaps = []
        expected_delta = timedelta(minutes=expected_interval_minutes)
        
        for i in range(1, len(sorted_readings)):
            prev_time = sorted_readings[i-1].timestamp
            curr_time = sorted_readings[i].timestamp
            actual_delta = curr_time - prev_time
            
            if actual_delta > expected_delta * 1.5:  # Allow 50% tolerance
                gaps.append((prev_time, curr_time))
        
        return gaps
    
    def get_readings_for_device(self, device_id: str) -> List[MeterReading]:
        """Get all readings for a specific device"""
        return self.readings.get(device_id, [])
    
    def get_readings_in_timerange(self, device_id: str, start: datetime, end: datetime) -> List[MeterReading]:
        """Get readings for a device in a specific time range"""
        device_readings = self.get_readings_for_device(device_id)
        return [r for r in device_readings if start <= r.timestamp <= end]
    
    def get_summary_by_location(self) -> Dict[str, Dict]:
        """Get summary of readings by building location"""
        summary = {}
        
        for device_id, readings in self.readings.items():
            if not readings:
                continue
            
            # Use first reading for location info
            first_reading = readings[0]
            location_key = f"{first_reading.location_floor or 'Unknown'} - {first_reading.location_zone or 'All Zones'}"
            
            if location_key not in summary:
                summary[location_key] = {
                    'devices': [],
                    'reading_count': 0,
                    'avg_power_w': 0,
                    'max_power_w': 0
                }
            
            summary[location_key]['devices'].append(device_id)
            summary[location_key]['reading_count'] += len(readings)
            powers = [r.power_w for r in readings]
            summary[location_key]['avg_power_w'] = np.mean(powers)
            summary[location_key]['max_power_w'] = np.max(powers)
        
        return summary
