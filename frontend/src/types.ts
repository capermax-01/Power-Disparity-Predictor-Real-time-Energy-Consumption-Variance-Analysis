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
