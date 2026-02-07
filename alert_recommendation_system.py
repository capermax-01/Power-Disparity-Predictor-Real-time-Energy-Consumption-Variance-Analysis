"""
Alert & Recommendation System
Generates prioritized alerts and actionable recommendations based on detected waste.
Implements configurable thresholds, filtering, and business logic for facility managers.

RESPONSIBILITIES:
1. Generate context-aware alerts (no false positives)
2. Prioritize alerts by cost impact and recurrence
3. Create specific, actionable recommendations
4. Calculate ROI for recommended actions
5. Group similar issues (e.g., all post-occupancy HVAC waste)
6. Support filtering by floor, zone, device type, time range
7. Track recommendation implementation and actual savings
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json


class AlertSeverity(str, Enum):
    """Alert priority levels"""
    INFO = "info"
    LOW = "low"  
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationType(str, Enum):
    """Types of recommendations"""
    AUTOMATION = "automation"  # Install smart controller
    SCHEDULING = "scheduling"  # Change schedule/settings
    MAINTENANCE = "maintenance"  # Fix leaking/broken equipment
    BEHAVIOR = "behavior"  # User behavior change
    REPLACEMENT = "replacement"  # Replace with efficient model
    MONITORING = "monitoring"  # Install monitoring to confirm issue


@dataclass
class Alert:
    """Generated alert for viewing by facility manager"""
    alert_id: str
    severity: AlertSeverity
    title: str
    description: str
    location_floor: Optional[str]
    location_zone: Optional[str]
    device_id: str
    device_category: str
    
    # Cost impact (primary decision driver)
    daily_cost_loss_inr: float
    monthly_cost_loss_inr: float
    annual_cost_loss_inr: float
    
    # Context
    waste_type: str  # "phantom_load", "post_occupancy", etc.
    pattern_frequency: str  # "one-time", "daily", "weekly", "recurring"
    first_detected: datetime
    last_detected: datetime
    detection_count: int  # How many times this alert was triggered
    
    # Explainability
    evidence: List[str]  # Why this alert was generated
    occupancy_mismatch: bool  # Key signal - using power when no one there
    
    # Response
    status: str = "open"  # "open", "acknowledged", "investigating", "resolved"
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
    
    # Related recommendations
    recommendation_ids: List[str] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dict"""
        return {
            'alert_id': self.alert_id,
            'severity': self.severity.value,
            'title': self.title,
            'description': self.description,
            'location': {
                'floor': self.location_floor,
                'zone': self.location_zone
            },
            'device': {
                'id': self.device_id,
                'category': self.device_category
            },
            'cost_impact': {
                'daily_inr': round(self.daily_cost_loss_inr, 2),
                'monthly_inr': round(self.monthly_cost_loss_inr, 2),
                'annual_inr': round(self.annual_cost_loss_inr, 0)
            },
            'waste_details': {
                'waste_type': self.waste_type,
                'pattern_frequency': self.pattern_frequency,
                'occupancy_mismatch': self.occupancy_mismatch,
                'detection_count': self.detection_count,
                'time_range': {
                    'first_detected': self.first_detected.isoformat(),
                    'last_detected': self.last_detected.isoformat()
                }
            },
            'evidence': self.evidence,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'recommendations': self.recommendation_ids,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class Recommendation:
    """Specific action to address detected waste"""
    recommendation_id: str
    alert_id: str
    
    type: RecommendationType
    title: str
    description: str
    detailed_action_steps: List[str]
    
    # Business case
    estimated_annual_savings_inr: float
    implementation_cost_inr: float
    payback_period_months: float  # Months to ROI
    confidence_percent: float  # 0-100 confidence this will save money
    
    # Implementation
    responsible_team: str  # "operations", "maintenance", "vendor", "occupants"
    estimated_implementation_days: int
    required_uptime_impact: str  # "none", "minor", "significant"
    
    # Prioritization
    priority: AlertSeverity
    urgency: str  # "low", "normal", "high", "emergency"
    
    # Status tracking
    status: str = "proposed"  # "proposed", "approved", "in_progress", "completed", "rejected"
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    actual_savings_inr: Optional[float] = None  # After implementation
    
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dict"""
        return {
            'recommendation_id': self.recommendation_id,
            'alert_id': self.alert_id,
            'type': self.type.value,
            'title': self.title,
            'description': self.description,
            'action_steps': self.detailed_action_steps,
            'business_case': {
                'estimated_annual_savings_inr': round(self.estimated_annual_savings_inr, 0),
                'implementation_cost_inr': round(self.implementation_cost_inr, 0),
                'payback_months': round(self.payback_period_months, 1),
                'confidence_percent': self.confidence_percent,
                'roi_percent': round((self.estimated_annual_savings_inr / (self.implementation_cost_inr + 1)) * 100, 1)
            },
            'implementation': {
                'responsible_team': self.responsible_team,
                'estimated_days': self.estimated_implementation_days,
                'uptime_impact': self.required_uptime_impact
            },
            'priority': self.priority.value,
            'urgency': self.urgency,
            'status': self.status,
            'approved_by': self.approved_by,
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'actual_savings_inr': self.actual_savings_inr,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class BuildingReport:
    """Comprehensive report for entire building"""
    building_id: str
    report_date: datetime
    
    # Alerts summary
    total_alerts: int
    critical_alerts: int
    high_alerts: int
    open_alerts: int
    
    # Top waste sources
    top_waste_leaks: List[Alert]  # Top 3 by annual cost
    
    # Cost summary
    total_monthly_waste_inr: float
    total_annual_waste_inr: float
    projected_annual_savings_if_fixed_inr: float
    
    # By category
    waste_by_category: Dict[str, float]  # device_category -> annual_inr
    waste_by_floor: Dict[str, float]  # floor -> annual_inr
    waste_by_type: Dict[str, float]  # waste_type -> annual_inr
    
    # Recommendations
    total_recommendations: int
    approved_recommendations: int
    projected_payback_months: float
    
    # Trends
    trend_vs_last_month: float  # percent change
    trend_vs_last_year: float  # percent change
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dict"""
        return {
            'building_id': self.building_id,
            'report_date': self.report_date.isoformat(),
            'summary': {
                'total_alerts': self.total_alerts,
                'critical': self.critical_alerts,
                'high': self.high_alerts,
                'open': self.open_alerts
            },
            'cost_impact': {
                'monthly_inr': round(self.total_monthly_waste_inr, 0),
                'annual_inr': round(self.total_annual_waste_inr, 0),
                'potential_savings_annual_inr': round(self.projected_annual_savings_if_fixed_inr, 0)
            },
            'top_waste_leaks': [alert.to_dict() for alert in self.top_waste_leaks],
            'waste_by_category': {k: round(v, 0) for k, v in self.waste_by_category.items()},
            'waste_by_floor': {k: round(v, 0) for k, v in self.waste_by_floor.items()},
            'waste_by_type': {k: round(v, 0) for k, v in self.waste_by_type.items()},
            'recommendations': {
                'total': self.total_recommendations,
                'approved': self.approved_recommendations,
                'projected_payback_months': round(self.projected_payback_months, 1)
            },
            'trends': {
                'vs_last_month_percent': round(self.trend_vs_last_month, 1),
                'vs_last_year_percent': round(self.trend_vs_last_year, 1)
            }
        }


class AlertGenerator:
    """
    Generates and manages alerts and recommendations.
    """
    
    def __init__(self, cost_per_kwh_inr: float = 8.0):
        self.cost_per_kwh_inr = cost_per_kwh_inr
        self.alerts: Dict[str, Alert] = {}
        self.recommendations: Dict[str, Recommendation] = {}
        self.alert_counter = 0
        self.recommendation_counter = 0
    
    def generate_alert_from_insight(self, device_id: str, device_category: str,
                                   waste_type: str, risk_level: str,
                                   location_floor: Optional[str],
                                   location_zone: Optional[str],
                                   power_disparity_w: float,
                                   duration_hours: float,
                                   occupancy_mismatch: bool,
                                   evidence: List[str]) -> Alert:
        """
        Convert an energy waste insight into an actionable alert.
        
        Args:
            device_id: Device identifier
            device_category: Category of device
            waste_type: Type of waste (phantom_load, post_occupancy, etc.)
            risk_level: Severity (low, medium, high, critical)
            location_floor: Floor number/name
            location_zone: Zone/area identifier
            power_disparity_w: Wasted power in watts
            duration_hours: How long this wastes power during typical day
            occupancy_mismatch: Whether power use during unoccupied time
            evidence: List of evidence strings
            
        Returns:
            Generated Alert object
        """
        self.alert_counter += 1
        alert_id = f"ALERT_{self.alert_counter:06d}"
        
        # Calculate cost impact
        daily_wasted_kwh = (power_disparity_w * duration_hours) / 1000
        daily_cost = daily_wasted_kwh * self.cost_per_kwh_inr
        monthly_cost = daily_cost * 30
        annual_cost = daily_cost * 365
        
        # Map risk level to severity
        severity_map = {
            'critical': AlertSeverity.CRITICAL,
            'high': AlertSeverity.HIGH,
            'medium': AlertSeverity.MEDIUM,
            'low': AlertSeverity.LOW
        }
        severity = severity_map.get(risk_level, AlertSeverity.MEDIUM)
        
        # Create human-readable title
        titles = {
            'phantom_load': f"Phantom Load: {device_category} consuming power 24/7",
            'post_occupancy': f"Post-Occupancy Waste: {device_category} left on after hours",
            'inefficient_usage': f"Inefficient Usage: {device_category} running suboptimally",
            'normal': f"Notice: {device_category} operating normally"
        }
        title = titles.get(waste_type, f"Energy Waste: {waste_type}")
        
        # Description with cost emphasis
        description = f"{device_category.title()} wasting ₹{annual_cost:,.0f}/year ({daily_cost:,.0f}/day). "
        if occupancy_mismatch:
            description += "Device consuming power when building is unoccupied. "
        description += "This includes recommended actions for cost recovery."
        
        alert = Alert(
            alert_id=alert_id,
            severity=severity,
            title=title,
            description=description,
            location_floor=location_floor,
            location_zone=location_zone,
            device_id=device_id,
            device_category=device_category,
            daily_cost_loss_inr=daily_cost,
            monthly_cost_loss_inr=monthly_cost,
            annual_cost_loss_inr=annual_cost,
            waste_type=waste_type,
            pattern_frequency="recurring" if duration_hours >= 4 else "periodic",
            first_detected=datetime.now(),
            last_detected=datetime.now(),
            detection_count=1,
            evidence=evidence,
            occupancy_mismatch=occupancy_mismatch
        )
        
        self.alerts[alert_id] = alert
        return alert
    
    def generate_recommendations(self, alert: Alert) -> List[Recommendation]:
        """
        Generate specific recommendations to address an alert.
        
        Args:
            alert: Alert object to address
            
        Returns:
            List of Recommendation objects
        """
        recommendations = []
        
        # Recommendations depend on waste type
        if alert.waste_type == 'phantom_load':
            # Recommend smart outlet/power strip
            self.recommendation_counter += 1
            rec1 = Recommendation(
                recommendation_id=f"REC_{self.recommendation_counter:06d}",
                alert_id=alert.alert_id,
                type=RecommendationType.AUTOMATION,
                title="Install Smart Power Strip",
                description="Smart outlet with motion sensor and schedule timer to eliminate phantom load.",
                detailed_action_steps=[
                    "Identify device and power outlet location",
                    "Procure smart multi-outlet power strip (₹500-1000)",
                    "Install and configure schedule (off during off-hours)",
                    "Test functionality and confirm power drops to ~2W"
                ],
                estimated_annual_savings_inr=alert.annual_cost_loss_inr * 0.85,
                implementation_cost_inr=800,
                payback_period_months=0.5,
                confidence_percent=92,
                responsible_team="operations",
                estimated_implementation_days=1,
                required_uptime_impact="none",
                priority=alert.severity,
                urgency="high"
            )
            recommendations.append(rec1)
            
            # Recommend monitoring
            self.recommendation_counter += 1
            rec2 = Recommendation(
                recommendation_id=f"REC_{self.recommendation_counter:06d}",
                alert_id=alert.alert_id,
                type=RecommendationType.MONITORING,
                title="Install Power Monitoring",
                description="Add sub-metering to track actual consumption and validate savings.",
                detailed_action_steps=[
                    "Install smart meter on target circuit",
                    "Configure alerts in building management system",
                    "Monthly review of consumption trends"
                ],
                estimated_annual_savings_inr=alert.annual_cost_loss_inr * 0.05,  # Just from visibility
                implementation_cost_inr=1200,
                payback_period_months=24,
                confidence_percent=70,
                responsible_team="maintenance",
                estimated_implementation_days=3,
                required_uptime_impact="minor",
                priority=AlertSeverity.MEDIUM,
                urgency="normal"
            )
            recommendations.append(rec2)
        
        elif alert.waste_type == 'post_occupancy':
            # Recommend occupancy-based automation
            self.recommendation_counter += 1
            rec1 = Recommendation(
                recommendation_id=f"REC_{self.recommendation_counter:06d}",
                alert_id=alert.alert_id,
                type=RecommendationType.AUTOMATION,
                title="Install Occupancy-Based Controller",
                description="Smart controller combining occupancy sensor + timer to auto-shutdown device after occupants leave.",
                detailed_action_steps=[
                    "Install PIR occupancy sensor near main entry",
                    "Connect to smart relay/contactor for device",
                    "Configure grace period (15-30 min after last motion)",
                    "Test multiple occupancy/departure scenarios"
                ],
                estimated_annual_savings_inr=alert.annual_cost_loss_inr * 0.75,
                implementation_cost_inr=2500,
                payback_period_months=3,
                confidence_percent=88,
                responsible_team="maintenance",
                estimated_implementation_days=2,
                required_uptime_impact="minor",
                priority=alert.severity,
                urgency="high"
            )
            recommendations.append(rec1)
        
        # Always recommend behavior change (no cost)
        self.recommendation_counter += 1
        rec_behavior = Recommendation(
            recommendation_id=f"REC_{self.recommendation_counter:06d}",
            alert_id=alert.alert_id,
            type=RecommendationType.BEHAVIOR,
            title="Occupant Awareness Campaign",
            description="Low-cost behavior change through signage and email reminders about turning off equipment.",
            detailed_action_steps=[
                "Send email reminder to building occupants",
                "Post reminder signage near device",
                "Include in next facility briefing",
                "Monthly reminder emails"
            ],
            estimated_annual_savings_inr=alert.annual_cost_loss_inr * 0.15,
            implementation_cost_inr=100,
            payback_period_months=0.1,
            confidence_percent=40,
            responsible_team="operations",
            estimated_implementation_days=1,
            required_uptime_impact="none",
            priority=AlertSeverity.LOW,
            urgency="low"
        )
        recommendations.append(rec_behavior)
        
        self.recommendations.update({rec.recommendation_id: rec for rec in recommendations})
        return recommendations
    
    def filter_alerts(self, floor: Optional[str] = None,
                     device_category: Optional[str] = None,
                     min_severity: Optional[AlertSeverity] = None,
                     status: Optional[str] = None,
                     min_annual_cost_inr: Optional[float] = None) -> List[Alert]:
        """
        Filter alerts by various criteria.
        
        Args:
            floor: Filter by floor (e.g., "3" or "Ground")
            device_category: Filter by appliance type
            min_severity: Minimum severity to include
            status: Alert status filter
            min_annual_cost_inr: Minimum annual cost impact
            
        Returns:
            Filtered list of alerts
        """
        filtered = list(self.alerts.values())
        
        if floor:
            filtered = [a for a in filtered if a.location_floor == floor]
        
        if device_category:
            filtered = [a for a in filtered if a.device_category.lower() == device_category.lower()]
        
        if min_severity:
            severity_order = {
                AlertSeverity.INFO: 0,
                AlertSeverity.LOW: 1,
                AlertSeverity.MEDIUM: 2,
                AlertSeverity.HIGH: 3,
                AlertSeverity.CRITICAL: 4
            }
            min_val = severity_order.get(min_severity, 0)
            filtered = [a for a in filtered if severity_order.get(a.severity, 0) >= min_val]
        
        if status:
            filtered = [a for a in filtered if a.status == status]
        
        if min_annual_cost_inr:
            filtered = [a for a in filtered if a.annual_cost_loss_inr >= min_annual_cost_inr]
        
        return filtered
    
    def build_building_report(self, building_id: str) -> BuildingReport:
        """
        Build comprehensive report for entire building.
        
        Args:
            building_id: Building identifier
            
        Returns:
            BuildingReport object
        """
        all_alerts = list(self.alerts.values())
        
        # Summary stats
        total_alerts = len(all_alerts)
        critical = sum(1 for a in all_alerts if a.severity == AlertSeverity.CRITICAL)
        high = sum(1 for a in all_alerts if a.severity == AlertSeverity.HIGH)
        open_alerts = sum(1 for a in all_alerts if a.status == "open")
        
        # Cost summary
        total_monthly = sum(a.monthly_cost_loss_inr for a in all_alerts)
        total_annual = sum(a.annual_cost_loss_inr for a in all_alerts)
        
        # Top 3 waste leaks by cost
        top_waste = sorted(all_alerts, key=lambda a: a.annual_cost_loss_inr, reverse=True)[:3]
        
        # Aggregate by category
        waste_by_category = {}
        waste_by_floor = {}
        waste_by_type = {}
        
        for alert in all_alerts:
            waste_by_category[alert.device_category] = waste_by_category.get(alert.device_category, 0) + alert.annual_cost_loss_inr
            floor_key = alert.location_floor or "Unknown"
            waste_by_floor[floor_key] = waste_by_floor.get(floor_key, 0) + alert.annual_cost_loss_inr
            waste_by_type[alert.waste_type] = waste_by_type.get(alert.waste_type, 0) + alert.annual_cost_loss_inr
        
        # Recommendations stats
        total_recs = len(self.recommendations)
        approved_recs = sum(1 for r in self.recommendations.values() if r.status == "approved")
        payback = np.mean([r.payback_period_months for r in self.recommendations.values()]) if self.recommendations else 0
        
        # Potential savings
        potential_savings = sum(r.estimated_annual_savings_inr for r in self.recommendations.values())
        
        report = BuildingReport(
            building_id=building_id,
            report_date=datetime.now(),
            total_alerts=total_alerts,
            critical_alerts=critical,
            high_alerts=high,
            open_alerts=open_alerts,
            top_waste_leaks=top_waste,
            total_monthly_waste_inr=total_monthly,
            total_annual_waste_inr=total_annual,
            projected_annual_savings_if_fixed_inr=potential_savings,
            waste_by_category=waste_by_category,
            waste_by_floor=waste_by_floor,
            waste_by_type=waste_by_type,
            total_recommendations=total_recs,
            approved_recommendations=approved_recs,
            projected_payback_months=payback,
            trend_vs_last_month=0.0,  # Would calculate from historical data
            trend_vs_last_year=0.0  # Would calculate from historical data
        )
        
        return report
