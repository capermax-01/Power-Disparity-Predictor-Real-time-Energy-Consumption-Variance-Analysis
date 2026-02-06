"""
Energy Waste Detection & Reasoning Engine
Detects 5 waste patterns and generates actionable insights
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta

COST_PER_KWH_INR = 8.5  # Indian commercial rate


@dataclass
class WasteAlert:
    """Represents a detected waste pattern"""
    waste_type: str  # 'phantom_load', 'post_occupancy', 'seasonal_mismatch', 'night_violation', 'maintenance_dump'
    zone_id: str
    device_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    
    # Timing
    first_detected: datetime
    last_detected: datetime
    duration_hours: float
    
    # Energy & Cost
    waste_power_kw: float
    waste_energy_kwh: float
    daily_cost_inr: float
    monthly_cost_inr: float
    annual_cost_inr: float
    
    # Reasoning
    reason: str
    confidence: float  # 0.0 to 1.0
    
    # Actions
    recommended_actions: List[Dict]  # Each action has 'priority', 'description', 'estimated_cost_inr', 'payback_days'
    
    building_id: str = "BLDG01"
    floor_number: int = 0
    area_sqft: float = 0.0


class EnergyWasteDetector:
    """Detects energy waste patterns using occupancy data"""
    
    def __init__(self, cost_per_kwh: float = COST_PER_KWH_INR):
        self.cost_per_kwh = cost_per_kwh
        self.waste_alerts: List[WasteAlert] = []
    
    def detect_phantom_loads(self, df: pd.DataFrame) -> List[WasteAlert]:
        """
        Phantom Load: Device ON when zone is unoccupied (especially at night)
        
        Typical Case:
        - SERVER_1 uses 3.8 kW continuously
        - Zone unoccupied (occupancy_status='Unoccupied')
        - Happens 24/7 or especially 10 PM - 6 AM
        - Cost: 3.8kW × 24h × ₹8.5 = ₹774.20/day
        """
        alerts = []
        
        # Group by device
        for (zone_id, device_type), group in df.groupby(['zone_id', 'device_type']):
            # Filter for unoccupied periods
            unoccupied = group[group['occupancy_status'] == 'Unoccupied'].copy()
            
            if len(unoccupied) == 0:
                continue
            
            # Check if device is ON during unoccupied hours
            device_on_unoccupied = unoccupied[unoccupied['device_state'] == 'ON'].copy()
            
            if len(device_on_unoccupied) == 0:
                continue
            
            # Calculate continuous usage periods
            device_on_unoccupied = device_on_unoccupied.sort_values('timestamp')
            
            # If >6 consecutive hours of unoccupied + on = phantom load
            consecutive_hours = len(device_on_unoccupied)
            
            if consecutive_hours >= 6:
                avg_power_kw = device_on_unoccupied['power_kw'].mean()
                max_power_kw = device_on_unoccupied['power_kw'].max()
                waste_energy_kwh = avg_power_kw * consecutive_hours
                
                # Cost calculation
                daily_cost = waste_energy_kwh / consecutive_hours * 24 * self.cost_per_kwh
                monthly_cost = daily_cost * 30
                annual_cost = daily_cost * 365
                
                # Severity based on cost
                if annual_cost > 100000:
                    severity = 'critical'
                    confidence = 0.98
                elif annual_cost > 50000:
                    severity = 'high'
                    confidence = 0.95
                elif annual_cost > 20000:
                    severity = 'medium'
                    confidence = 0.90
                else:
                    severity = 'low'
                    confidence = 0.85
                
                # Recommendations
                actions = self._recommend_actions_phantom_load(
                    device_type, avg_power_kw, annual_cost
                )
                
                alert = WasteAlert(
                    waste_type='phantom_load',
                    zone_id=zone_id,
                    device_type=device_type,
                    severity=severity,
                    first_detected=device_on_unoccupied['timestamp'].min(),
                    last_detected=device_on_unoccupied['timestamp'].max(),
                    duration_hours=consecutive_hours,
                    waste_power_kw=avg_power_kw,
                    waste_energy_kwh=waste_energy_kwh,
                    daily_cost_inr=daily_cost,
                    monthly_cost_inr=monthly_cost,
                    annual_cost_inr=annual_cost,
                    reason=(f"Device {device_type} in {zone_id} is ON for {consecutive_hours}h "
                           f"while zone unoccupied. Operating 24/7 when no one present."),
                    confidence=confidence,
                    recommended_actions=actions,
                    building_id=group['building_id'].iloc[0] if 'building_id' in group.columns else "BLDG01",
                    floor_number=group['floor_number'].iloc[0] if 'floor_number' in group.columns else 0,
                    area_sqft=group['area_sqft'].iloc[0] if 'area_sqft' in group.columns else 0
                )
                
                alerts.append(alert)
        
        return alerts
    
    def detect_post_occupancy_waste(self, df: pd.DataFrame) -> List[WasteAlert]:
        """
        Post-Occupancy Waste: Equipment continues running 15+ minutes after occupancy ends
        
        Example:
        - 6 PM: Zone switches from Occupied to Unoccupied
        - Equipment (Light, AC) still ON
        - 20 minutes later, still running
        - Should auto-shutoff when zone becomes unoccupied
        """
        alerts = []
        
        for (zone_id, device_type), group in df.groupby(['zone_id', 'device_type']):
            group = group.sort_values('timestamp').reset_index(drop=True)
            
            if len(group) < 2:
                continue
            
            # Detect occupancy changes
            group['occupancy_changed'] = group['occupancy_status'].ne(group['occupancy_status'].shift())
            
            # Find transitions from Occupied → Unoccupied
            transitions = group[
                (group['occupancy_status'] == 'Unoccupied') & 
                (group['occupancy_changed'] == True)
            ].index.tolist()
            
            for idx in transitions:
                if idx >= len(group) - 5:  # Not enough future data
                    continue
                
                # Check if device stayed ON after occupancy ended
                post_occupancy = group.iloc[idx:idx+5]  # Next 5 hours
                device_on_after = post_occupancy[post_occupancy['device_state'] == 'ON']
                
                if len(device_on_after) >= 2:  # Running for 2+ hours after occupancy ends
                    hours_running = len(device_on_after)
                    avg_power_kw = device_on_after['power_kw'].mean()
                    waste_energy_kwh = avg_power_kw * hours_running
                    
                    daily_cost = waste_energy_kwh * self.cost_per_kwh
                    monthly_cost = daily_cost * 30
                    annual_cost = daily_cost * 365
                    
                    severity = 'high' if hours_running > 4 else 'medium'
                    
                    actions = self._recommend_actions_post_occupancy(
                        device_type, hours_running, annual_cost
                    )
                    
                    alert = WasteAlert(
                        waste_type='post_occupancy',
                        zone_id=zone_id,
                        device_type=device_type,
                        severity=severity,
                        first_detected=post_occupancy['timestamp'].iloc[0],
                        last_detected=post_occupancy['timestamp'].iloc[-1],
                        duration_hours=hours_running,
                        waste_power_kw=avg_power_kw,
                        waste_energy_kwh=waste_energy_kwh,
                        daily_cost_inr=daily_cost,
                        monthly_cost_inr=monthly_cost,
                        annual_cost_inr=annual_cost,
                        reason=(f"{device_type} in {zone_id} continues running {hours_running}h "
                               f"after occupancy ended. Should auto-shutoff."),
                        confidence=0.92,
                        recommended_actions=actions,
                        building_id=group['building_id'].iloc[0] if 'building_id' in group.columns else "BLDG01",
                        floor_number=group['floor_number'].iloc[0] if 'floor_number' in group.columns else 0
                    )
                    
                    alerts.append(alert)
                    break  # One alert per occupancy transition
        
        return alerts
    
    def detect_seasonal_mismatch(self, df: pd.DataFrame) -> List[WasteAlert]:
        """
        Seasonal Mismatch: Wrong device running for season
        
        Example:
        - Season = 'Summer' (avg temp 30°C+)
        - Heating device is ON
        - Unoccupied zone
        - Unreasonable for summer
        """
        alerts = []
        
        for (zone_id, device_type), group in df.groupby(['zone_id', 'device_type']):
            
            # Only check heating/cooling devices
            if device_type.lower() not in ['heating', 'ac', 'air_conditioner', 'heater', 'fan']:
                continue
            
            group_with_season = group[group['season'].notna()]
            
            if len(group_with_season) == 0:
                continue
            
            # Summer heating or winter cooling in unoccupied zones
            for season in ['Summer', 'Summer']:
                season_data = group_with_season[group_with_season['season'] == season].copy()
                
                if len(season_data) == 0:
                    continue
                
                # In summer, heating should not be running
                if season == 'Summer' and device_type.lower() in ['heating', 'heater']:
                    unoccupied_running = season_data[
                        (season_data['occupancy_status'] == 'Unoccupied') &
                        (season_data['device_state'] == 'ON')
                    ]
                    
                    if len(unoccupied_running) > 0:
                        hours = len(unoccupied_running)
                        avg_power = unoccupied_running['power_kw'].mean()
                        waste_energy_kwh = avg_power * hours
                        
                        annual_cost = waste_energy_kwh * self.cost_per_kwh * (365/len(unoccupied_running))
                        
                        alert = WasteAlert(
                            waste_type='seasonal_mismatch',
                            zone_id=zone_id,
                            device_type=device_type,
                            severity='high',
                            first_detected=unoccupied_running['timestamp'].min(),
                            last_detected=unoccupied_running['timestamp'].max(),
                            duration_hours=hours,
                            waste_power_kw=avg_power,
                            waste_energy_kwh=waste_energy_kwh,
                            daily_cost_inr=waste_energy_kwh * self.cost_per_kwh,
                            monthly_cost_inr=waste_energy_kwh * self.cost_per_kwh * 30,
                            annual_cost_inr=annual_cost,
                            reason=(f"Heating device {device_type} running in {season} "
                                   f"in {zone_id} while unoccupied. Likely thermostat malfunction."),
                            confidence=0.88,
                            recommended_actions=[
                                {
                                    'priority': 'CRITICAL',
                                    'description': 'Inspect thermostat - may be malfunctioning',
                                    'estimated_cost_inr': 2000,
                                    'payback_days': 2
                                }
                            ]
                        )
                        
                        alerts.append(alert)
        
        return alerts
    
    def detect_night_mode_violations(self, df: pd.DataFrame) -> List[WasteAlert]:
        """
        Night Mode Violation: Secondary systems active during 10 PM - 6 AM in unoccupied zones
        """
        alerts = []
        
        # Define night hours
        night_hours = set(range(22, 24)) | set(range(0, 6))
        
        for (zone_id, device_type), group in df.groupby(['zone_id', 'device_type']):
            
            # Only check auxiliary systems
            if device_type.lower() not in ['light', 'fan', 'display', 'screen', 'auxiliary']:
                continue
            
            group['hour'] = pd.to_datetime(group['timestamp']).dt.hour
            
            # Find night-time unoccupied usage
            night_unoccupied = group[
                (group['hour'].isin(night_hours)) &
                (group['occupancy_status'] == 'Unoccupied') &
                (group['device_state'] == 'ON')
            ]
            
            if len(night_unoccupied) > 3:  # More than 3 nights
                hours = len(night_unoccupied)
                avg_power = night_unoccupied['power_kw'].mean()
                waste_energy_kwh = avg_power * hours
                
                daily_cost = avg_power * 8 * self.cost_per_kwh  # Assume 8 night hours/day
                annual_cost = daily_cost * 365
                
                alert = WasteAlert(
                    waste_type='night_violation',
                    zone_id=zone_id,
                    device_type=device_type,
                    severity='medium',
                    first_detected=night_unoccupied['timestamp'].min(),
                    last_detected=night_unoccupied['timestamp'].max(),
                    duration_hours=hours,
                    waste_power_kw=avg_power,
                    waste_energy_kwh=waste_energy_kwh,
                    daily_cost_inr=daily_cost,
                    monthly_cost_inr=daily_cost * 30,
                    annual_cost_inr=annual_cost,
                    reason=(f"{device_type} in {zone_id} active {hours}h during night hours "
                           f"(10 PM - 6 AM) while unoccupied. Normal night mode should disable this."),
                    confidence=0.85,
                    recommended_actions=[
                        {'priority': 'MEDIUM', 'description': 'Enable night mode auto-shutoff', 
                         'estimated_cost_inr': 0, 'payback_days': 0},
                        {'priority': 'MEDIUM', 'description': 'Install motion sensor (light)',
                         'estimated_cost_inr': 3000, 'payback_days': 30}
                    ]
                )
                
                alerts.append(alert)
        
        return alerts
    
    def detect_all_waste(self, df: pd.DataFrame) -> List[WasteAlert]:
        """Run all waste detection algorithms"""
        all_alerts = []
        
        all_alerts.extend(self.detect_phantom_loads(df))
        all_alerts.extend(self.detect_post_occupancy_waste(df))
        all_alerts.extend(self.detect_seasonal_mismatch(df))
        all_alerts.extend(self.detect_night_mode_violations(df))
        
        # Sort by financial impact (highest first)
        all_alerts.sort(key=lambda x: x.annual_cost_inr, reverse=True)
        
        self.waste_alerts = all_alerts
        return all_alerts
    
    @staticmethod
    def _recommend_actions_phantom_load(device_type: str, power_kw: float, annual_cost: float) -> List[Dict]:
        """Generate recommendations for phantom load waste"""
        actions = []
        
        # Standard actions
        actions.append({
            'priority': 'HIGH',
            'description': f'Install smart power strip with auto-shutoff (schedule 8 PM - 6 AM)',
            'estimated_cost_inr': 2500,
            'payback_days': int(2500 / (annual_cost / 365))
        })
        
        if 'server' in device_type.lower():
            actions.append({
                'priority': 'HIGH',
                'description': 'Enable wake-on-LAN + schedule server hibernation (unoccupied hours)',
                'estimated_cost_inr': 0,
                'payback_days': 0
            })
        
        if 'light' in device_type.lower():
            actions.append({
                'priority': 'MEDIUM',
                'description': 'Install motion-based vacancy sensor',
                'estimated_cost_inr': 4000,
                'payback_days': int(4000 / (annual_cost / 365))
            })
        
        if 'ac' in device_type.lower() or 'heating' in device_type.lower():
            actions.append({
                'priority': 'MEDIUM',
                'description': 'Implement occupancy-aware HVAC scheduling',
                'estimated_cost_inr': 8000,
                'payback_days': int(8000 / (annual_cost / 365)) if annual_cost > 0 else 999
            })
        
        return actions[:3]  # Top 3 actions
    
    @staticmethod
    def _recommend_actions_post_occupancy(device_type: str, hours_wasted: float, annual_cost: float) -> List[Dict]:
        """Generate recommendations for post-occupancy waste"""
        actions = []
        
        actions.append({
            'priority': 'HIGH',
            'description': f'Install occupancy-based auto-shutoff timer ({int(15)} min delay)',
            'estimated_cost_inr': 1500,
            'payback_days': int(1500 / (annual_cost / 365)) if annual_cost > 0 else 30
        })
        
        if 'light' in device_type.lower():
            actions.append({
                'priority': 'MEDIUM',
                'description': 'Enable daylight harvesting + occupancy sensor',
                'estimated_cost_inr': 5000,
                'payback_days': int(5000 / (annual_cost / 365)) if annual_cost > 0 else 60
            })
        
        actions.append({
            'priority': 'MEDIUM',
            'description': 'Train staff on manual shutoff procedures',
            'estimated_cost_inr': 500,
            'payback_days': 3
        })
        
        return actions
    
    def generate_insight_text(self, alert: WasteAlert) -> str:
        """Generate human-readable insight from waste alert"""
        return f"""
🚨 WASTE DETECTED: {alert.waste_type.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Building: {alert.building_id}, Floor {alert.floor_number}, Zone {alert.zone_id} ({alert.area_sqft} sqft)
Device: {alert.device_type}
Severity: {alert.severity.upper()} (Confidence: {alert.confidence*100:.0f}%)

📊 DETAILS:
   Duration: {alert.duration_hours:.1f} hours
   Power: {alert.waste_power_kw:.2f} kW
   Energy wasted: {alert.waste_energy_kwh:.1f} kWh

💰 FINANCIAL IMPACT:
   Daily: ₹{alert.daily_cost_inr:,.0f}
   Monthly: ₹{alert.monthly_cost_inr:,.0f}
   Annual: ₹{alert.annual_cost_inr:,.0f}

📝 REASON: {alert.reason}

✅ RECOMMENDED ACTIONS:
"""  + "\n".join([
    f"   [{action['priority']}] {action['description']}\n"
    f"      Cost: ₹{action['estimated_cost_inr']:,} | "
    f"Payback: {action['payback_days']} days"
    for action in alert.recommended_actions
]) + "\n"
    
    def to_dict(self) -> Dict:
        """Convert alert to dictionary for JSON output"""
        return {
            'waste_type': self.waste_type,
            'zone_id': self.zone_id,
            'device_type': self.device_type,
            'severity': self.severity,
            'duration_hours': self.duration_hours,
            'waste_power_kw': round(self.waste_power_kw, 2),
            'waste_energy_kwh': round(self.waste_energy_kwh, 1),
            'daily_cost_inr': round(self.daily_cost_inr, 2),
            'monthly_cost_inr': round(self.monthly_cost_inr, 2),
            'annual_cost_inr': round(self.annual_cost_inr, 0),
            'confidence': round(self.confidence, 3),
            'reason': self.reason,
            'actions': self.recommended_actions
        }


# Test example
if __name__ == "__main__":
    # Create sample data matching your CSV structure
    sample_data = {
        'timestamp': pd.date_range('2026-02-05', periods=50, freq='H'),
        'building_id': 'BLDG01',
        'floor_number': 4,
        'zone_id': 'SERVER_1',
        'area_sqft': 300,
        'device_type': 'Server',
        'power_kw': [3.8] * 50,  # Continuous 3.8kW
        'device_state': ['ON'] * 50,
        'occupancy_status': ['Unoccupied'] * 50,  # Always unoccupied
        'occupancy_count': [0] * 50,
        'season': ['Winter'] * 50,
    }
    
    df = pd.DataFrame(sample_data)
    
    detector = EnergyWasteDetector(cost_per_kwh=8.5)
    alerts = detector.detect_all_waste(df)
    
    print(f"\n✅ Detected {len(alerts)} waste patterns\n")
    for alert in alerts:
        print(detector.generate_insight_text(alert))
