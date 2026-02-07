import React, { useState } from 'react'
import { WasteAnalysisInput, WasteAnalysisOutput } from '../types'
import { API_BASE_URL } from '../constants'
import '../styles/prediction-form.css'

export default function PredictionForm(){
  const [input, setInput] = useState<WasteAnalysisInput>({
    hour: 14,
    day_of_week: 3,
    appliance_id: 'fridge_207',
    appliance_category: 'kitchen',
    is_weekend: 0,
    month: 6,
    season: 'summer',
    power_max: 2500,
    occupancy_status: 'occupied',
    occupancy_confidence: 0.9,
    location_description: 'Office Zone A',
    duration_hours: 1
  })
  
  const [result, setResult] = useState<WasteAnalysisOutput | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showExplanation, setShowExplanation] = useState(false)

  async function submit(e:React.FormEvent){
    e.preventDefault()
    setLoading(true)
    setError(null)
    
    try{
      const res = await fetch(`${API_BASE_URL}/analyze-waste`, {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify(input)
      })
      
      if (!res.ok) {
        throw new Error(`API error: ${res.statusText}`)
      }
      
      const data = await res.json()
      setResult(data)
      setShowExplanation(false)
    } catch(err: any){
      console.error(err)
      setError(err.message || 'Failed to analyze waste')
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (level: string) => {
    switch(level) {
      case 'critical': return '#c41e3a'
      case 'high': return '#ff6600'
      case 'medium': return '#ffcc00'
      case 'low': return '#00cc00'
      default: return '#666'
    }
  }

  const getWasteEmoji = (type: string) => {
    switch(type) {
      case 'phantom_load': return '👻'
      case 'post_occupancy': return '⏰'
      case 'inefficient_usage': return '⚙️'
      case 'normal': return '✅'
      default: return '❓'
    }
  }

  return (
    <div className='prediction-form-container'>
      <form onSubmit={submit} className='prediction-form'>
        <div className='form-grid'>
          {/* Appliance Information */}
          <fieldset className='form-section'>
            <legend>📱 Appliance Information</legend>
            
            <label>
              Appliance ID:
              <input
                type="text"
                value={input.appliance_id}
                onChange={e => setInput({...input, appliance_id: e.target.value})}
                placeholder="e.g., fridge_207"
              />
            </label>
            
            <label>
              Category:
              <select
                value={input.appliance_category || ''}
                onChange={e => setInput({...input, appliance_category: e.target.value})}
              >
                <option value='kitchen'>Kitchen</option>
                <option value='hvac'>HVAC</option>
                <option value='server'>Server</option>
                <option value='lighting'>Lighting</option>
                <option value='other'>Other</option>
              </select>
            </label>
            
            <label>
              Location:
              <input
                type="text"
                value={input.location_description || ''}
                onChange={e => setInput({...input, location_description: e.target.value})}
                placeholder="e.g., Office Zone A"
              />
            </label>
          </fieldset>

          {/* Time Context */}
          <fieldset className='form-section'>
            <legend>🕐 Time Context</legend>
            
            <label>
              Hour (0-23):
              <input
                type="number"
                min="0"
                max="23"
                value={input.hour}
                onChange={e => setInput({...input, hour: Number(e.target.value)})}
              />
            </label>
            
            <label>
              Day of Week (0=Mon, 6=Sun):
              <input
                type="number"
                min="0"
                max="6"
                value={input.day_of_week}
                onChange={e => setInput({...input, day_of_week: Number(e.target.value)})}
              />
            </label>
            
            <label>
              <input
                type="checkbox"
                checked={Boolean(input.is_weekend)}
                onChange={e => setInput({...input, is_weekend: e.target.checked ? 1 : 0})}
              />
              Is Weekend
            </label>
            
            <label>
              Month (1-12):
              <input
                type="number"
                min="1"
                max="12"
                value={input.month}
                onChange={e => setInput({...input, month: Number(e.target.value)})}
              />
            </label>
            
            <label>
              Season:
              <select
                value={input.season || 'unknown'}
                onChange={e => setInput({...input, season: e.target.value})}
              >
                <option value='winter'>Winter</option>
                <option value='spring'>Spring</option>
                <option value='summer'>Summer</option>
                <option value='fall'>Fall</option>
                <option value='unknown'>Unknown</option>
              </select>
            </label>
          </fieldset>

          {/* Power Metrics */}
          <fieldset className='form-section'>
            <legend>⚡ Power Metrics</legend>
            
            <label>
              Max Power (W):
              <input
                type="number"
                step="100"
                value={input.power_max}
                onChange={e => setInput({...input, power_max: Number(e.target.value)})}
              />
            </label>
            
            <label>
              Baseline Power (W):
              <input
                type="number"
                step="100"
                value={input.baseline_power_w || 0}
                onChange={e => setInput({...input, baseline_power_w: Number(e.target.value)})}
              />
            </label>
            
            <label>
              Actual Power (W):
              <input
                type="number"
                step="100"
                value={input.actual_power_w || ''}
                onChange={e => setInput({...input, actual_power_w: e.target.value ? Number(e.target.value) : undefined})}
              />
            </label>
          </fieldset>

          {/* Occupancy */}
          <fieldset className='form-section'>
            <legend>👥 Occupancy Context</legend>
            
            <label>
              Occupancy Status:
              <select
                value={input.occupancy_status || 'unknown'}
                onChange={e => setInput({...input, occupancy_status: e.target.value})}
              >
                <option value='occupied'>Occupied</option>
                <option value='unoccupied'>Unoccupied</option>
                <option value='unknown'>Unknown</option>
              </select>
            </label>
            
            <label>
              Confidence (0-1):
              <input
                type="number"
                min="0"
                max="1"
                step="0.1"
                value={input.occupancy_confidence || 0.5}
                onChange={e => setInput({...input, occupancy_confidence: Number(e.target.value)})}
              />
            </label>
            
            <label>
              Duration (hours):
              <input
                type="number"
                min="0.1"
                step="0.5"
                value={input.duration_hours || 1}
                onChange={e => setInput({...input, duration_hours: Number(e.target.value)})}
              />
            </label>
          </fieldset>
        </div>

        <button type="submit" disabled={loading} className='submit-btn'>
          {loading ? '🔄 Analyzing...' : '🔍 Analyze Energy Waste'}
        </button>
      </form>

      {error && (
        <div className='error-message'>❌ {error}</div>
      )}

      {result && (
        <div className='result-container'>
          <div className='result-header' style={{borderColor: getRiskColor(result.risk_level)}}>
            <h3>
              {getWasteEmoji(result.waste_type)} {result.waste_type.replace('_', ' ').toUpperCase()}
            </h3>
            <span
              className='risk-badge'
              style={{backgroundColor: getRiskColor(result.risk_level)}}
            >
              {result.risk_level.toUpperCase()} • {(result.confidence * 100).toFixed(0)}% confident
            </span>
          </div>

          {/* Summary */}
          <div className='result-section'>
            <h4>📊 Summary</h4>
            <div className='summary-grid'>
              <div className='summary-card'>
                <div className='label'>Waste Type</div>
                <div className='value'>{result.waste_type.replace('_', ' ')}</div>
              </div>
              <div className='summary-card'>
                <div className='label'>Location</div>
                <div className='value'>{result.location}</div>
              </div>
              <div className='summary-card'>
                <div className='label'>Power Disparity</div>
                <div className='value'>{result.power_disparity_w.toFixed(0)}W</div>
              </div>
              <div className='summary-card'>
                <div className='label'>Estimated Waste</div>
                <div className='value'>{result.estimated_waste_power_w.toFixed(0)}W</div>
              </div>
            </div>
          </div>

          {/* Cost Impact */}
          <div className='result-section'>
            <h4>💰 Financial Impact</h4>
            <div className='cost-impact'>
              <div className='cost-item'>
                <span className='cost-label'>Daily Loss:</span>
                <span className='cost-value'>₹{result.cost_impact.daily_inr.toLocaleString('en-IN', {maximumFractionDigits: 0})}</span>
              </div>
              <div className='cost-item'>
                <span className='cost-label'>Monthly Loss:</span>
                <span className='cost-value'>₹{result.cost_impact.monthly_inr.toLocaleString('en-IN', {maximumFractionDigits: 0})}</span>
              </div>
              <div className='cost-item' style={{fontSize: '1.2em', fontWeight: 'bold'}}>
                <span className='cost-label'>Annual Loss:</span>
                <span className='cost-value'>₹{result.cost_impact.annual_inr.toLocaleString('en-IN', {maximumFractionDigits: 0})}</span>
              </div>
            </div>
          </div>

          {/* Explainability */}
          <div className='result-section'>
            <button
              type='button'
              className='toggle-btn'
              onClick={() => setShowExplanation(!showExplanation)}
            >
              {showExplanation ? '▼' : '▶'} 🔍 Why This Was Flagged
            </button>
            {showExplanation && (
              <div className='explanation'>
                <ul>
                  {result.explainability.reasoning.map((reason, idx) => (
                    <li key={idx}>{reason}</li>
                  ))}
                </ul>
                <p className='signal-strength'>
                  <strong>Signal Strength:</strong> {result.explainability.signal_strength}
                  {result.explainability.occupancy_mismatch && ' | ⚠️ Occupancy Mismatch Detected'}
                </p>
              </div>
            )}
          </div>

          {/* Recommendations */}
          {result.recommended_actions.length > 0 && (
            <div className='result-section'>
              <h4>✅ Recommended Actions</h4>
              <div className='actions-list'>
                {result.recommended_actions.map((action, idx) => (
                  <div key={idx} className='action-item'>
                    <div className='action-header'>
                      <span className='action-priority'>[{action.priority}]</span>
                      <span className='action-desc'>{action.description}</span>
                    </div>
                    <div className='action-details'>
                      <span>💵 Cost: ₹{action.estimated_cost.toLocaleString('en-IN')}</span>
                      <span>📅 Payback: {action.payback_days} days</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.waste_type === 'normal' && (
            <div className='result-section success'>
              <h4>✨ Good News!</h4>
              <p>No significant energy waste detected. Your appliance is operating normally.</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
