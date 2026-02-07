export type PredictionInput = {
  hour: number
  day_of_week: number
  appliance_id: string
  appliance_category?: string
  power_reading?: number
}

export type PredictionResult = {
  predicted_disparity_w: number
  confidence?: number
}

// ============================================================================
// ENERGY WASTE ANALYSIS TYPES
// ============================================================================

export type WasteType = 'phantom_load' | 'post_occupancy' | 'inefficient_usage' | 'normal'
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'
export type OccupancyStatus = 'occupied' | 'unoccupied' | 'unknown'

export type ActionItem = {
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
  description: string
  estimated_cost: number
  payback_days: number
}

export type ExplainabilityDetails = {
  occupancy_mismatch: boolean
  time_pattern: string
  signal_strength: 'weak' | 'moderate' | 'strong'
  reasoning: string[]
}

export type CostImpact = {
  daily_inr: number
  monthly_inr: number
  annual_inr: number
}

export type WasteAnalysisInput = {
  // Appliance information
  appliance_id: string
  appliance_category: string
  location_description?: string
  
  // Time and context
  hour: number
  day_of_week: number
  is_weekend: number
  month: number
  season?: string
  
  // Power readings
  power_max: number
  power_rolling_mean_24?: number
  power_rolling_std_24?: number
  actual_power_w?: number
  baseline_power_w?: number
  
  // Occupancy information
  occupancy_status?: string
  occupancy_confidence?: number
  
  // Duration and tariff
  duration_hours?: number
  cost_per_kwh?: number
}

export type WasteAnalysisOutput = {
  waste_type: WasteType
  risk_level: RiskLevel
  appliance_category: string
  location: string
  detected_at: string
  
  // Power metrics
  power_disparity_w: number
  estimated_waste_power_w: number
  duration_hours: number
  total_wasted_kwh: number
  
  // Cost impact
  cost_impact: CostImpact
  
  // Explainability
  explainability: ExplainabilityDetails
  
  // Recommendations
  recommended_actions: ActionItem[]
  
  // Confidence in diagnosis
  confidence: number
}

