"""
Energy Waste Detection Demo
Demonstrates waste detection on energy_data.csv with real patterns
"""

import pandas as pd
from waste_detection_engine import EnergyWasteDetector
import json

print("\n" + "="*80)
print("ENERGY WASTE DETECTION - COMPREHENSIVE DEMO")
print("="*80)

# Load the actual energy data
print("\n📂 Loading energy_data.csv...")
try:
    df = pd.read_csv('energy_data.csv')
    print(f"✓ Loaded {len(df)} records")
    print(f"✓ Columns: {list(df.columns)}")
    print(f"✓ Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
except Exception as e:
    print(f"✗ Error loading file: {e}")
    import sys
    sys.exit(1)

# Initialize waste detector
print("\n🔍 Initializing Waste Detection Engine...")
detector = EnergyWasteDetector(cost_per_kwh=8.5)
print("✓ Detector ready (cost rate: ₹8.50/kWh)")

# Run multi-pattern detection
print("\n" + "="*80)
print("RUNNING WASTE DETECTION ALGORITHMS")
print("="*80)

print("\n[1/4] Detecting Phantom Loads...")
phantom_alerts = detector.detect_phantom_loads(df)
print(f"✓ Found {len(phantom_alerts)} phantom load patterns")

print("\n[2/4] Detecting Post-Occupancy Waste...")
post_occ_alerts = detector.detect_post_occupancy_waste(df)
print(f"✓ Found {len(post_occ_alerts)} post-occupancy patterns")

print("\n[3/4] Detecting Seasonal Mismatches...")
seasonal_alerts = detector.detect_seasonal_mismatch(df)
print(f"✓ Found {len(seasonal_alerts)} seasonal mismatch patterns")

print("\n[4/4] Detecting Night Mode Violations...")
night_alerts = detector.detect_night_mode_violations(df)
print(f"✓ Found {len(night_alerts)} night mode violations")

# Compile all alerts
all_alerts = phantom_alerts + post_occ_alerts + seasonal_alerts + night_alerts
all_alerts.sort(key=lambda x: x.annual_cost_inr, reverse=True)

# Summary statistics
print("\n" + "="*80)
print("WASTE DETECTION SUMMARY")
print("="*80)

total_annual_loss = sum(a.annual_cost_inr for a in all_alerts)
total_monthly_loss = sum(a.monthly_cost_inr for a in all_alerts)

print(f"\n📊 TOTAL FINDINGS: {len(all_alerts)} waste patterns detected")
print(f"\n💰 FINANCIAL IMPACT:")
print(f"   Total Monthly Loss: ₹{total_monthly_loss:,.0f}")
print(f"   Total Annual Loss:  ₹{total_annual_loss:,.0f}")

# Distribution by severity
severity_counts = {}
for alert in all_alerts:
    severity_counts[alert.severity] = severity_counts.get(alert.severity, 0) + 1

print(f"\n🎯 DISTRIBUTION BY SEVERITY:")
for sev in ['critical', 'high', 'medium', 'low']:
    count = severity_counts.get(sev, 0)
    if count > 0:
        print(f"   {sev.upper()}: {count} patterns")

# Distribution by waste type
type_counts = {}
for alert in all_alerts:
    type_counts[alert.waste_type] = type_counts.get(alert.waste_type, 0) + 1

print(f"\n📈 DISTRIBUTION BY TYPE:")
for wtype in ['phantom_load', 'post_occupancy', 'seasonal_mismatch', 'night_violation']:
    count = type_counts.get(wtype, 0)
    if count > 0:
        print(f"   {wtype.upper()}: {count} patterns")

# Top 3 most costly waste patterns
print("\n" + "="*80)
print("TOP 3 HIGHEST-IMPACT WASTE PATTERNS")
print("="*80)

for i, alert in enumerate(all_alerts[:3], 1):
    print(f"\n{'='*80}")
    print(f"#{i} - {alert.waste_type.upper()} (SEVERITY: {alert.severity.upper()})")
    print(f"{'='*80}")
    print(detector.generate_insight_text(alert))

# Export detailed report
print("\n" + "="*80)
print("EXPORTING DETAILED REPORTS")
print("="*80)

# Export as JSON
json_report = {
    "timestamp": pd.Timestamp.now().isoformat(),
    "total_patterns_detected": len(all_alerts),
    "total_annual_loss_inr": float(total_annual_loss),
    "total_monthly_loss_inr": float(total_monthly_loss),
    "severity_distribution": severity_counts,
    "type_distribution": type_counts,
    "top_10_waste_alerts": [
        alert.__dict__ for alert in all_alerts[:10]
    ]
}

# Fix JSON serialization issues
def fix_json(obj):
    if isinstance(obj, (pd.Timestamp, pd.Timedelta)):
        return str(obj)
    raise TypeError

with open('waste_detection_report.json', 'w') as f:
    json.dump(json_report, f, indent=2, default=str)
print("✓ Saved: waste_detection_report.json")

# Export as CSV
alerts_df = pd.DataFrame([
    {
        'zone_id': a.zone_id,
        'device_type': a.device_type,
        'waste_type': a.waste_type,
        'severity': a.severity,
        'duration_hours': a.duration_hours,
        'waste_power_kw': a.waste_power_kw,
        'waste_energy_kwh': a.waste_energy_kwh,
        'daily_cost_inr': round(a.daily_cost_inr, 2),
        'monthly_cost_inr': round(a.monthly_cost_inr, 2),
        'annual_cost_inr': round(a.annual_cost_inr, 0),
        'confidence': round(a.confidence, 3),
        'reason': a.reason[:80] + '...'
    }
    for a in all_alerts
])

alerts_df.to_csv('waste_detection_alerts.csv', index=False)
print("✓ Saved: waste_detection_alerts.csv")

# Export markdown report
with open('WASTE_DETECTION_DEMO_RESULTS.md', 'w') as f:
    f.write("# 🚨 ENERGY WASTE DETECTION - DEMO RESULTS\n\n")
    f.write(f"**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write(f"## 📊 Executive Summary\n\n")
    f.write(f"- **Total Waste Patterns Detected:** {len(all_alerts)}\n")
    f.write(f"- **Total Monthly Loss:** ₹{total_monthly_loss:,.0f}\n")
    f.write(f"- **Total Annual Loss:** ₹{total_annual_loss:,.0f}\n")
    f.write(f"- **Average Confidence:** {sum(a.confidence for a in all_alerts)/len(all_alerts)*100:.1f}%\n\n")
    
    f.write(f"## 🎯 Severity Distribution\n\n")
    for sev in ['critical', 'high', 'medium', 'low']:
        count = severity_counts.get(sev, 0)
        if count > 0:
            f.write(f"- **{sev.upper()}:** {count} patterns\n")
    
    f.write(f"\n## 📈 Waste Type Distribution\n\n")
    for wtype in ['phantom_load', 'post_occupancy', 'seasonal_mismatch', 'night_violation']:
        count = type_counts.get(wtype, 0)
        if count > 0:
            f.write(f"- **{wtype.upper()}:** {count} patterns\n")
    
    f.write(f"\n## 💰 Top 3 Waste Patterns\n\n")
    for i, alert in enumerate(all_alerts[:3], 1):
        f.write(f"\n### #{i} - {alert.waste_type.upper()} in {alert.zone_id}\n")
        f.write(f"**Severity:** {alert.severity.upper()} | **Confidence:** {alert.confidence*100:.0f}%\n\n")
        f.write(f"**Annual Cost Impact:** ₹{alert.annual_cost_inr:,.0f}\n\n")
        f.write(f"**Reason:** {alert.reason}\n\n")
        f.write(f"**Recommended Actions:**\n")
        for action in alert.recommended_actions:
            f.write(f"- [{action['priority']}] {action['description']}\n")
            f.write(f"  Cost: ₹{action['estimated_cost_inr']:,} | Payback: {action['payback_days']} days\n")

print("✓ Saved: WASTE_DETECTION_DEMO_RESULTS.md")

# Print final statistics
print("\n" + "="*80)
print("DEMO COMPLETE ✅")
print("="*80)
print(f"\nGenerated Files:")
print(f"  1. waste_detection_report.json      - Machine-readable detailed report")
print(f"  2. waste_detection_alerts.csv       - Spreadsheet of all alerts")
print(f"  3. WASTE_DETECTION_DEMO_RESULTS.md  - Human-readable markdown report")
print(f"\nNext Steps:")
print(f"  1. Review waste_detection_alerts.csv in Excel")
print(f"  2. Check WASTE_DETECTION_DEMO_RESULTS.md for detailed insights")
print(f"  3. Implement recommended actions (₹{total_annual_loss:,.0f}/year savings potential)")
print("\n")
