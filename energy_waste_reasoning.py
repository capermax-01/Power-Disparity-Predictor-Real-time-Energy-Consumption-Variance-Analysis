"""
Energy Waste Detection & Reasoning Engine
Converts ML power disparity signals into explainable, actionable waste insights.

ARCHITECTURE:
1. ML Model: Outputs power disparity signal (variance from baseline)
2. Reasoning Layer: Interprets signal using occupancy + time context
3. Classification: Maps signals to waste types
4. Insight Generation: Create human-readable, cost-aware recommendations
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json


class WasteType(str, Enum):
    """Energy waste classification"""
    PHANTOM_LOAD = "phantom_load"
    POST_OCCUPANCY = "post_occupancy"
    INEFFICIENT_USAGE = "inefficient_usage"
    NORMAL = "normal"


class RiskLevel(str, Enum):
    """Risk severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OccupancyStatus(str, Enum):
    """Occupancy states"""
    OCCUPIED = "occupied"
    UNOCCUPIED = "unoccupied"
    UNKNOWN = "unknown"


@dataclass
class PowerDisparitySignal:
    """ML model output - power disparity measurement"""
    predicted_power_w: float  # ML predicted disparity
    confidence: float  # ML prediction confidence (0-1)
    baseline_power_w: float  # Expected normal power
    actual_power_w: float  # Observed power (optional)
    variance_percent: float  # Deviation from baseline


@dataclass
class OccupancyContext:
    """Building occupancy and time context"""
    occupancy_status: OccupancyStatus
    occupancy_confidence: float  # 0-1, how sure are we
    hour: int  # 0-23
    day_of_week: int  # 0-6 (0=Monday)
    is_weekend: bool
    season: str  # 'winter', 'spring', 'summer', 'fall'
    
    @property
    def is_working_hours(self) -> bool:
        """9 AM - 6 PM on weekdays"""
        return 9 <= self.hour < 18 and self.day_of_week < 5
    
    @property
    def is_night_hours(self) -> bool:
        """10 PM - 6 AM (typical off-hours)"""
        return self.hour >= 22 or self.hour < 6


@dataclass
class ActionItem:
    """Recommended corrective action"""
    priority: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    description: str
    estimated_cost_inr: float
    estimated_payback_days: int
    confidence: float


@dataclass
class EnergyWasteInsight:
    """Complete energy waste insight with reasoning"""
    waste_type: WasteType
    risk_level: RiskLevel
    
    # What happened
    appliance_category: str
    location_description: str  # e.g., "Office Zone A"
    detected_at: str  # ISO timestamp
    
    # How bad is it
    power_disparity_w: float
    estimated_waste_power_w: float
    duration_hours: float
    total_wasted_kwh: float
    
    # Cost impact
    cost_per_kwh: float  # tariff
    estimated_daily_loss_inr: float
    estimated_monthly_loss_inr: float
    estimated_annual_loss_inr: float
    
    # Why it happened (explainability)
    occupancy_mismatch: bool  # Key signal
    time_pattern: str  # "night_hours", "after_occupancy", "during_occupancy", "unknown"
    signal_strength: str  # "weak", "moderate", "strong"
    reasoning_chain: List[str]  # Step-by-step explanation
    
    # Actionable recommendations
    actions: List[ActionItem]
    
    # Confidence in diagnosis
    confidence: float  # 0-1
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dict"""
        return {
            'waste_type': self.waste_type.value,
            'risk_level': self.risk_level.value,
            'appliance_category': self.appliance_category,
            'location': self.location_description,
            'detected_at': self.detected_at,
            'power_disparity_w': round(self.power_disparity_w, 2),
            'estimated_waste_power_w': round(self.estimated_waste_power_w, 2),
            'duration_hours': round(self.duration_hours, 1),
            'total_wasted_kwh': round(self.total_wasted_kwh, 2),
            'cost_impact': {
                'daily_inr': round(self.estimated_daily_loss_inr, 2),
                'monthly_inr': round(self.estimated_monthly_loss_inr, 2),
                'annual_inr': round(self.estimated_annual_loss_inr, 0),
            },
            'explainability': {
                'occupancy_mismatch': self.occupancy_mismatch,
                'time_pattern': self.time_pattern,
                'signal_strength': self.signal_strength,
                'reasoning': self.reasoning_chain,
            },
            'recommended_actions': [
                {
                    'priority': action.priority,
                    'description': action.description,
                    'estimated_cost': action.estimated_cost_inr,
                    'payback_days': action.estimated_payback_days,
                }
                for action in self.actions
            ],
            'confidence': round(self.confidence, 3),
        }
    
    def to_human_readable(self) -> str:
        """Generate human-readable insight text"""
        lines = []
        
        # Title
        severity_emoji = "🔴" if self.risk_level == RiskLevel.CRITICAL else \
                         "🟠" if self.risk_level == RiskLevel.HIGH else \
                         "🟡" if self.risk_level == RiskLevel.MEDIUM else "🟢"
        
        lines.append(f"{severity_emoji} {self.waste_type.value.replace('_', ' ').upper()}")
        lines.append(f"   Location: {self.location_description}")
        lines.append(f"   Severity: {self.risk_level.value.upper()} (Confidence: {self.confidence*100:.0f}%)")
        lines.append("")
        
        # What is happening
        lines.append("📊 What's Happening:")
        lines.append(f"   Device: {self.appliance_category}")
        lines.append(f"   Power disparity: {self.power_disparity_w:.0f}W")
        lines.append(f"   Estimated wasted power: {self.estimated_waste_power_w:.0f}W")
        lines.append(f"   Duration: {self.duration_hours:.1f} hours")
        lines.append("")
        
        # Cost impact
        lines.append("💰 Financial Impact:")
        lines.append(f"   Per day: ₹{self.estimated_daily_loss_inr:,.0f}")
        lines.append(f"   Per month: ₹{self.estimated_monthly_loss_inr:,.0f}")
        lines.append(f"   Per year: ₹{self.estimated_annual_loss_inr:,.0f}")
        lines.append("")
        
        # Why it happened
        lines.append("🔍 Why This Was Flagged:")
        for step in self.reasoning_chain:
            lines.append(f"   • {step}")
        lines.append("")
        
        # Actions
        if self.actions:
            lines.append("✅ Recommended Actions:")
            for i, action in enumerate(self.actions, 1):
                payback = f"{action.estimated_payback_days}d" if action.estimated_payback_days < 365 \
                         else f"{action.estimated_payback_days/365:.1f}y"
                lines.append(f"   {i}. [{action.priority}] {action.description}")
                lines.append(f"      → Investment: ₹{action.estimated_cost_inr:,} | Payback: {payback}")
        
        return "\n".join(lines)


class EnergyWasteReasoningEngine:
    """
    Core reasoning engine that converts ML signals into waste insights.
    
    SIGNAL FLOW:
    Power Disparity Signal + Occupancy Context → Waste Classification → Insight Generation
    """
    
    def __init__(self, cost_per_kwh: float = 8.0, location_id: str = "BLDG01"):
        """
        Args:
            cost_per_kwh: Electricity tariff in ₹/kWh (default: ₹8 per Indian commercial rate)
            location_id: Building or facility identifier
        """
        self.cost_per_kwh = cost_per_kwh
        self.location_id = location_id
    
    def analyze(
        self,
        signal: PowerDisparitySignal,
        context: OccupancyContext,
        appliance_category: str,
        location_description: str = "",
        duration_hours: float = 1.0,
    ) -> EnergyWasteInsight:
        """
        Main analysis function: Convert signal + context → waste insight.
        
        Args:
            signal: ML power disparity prediction
            context: Occupancy and time information
            appliance_category: Type of appliance (e.g., "lighting", "hvac", "server")
            location_description: Human-readable location (e.g., "Office Zone A")
            duration_hours: How long has this been going on
            
        Returns:
            EnergyWasteInsight with waste type, cost impact, and recommendations
        """
        
        # Step 1: Classify waste type based on signal + context
        waste_type, occupancy_mismatch = self._classify_waste_type(
            signal, context
        )
        
        # Step 2: Determine severity
        risk_level = self._determine_risk_level(
            signal, waste_type, appliance_category
        )
        
        # Step 3: Calculate cost impact
        estimated_waste_power = self._estimate_waste_power(
            signal, waste_type, context
        )
        
        daily_loss, monthly_loss, annual_loss = self._calculate_cost_impact(
            estimated_waste_power, duration_hours
        )
        
        # Step 4: Generate explainability chain
        reasoning_chain = self._build_reasoning_chain(
            signal, context, waste_type, occupancy_mismatch
        )
        
        # Step 5: Generate recommendations
        actions = self._generate_recommendations(
            waste_type, appliance_category, annual_loss, risk_level
        )
        
        # Step 6: Determine signal strength
        signal_strength = self._assess_signal_strength(signal)
        
        # Step 7: Determine time pattern
        time_pattern = self._classify_time_pattern(context, occupancy_mismatch)
        
        # Step 8: Calculate overall confidence
        confidence = self._calculate_confidence(
            signal, context, waste_type, risk_level
        )
        
        # Create insight
        insight = EnergyWasteInsight(
            waste_type=waste_type,
            risk_level=risk_level,
            appliance_category=appliance_category,
            location_description=location_description or f"{self.location_id}/Unknown",
            detected_at=datetime.now().isoformat(),
            power_disparity_w=signal.predicted_power_w,
            estimated_waste_power_w=estimated_waste_power,
            duration_hours=duration_hours,
            total_wasted_kwh=(estimated_waste_power / 1000.0) * duration_hours,
            cost_per_kwh=self.cost_per_kwh,
            estimated_daily_loss_inr=daily_loss,
            estimated_monthly_loss_inr=monthly_loss,
            estimated_annual_loss_inr=annual_loss,
            occupancy_mismatch=occupancy_mismatch,
            time_pattern=time_pattern,
            signal_strength=signal_strength,
            reasoning_chain=reasoning_chain,
            actions=actions,
            confidence=confidence,
        )
        
        return insight
    
    def _classify_waste_type(
        self,
        signal: PowerDisparitySignal,
        context: OccupancyContext
    ) -> Tuple[WasteType, bool]:
        """
        Classify waste type using signal + context.
        
        DECISION TREE:
        IF high_disparity AND unoccupied
          → PHANTOM_LOAD
        ELSE IF high_disparity AND after_occupancy_hours
          → POST_OCCUPANCY
        ELSE IF medium_disparity AND occupied_hours
          → INEFFICIENT_USAGE
        ELSE
          → NORMAL
        """
        high_disparity = signal.predicted_power_w > 500  # Threshold: >500W deviation
        medium_disparity = signal.predicted_power_w > 200
        occupancy_mismatch = False
        
        # Rule 1: Unoccupied + high disparity = Phantom load
        if context.occupancy_status == OccupancyStatus.UNOCCUPIED and high_disparity:
            return WasteType.PHANTOM_LOAD, True
        
        # Rule 2: After occupancy hours + high disparity = Post-occupancy
        if (context.hour > 18 or context.hour < 6) and context.occupancy_status == OccupancyStatus.UNOCCUPIED and medium_disparity:
            occupancy_mismatch = True
            return WasteType.POST_OCCUPANCY, occupancy_mismatch
        
        # Rule 3: During occupancy + medium disparity = Inefficient usage
        if context.occupancy_status == OccupancyStatus.OCCUPIED and medium_disparity:
            return WasteType.INEFFICIENT_USAGE, False
        
        # Default: Normal behavior
        return WasteType.NORMAL, False
    
    def _determine_risk_level(
        self,
        signal: PowerDisparitySignal,
        waste_type: WasteType,
        appliance_category: str
    ) -> RiskLevel:
        """Determine severity based on signal and waste type"""
        
        if waste_type == WasteType.NORMAL:
            return RiskLevel.LOW
        
        # Higher power disparity = higher risk
        if signal.predicted_power_w > 1000:
            return RiskLevel.CRITICAL
        elif signal.predicted_power_w > 500:
            return RiskLevel.HIGH
        elif signal.predicted_power_w > 200:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _estimate_waste_power(
        self,
        signal: PowerDisparitySignal,
        waste_type: WasteType,
        context: OccupancyContext
    ) -> float:
        """Estimate actual wasted power in watts"""
        
        if waste_type == WasteType.NORMAL:
            return 0.0
        
        # ML signal is power disparity - use as waste estimate
        # Add 20% margin for night-time phantom loads (more severe)
        waste_power = signal.predicted_power_w
        
        if context.is_night_hours and waste_type == WasteType.PHANTOM_LOAD:
            waste_power *= 1.2  # 20% higher severity at night
        
        return waste_power
    
    def _calculate_cost_impact(
        self,
        waste_power_w: float,
        duration_hours: float
    ) -> Tuple[float, float, float]:
        """Calculate financial impact in ₹"""
        
        # Convert watts to kilowatts
        waste_power_kw = waste_power_w / 1000.0
        
        # Energy consumed
        daily_kwh = waste_power_kw * 24  # Full day extrapolation
        
        # Cost
        daily_cost = daily_kwh * self.cost_per_kwh
        monthly_cost = daily_cost * 30
        annual_cost = daily_cost * 365
        
        return daily_cost, monthly_cost, annual_cost
    
    def _build_reasoning_chain(
        self,
        signal: PowerDisparitySignal,
        context: OccupancyContext,
        waste_type: WasteType,
        occupancy_mismatch: bool
    ) -> List[str]:
        """Build explainability chain - why was this flagged"""
        
        chain = []
        
        # Signal strength
        chain.append(f"ML detected {signal.predicted_power_w:.0f}W power deviation (confidence: {signal.confidence*100:.0f}%)")
        
        # Context
        if context.occupancy_status == OccupancyStatus.UNOCCUPIED:
            chain.append("Building is unoccupied at this time")
        else:
            chain.append("Building is occupied")
        
        if context.is_night_hours:
            chain.append("This occurs during off-hours (10 PM - 6 AM)")
        elif context.is_working_hours:
            chain.append("This occurs during working hours (9 AM - 6 PM)")
        
        # Waste classification
        if waste_type == WasteType.PHANTOM_LOAD:
            chain.append(f"High power consumption during unoccupancy = Phantom load (24/7 waste)")
        elif waste_type == WasteType.POST_OCCUPANCY:
            chain.append(f"Equipment continues running after occupancy ends = Post-occupancy waste")
        elif waste_type == WasteType.INEFFICIENT_USAGE:
            chain.append(f"Unusual power variance during occupancy = Inefficient usage pattern")
        
        # Financial impact
        chain.append("This translates to continuous financial loss")
        
        return chain
    
    def _generate_recommendations(
        self,
        waste_type: WasteType,
        appliance_category: str,
        annual_cost_inr: float,
        risk_level: RiskLevel
    ) -> List[ActionItem]:
        """Generate ranked corrective actions"""
        
        actions = []
        
        if waste_type == WasteType.PHANTOM_LOAD:
            # Phantom load recommendations
            actions.append(ActionItem(
                priority="CRITICAL",
                description=f"Install smart power strip or occupancy-based disconnect for {appliance_category}",
                estimated_cost_inr=3000,
                estimated_payback_days=int(3000 / (annual_cost_inr / 365)) if annual_cost_inr > 0 else 30,
                confidence=0.95
            ))
            
            actions.append(ActionItem(
                priority="HIGH",
                description=f"Enable sleep/idle mode on {appliance_category} with 15-min shutdown timer",
                estimated_cost_inr=0,  # Software configuration
                estimated_payback_days=0,
                confidence=0.90
            ))
            
            actions.append(ActionItem(
                priority="MEDIUM",
                description="Enable building SCADA to monitor phantom loads in real-time",
                estimated_cost_inr=15000,
                estimated_payback_days=int(15000 / (annual_cost_inr / 365)) if annual_cost_inr > 0 else 90,
                confidence=0.80
            ))
        
        elif waste_type == WasteType.POST_OCCUPANCY:
            actions.append(ActionItem(
                priority="HIGH",
                description=f"Install occupancy sensor-based auto-shutoff for {appliance_category} (15-min delay)",
                estimated_cost_inr=2500,
                estimated_payback_days=int(2500 / (annual_cost_inr / 365)) if annual_cost_inr > 0 else 30,
                confidence=0.92
            ))
            
            actions.append(ActionItem(
                priority="MEDIUM",
                description="Train staff on manual shutdown protocols after occupancy ends",
                estimated_cost_inr=1000,
                estimated_payback_days=10,
                confidence=0.85
            ))
            
            actions.append(ActionItem(
                priority="LOW",
                description="Install LED retrofit + daylight harvesting in the zone",
                estimated_cost_inr=8000,
                estimated_payback_days=int(8000 / (annual_cost_inr / 365)) if annual_cost_inr > 0 else 120,
                confidence=0.75
            ))
        
        elif waste_type == WasteType.INEFFICIENT_USAGE:
            actions.append(ActionItem(
                priority="HIGH",
                description=f"Optimize {appliance_category} operating schedule and setpoints",
                estimated_cost_inr=2000,
                estimated_payback_days=int(2000 / (annual_cost_inr / 365)) if annual_cost_inr > 0 else 45,
                confidence=0.88
            ))
            
            actions.append(ActionItem(
                priority="MEDIUM",
                description="Conduct energy audit to identify inefficiency root cause",
                estimated_cost_inr=5000,
                estimated_payback_days=15,
                confidence=0.80
            ))
        
        # Filter out only the top 3 most relevant
        return sorted(actions, key=lambda x: x.priority == "CRITICAL", reverse=True)[:3]
    
    def _assess_signal_strength(self, signal: PowerDisparitySignal) -> str:
        """Classify ML signal strength"""
        
        if signal.predicted_power_w < 100 or signal.confidence < 0.6:
            return "weak"
        elif signal.predicted_power_w < 500 or signal.confidence < 0.85:
            return "moderate"
        else:
            return "strong"
    
    def _classify_time_pattern(
        self,
        context: OccupancyContext,
        occupancy_mismatch: bool
    ) -> str:
        """Classify temporal pattern of waste"""
        
        if context.is_night_hours:
            return "night_hours"
        elif context.is_working_hours:
            return "working_hours"
        elif occupancy_mismatch:
            return "after_occupancy"
        else:
            return "unknown"
    
    def _calculate_confidence(
        self,
        signal: PowerDisparitySignal,
        context: OccupancyContext,
        waste_type: WasteType,
        risk_level: RiskLevel
    ) -> float:
        """Calculate overall confidence in the waste diagnosis"""
        
        if waste_type == WasteType.NORMAL:
            return 1.0  # Very confident in "normal" classification
        
        # Start with ML model confidence
        confidence = signal.confidence * 0.6  # 60% weight on ML
        
        # Add occupancy context confidence
        if context.occupancy_status != OccupancyStatus.UNKNOWN:
            confidence += context.occupancy_confidence * 0.3  # 30% weight on occupancy
        
        # Add risk severity bonus
        if risk_level == RiskLevel.CRITICAL:
            confidence += 0.1  # High severity adds conviction
        elif risk_level == RiskLevel.LOW:
            confidence -= 0.1  # Low severity reduces conviction
        
        return min(1.0, max(0.0, confidence))


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    
    engine = EnergyWasteReasoningEngine(cost_per_kwh=8.0, location_id="OFFICE_BLDG_01")
    
    # Test Case 1: Phantom Load (Server running 24/7 in unoccupied zone)
    print("\n" + "="*80)
    print("TEST CASE 1: PHANTOM LOAD DETECTION")
    print("="*80)
    
    signal1 = PowerDisparitySignal(
        predicted_power_w=2800,
        confidence=0.95,
        baseline_power_w=0,
        actual_power_w=2800,
        variance_percent=300
    )
    
    context1 = OccupancyContext(
        occupancy_status=OccupancyStatus.UNOCCUPIED,
        occupancy_confidence=0.98,
        hour=2,
        day_of_week=3,
        is_weekend=False,
        season="winter"
    )
    
    insight1 = engine.analyze(
        signal=signal1,
        context=context1,
        appliance_category="Server Room",
        location_description="Server Room - Floor 4",
        duration_hours=8.0
    )
    
    print(insight1.to_human_readable())
    print("\nJSON Output:", json.dumps(insight1.to_dict(), indent=2, ensure_ascii=False))
    
    # Test Case 2: Inefficient Usage (HVAC running high during occupancy)
    print("\n" + "="*80)
    print("TEST CASE 2: INEFFICIENT USAGE DETECTION")
    print("="*80)
    
    signal2 = PowerDisparitySignal(
        predicted_power_w=450,
        confidence=0.88,
        baseline_power_w=300,
        actual_power_w=700,
        variance_percent=133
    )
    
    context2 = OccupancyContext(
        occupancy_status=OccupancyStatus.OCCUPIED,
        occupancy_confidence=0.92,
        hour=14,
        day_of_week=2,
        is_weekend=False,
        season="summer"
    )
    
    insight2 = engine.analyze(
        signal=signal2,
        context=context2,
        appliance_category="HVAC System",
        location_description="Office Zone A - Floor 2",
        duration_hours=6.0
    )
    
    print(insight2.to_human_readable())
    print("\nJSON Output:", json.dumps(insight2.to_dict(), indent=2, ensure_ascii=False))
    
    # Test Case 3: Normal Operation (Low variance during occupancy)
    print("\n" + "="*80)
    print("TEST CASE 3: NORMAL OPERATION (No Waste)")
    print("="*80)
    
    signal3 = PowerDisparitySignal(
        predicted_power_w=80,
        confidence=0.92,
        baseline_power_w=300,
        actual_power_w=320,
        variance_percent=6.7
    )
    
    context3 = OccupancyContext(
        occupancy_status=OccupancyStatus.OCCUPIED,
        occupancy_confidence=0.95,
        hour=11,
        day_of_week=1,
        is_weekend=False,
        season="spring"
    )
    
    insight3 = engine.analyze(
        signal=signal3,
        context=context3,
        appliance_category="Office Lighting",
        location_description="Conference Room B - Floor 1",
        duration_hours=3.0
    )
    
    print(insight3.to_human_readable())
    print("\nJSON Output:", json.dumps(insight3.to_dict(), indent=2, ensure_ascii=False))
