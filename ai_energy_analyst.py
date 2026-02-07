"""
AI-Based Energy Waste Detection Engine (CORRECTED LOGIC)
Follows energy conservation rules - no double counting
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime, time
import pandas as pd
import numpy as np
from collections import defaultdict


@dataclass
class WasteIssue:
    """Represents a single energy waste issue"""
    title: str
    location: str
    device: str
    time_period: str
    extra_energy_kwh: float
    cost_per_day: float
    action: str
    reason: str
    severity: str


@dataclass
class EnergyAnalysisReport:
    """Complete energy analysis report"""
    total_energy_kwh: float
    energy_wasted_kwh: float
    money_lost_today: float
    monthly_savings_potential: float
    efficiency_score: int
    issues: List[WasteIssue]
    daily_loss: float
    monthly_loss: float
    yearly_loss: float
    automation_rules: List[str]
    main_waste_source: str
    timestamp: datetime = field(default_factory=datetime.now)


class AIEnergyAnalyst:
    """AI Energy Analyst - Physically Correct Energy Waste Detection"""
    
    def __init__(self, cost_per_kwh: float = 8.0):
        self.cost_per_kwh = cost_per_kwh
        self.business_start = time(9, 0)
        self.business_end = time(18, 0)
        self.phantom_threshold = {
            'hvac': 200,
            'lighting': 50,
            'computer': 20,
            'printer': 15,
            'default': 10
        }
    
    def analyze(self, readings: List[Dict]) -> EnergyAnalysisReport:
        """Main analysis - PHYSICALLY CORRECT, NO DOUBLE COUNTING"""
        if not readings:
            return self._empty_report()
        
        df = pd.DataFrame([r if isinstance(r, dict) else r.to_dict() for r in readings])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        df['duration_hours'] = 1.0
        
        # Step 1: Calculate TOTAL ENERGY USED
        df['energy_kwh'] = (df['power_w'] / 1000.0) * df['duration_hours']
        total_energy_used = df['energy_kwh'].sum()
        
        # Step 2: Learn baselines
        baselines = self._learn_baselines(df)
        
        # Step 3: Classify each record (PRIORITY-BASED, NO OVERLAP)
        df['waste_category'] = 'normal'
        df['expected_baseline_w'] = 0.0
        df['excess_power_w'] = 0.0
        df['wasted_energy_kwh'] = 0.0
        
        for idx, row in df.iterrows():
            device_id = row['device_id']
            baseline = baselines.get(device_id, {})
            
            # Priority 1: Phantom Load
            if self._is_phantom_load(row, baseline):
                df.at[idx, 'waste_category'] = 'phantom_load'
                df.at[idx, 'expected_baseline_w'] = 0.0
                df.at[idx, 'excess_power_w'] = row['power_w']
                df.at[idx, 'wasted_energy_kwh'] = (row['power_w'] / 1000.0) * row['duration_hours']
                continue
            
            # Priority 2: Unoccupied Usage
            if self._is_unoccupied_usage(row, baseline):
                expected = baseline.get('unoccupied_baseline', 0)
                df.at[idx, 'waste_category'] = 'unoccupied_usage'
                df.at[idx, 'expected_baseline_w'] = expected
                df.at[idx, 'excess_power_w'] = max(0, row['power_w'] - expected)
                df.at[idx, 'wasted_energy_kwh'] = (df.at[idx, 'excess_power_w'] / 1000.0) * row['duration_hours']
                continue
            
            # Priority 3: After-Hours Usage
            if self._is_after_hours(row, baseline):
                expected = baseline.get('after_hours_baseline', 0)
                df.at[idx, 'waste_category'] = 'after_hours'
                df.at[idx, 'expected_baseline_w'] = expected
                df.at[idx, 'excess_power_w'] = max(0, row['power_w'] - expected)
                df.at[idx, 'wasted_energy_kwh'] = (df.at[idx, 'excess_power_w'] / 1000.0) * row['duration_hours']
                continue
        
        # Step 4: Calculate TOTAL WASTED ENERGY
        total_wasted_energy = df['wasted_energy_kwh'].sum()
        
        # Safety check
        if total_wasted_energy > total_energy_used:
            scale_factor = total_energy_used * 0.95 / total_wasted_energy
            df['wasted_energy_kwh'] = df['wasted_energy_kwh'] * scale_factor
            total_wasted_energy = df['wasted_energy_kwh'].sum()
        
        # Step 5: Generate issues
        issues = self._generate_issues_from_classified_data(df, baselines)
        
        # Step 6: Calculate costs
        daily_loss = total_wasted_energy * self.cost_per_kwh
        monthly_loss = daily_loss * 30
        yearly_loss = daily_loss * 365
        
        # Step 7: Calculate efficiency
        efficiency_score = self._calculate_efficiency_score(total_energy_used, total_wasted_energy)
        
        # Step 8: Generate automation
        automation_rules = self._generate_automation_rules(issues)
        
        # Step 9: Main waste source
        main_waste_source = self._identify_main_waste_source(issues)
        
        issues.sort(key=lambda x: x.cost_per_day, reverse=True)
        
        return EnergyAnalysisReport(
            total_energy_kwh=round(total_energy_used, 2),
            energy_wasted_kwh=round(total_wasted_energy, 2),
            money_lost_today=round(daily_loss, 2),
            monthly_savings_potential=round(monthly_loss, 2),
            efficiency_score=efficiency_score,
            issues=issues,
            daily_loss=round(daily_loss, 2),
            monthly_loss=round(monthly_loss, 2),
            yearly_loss=round(yearly_loss, 0),
            automation_rules=automation_rules,
            main_waste_source=main_waste_source
        )
    
    def _learn_baselines(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """Learn normal behavior for each device"""
        baselines = {}
        
        for device_id in df['device_id'].unique():
            device_df = df[df['device_id'] == device_id]
            category = device_df['device_category'].iloc[0]
            
            occupied_data = device_df[device_df['occupancy_status'] == 'occupied']
            unoccupied_data = device_df[device_df['occupancy_status'] == 'unoccupied']
            
            occupied_baseline = occupied_data['power_w'].mean() if len(occupied_data) > 0 else device_df['power_w'].mean()
            
            # For unoccupied baseline, use 10% of occupied for HVAC/lighting, 0 for others
            if category.lower() in ['hvac', 'lighting']:
                unoccupied_baseline = unoccupied_data['power_w'].mean()
            else:
                unoccupied_baseline = 0
            
            baselines[device_id] = {
                'avg_power': device_df['power_w'].mean(),
                'max_power': device_df['power_w'].max(),
                'min_power': device_df['power_w'].min(),
                'occupied_baseline': occupied_baseline,
                'unoccupied_baseline': unoccupied_baseline,
                'after_hours_baseline': unoccupied_baseline,
                'category': category,
                'location': f"{device_df['location_floor'].iloc[0] or 'Unknown Floor'}, {device_df['location_zone'].iloc[0] or 'Unknown Zone'}"
            }
        
        return baselines
    
    def _is_phantom_load(self, row: pd.Series, baseline: Dict) -> bool:
        """Check if record is phantom load"""
        category = baseline.get('category', '').lower()
        
        if category in ['fridge', 'freezer', 'server', 'security', 'router']:
            return False
        
        if row['occupancy_status'] == 'unoccupied':
            threshold = self.phantom_threshold.get(category, self.phantom_threshold['default'])
            # Phantom load: constant low power that should be zero
            if row['power_w'] > 0 and row['power_w'] <= threshold * 3:
                return True
        
        return False
    
    def _is_unoccupied_usage(self, row: pd.Series, baseline: Dict) -> bool:
        """Check if high usage when unoccupied"""
        category = baseline.get('category', '').lower()
        
        if category in ['fridge', 'freezer', 'server', 'security', 'router']:
            return False
        
        if row['occupancy_status'] == 'unoccupied':
            # For HVAC and lighting, any significant power when unoccupied is waste
            if category in ['hvac', 'lighting']:
                expected = baseline.get('unoccupied_baseline', 0)
                if row['power_w'] > expected + 100:  # More than expected + 100W
                    return True
            else:
                expected = baseline.get('unoccupied_baseline', 0)
                if row['power_w'] > expected + 50:
                    return True
        
        return False
    
    def _is_after_hours(self, row: pd.Series, baseline: Dict) -> bool:
        """Check if after business hours"""
        category = baseline.get('category', '').lower()
        
        if category in ['fridge', 'freezer', 'server', 'security', 'router']:
            return False
        
        hour = row['timestamp'].hour
        is_after_hours = (hour < self.business_start.hour) or (hour >= self.business_end.hour)
        
        if is_after_hours and row['occupancy_status'] != 'occupied':
            expected = baseline.get('after_hours_baseline', 0)
            if row['power_w'] > expected + 100:
                return True
        
        return False
    
    def _generate_issues_from_classified_data(self, df: pd.DataFrame, baselines: Dict) -> List[WasteIssue]:
        """Generate issues from classified waste records"""
        issues = []
        waste_df = df[df['waste_category'] != 'normal']
        
        for device_id in waste_df['device_id'].unique():
            device_waste = waste_df[waste_df['device_id'] == device_id]
            baseline = baselines.get(device_id, {})
            
            for waste_type in device_waste['waste_category'].unique():
                type_waste = device_waste[device_waste['waste_category'] == waste_type]
                
                total_wasted_kwh = type_waste['wasted_energy_kwh'].sum()
                avg_excess_power = type_waste['excess_power_w'].mean()
                cost_per_day = total_wasted_kwh * self.cost_per_kwh
                
                if waste_type == 'phantom_load':
                    issues.append(WasteIssue(
                        title=f"Phantom Load: {baseline['category'].upper()} Never Turns Off",
                        location=baseline['location'],
                        device=device_id,
                        time_period="24/7",
                        extra_energy_kwh=round(total_wasted_kwh, 2),
                        cost_per_day=round(cost_per_day, 2),
                        action=f"Install smart plug to cut power when not in use",
                        reason=f"Device draws {int(avg_excess_power)}W constantly, even when 'off'",
                        severity="medium" if cost_per_day > 20 else "low"
                    ))
                
                elif waste_type == 'unoccupied_usage':
                    issues.append(WasteIssue(
                        title=f"{baseline['category'].upper()} Active When Space Unoccupied",
                        location=baseline['location'],
                        device=device_id,
                        time_period="During unoccupied periods",
                        extra_energy_kwh=round(total_wasted_kwh, 2),
                        cost_per_day=round(cost_per_day, 2),
                        action=f"Connect to occupancy sensor for automatic control",
                        reason=f"Device uses {int(avg_excess_power)}W when no one is present",
                        severity="critical" if cost_per_day > 100 else "high"
                    ))
                
                elif waste_type == 'after_hours':
                    issues.append(WasteIssue(
                        title=f"{baseline['category'].upper()} Running After Hours",
                        location=baseline['location'],
                        device=device_id,
                        time_period=f"After {self.business_end.hour}:00 PM",
                        extra_energy_kwh=round(total_wasted_kwh, 2),
                        cost_per_day=round(cost_per_day, 2),
                        action=f"Set timer to turn off at {self.business_end.hour}:00 PM",
                        reason=f"Consuming {int(avg_excess_power)}W when building is empty",
                        severity="high" if cost_per_day > 50 else "medium"
                    ))
        
        return issues
    
    def _calculate_efficiency_score(self, total_energy: float, wasted_energy: float) -> int:
        """Calculate efficiency score (0-100)"""
        if total_energy == 0:
            return 100
        waste_percentage = (wasted_energy / total_energy) * 100
        efficiency = 100 - waste_percentage
        return max(0, min(100, int(efficiency)))
    
    def _generate_automation_rules(self, issues: List[WasteIssue]) -> List[str]:
        """Generate simple IF-THEN automation rules"""
        rules = []
        
        after_hours = [i for i in issues if "After Hours" in i.title]
        phantom = [i for i in issues if "Phantom Load" in i.title]
        unoccupied = [i for i in issues if "Unoccupied" in i.title]
        
        if after_hours:
            rules.append("IF time is after 6:00 PM, THEN turn off all HVAC and lighting systems")
        
        if unoccupied:
            rules.append("IF occupancy sensor detects no motion for 15 minutes, THEN reduce HVAC to setback mode")
            rules.append("IF space is unoccupied, THEN turn off all non-essential lighting")
        
        if phantom:
            rules.append("IF device is in standby mode for more than 1 hour, THEN cut power completely")
        
        return rules
    
    def _identify_main_waste_source(self, issues: List[WasteIssue]) -> str:
        """Identify the main source of waste"""
        if not issues:
            return "No significant energy waste detected. System is operating efficiently."
        
        category_costs = defaultdict(float)
        for issue in issues:
            if "HVAC" in issue.title:
                category_costs["HVAC"] += issue.cost_per_day
            elif "Lighting" in issue.title or "LIGHTING" in issue.title:
                category_costs["Lighting"] += issue.cost_per_day
            elif "Phantom" in issue.title:
                category_costs["Phantom Loads"] += issue.cost_per_day
            else:
                category_costs["Other Devices"] += issue.cost_per_day
        
        if not category_costs:
            return "Energy waste detected across multiple device categories."
        
        main_source = max(category_costs.items(), key=lambda x: x[1])
        percentage = (main_source[1] / sum(category_costs.values())) * 100
        
        return f"Most waste comes from {main_source[0]} ({int(percentage)}% of total waste)"
    
    def _empty_report(self) -> EnergyAnalysisReport:
        """Return empty report when no data"""
        return EnergyAnalysisReport(
            total_energy_kwh=0,
            energy_wasted_kwh=0,
            money_lost_today=0,
            monthly_savings_potential=0,
            efficiency_score=100,
            issues=[],
            daily_loss=0,
            monthly_loss=0,
            yearly_loss=0,
            automation_rules=[],
            main_waste_source="No data available for analysis"
        )
    
    def report_to_dict(self, report: EnergyAnalysisReport) -> Dict[str, Any]:
        """Convert report to dictionary for API response"""
        return {
            "summary": {
                "total_energy_kwh": report.total_energy_kwh,
                "energy_wasted_kwh": report.energy_wasted_kwh,
                "money_lost_today": report.money_lost_today,
                "monthly_savings_potential": report.monthly_savings_potential,
                "efficiency_score": report.efficiency_score
            },
            "issues": [
                {
                    "title": issue.title,
                    "location": issue.location,
                    "device": issue.device,
                    "time_period": issue.time_period,
                    "extra_energy_kwh": issue.extra_energy_kwh,
                    "cost_per_day": issue.cost_per_day,
                    "action": issue.action,
                    "reason": issue.reason,
                    "severity": issue.severity
                }
                for issue in report.issues
            ],
            "cost_savings": {
                "daily_loss": report.daily_loss,
                "monthly_loss": report.monthly_loss,
                "yearly_loss": report.yearly_loss
            },
            "automation_suggestions": report.automation_rules,
            "conclusion": report.main_waste_source,
            "timestamp": report.timestamp.isoformat()
        }
