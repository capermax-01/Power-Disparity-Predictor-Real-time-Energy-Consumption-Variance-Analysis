import React from 'react'
import PredictionForm from '../components/PredictionForm'
import '../styles/predictor.css'

export default function Predictor(){
  return (
    <div className='predictor-container'>
      <h2>Energy Waste Analysis</h2>
      <p className='intro-text'>
        Analyze appliances for invisible energy waste using AI-powered reasoning.
        The system detects phantom loads, post-occupancy waste, and inefficient usage patterns.
      </p>
      
      {/* Information Section */}
      <div className='info-section'>
        <div className='demo-notice'>
          <h3>ℹ️ About This Demo</h3>
          <p>
            <strong>Current Mode:</strong> Manual input for demonstration
          </p>
          <p>
            The inputs below simulate data from smart meters and IoT occupancy sensors. 
            In real-world deployments, the same AI reasoning engine can consume automated data streams from:
          </p>
          <ul>
            <li>Smart meters and sub-meters</li>
            <li>Occupancy sensors (PIR, CO₂, calendar APIs)</li>
            <li>SCADA/BMS systems</li>
            <li>IoT device APIs</li>
          </ul>
          <p className='key-point'>
            <strong>Key Point:</strong> The AI reasoning engine is data-source agnostic. 
            Manual input is a simulation layer for demonstration; automation is a deployment choice.
          </p>
        </div>

        <div className='architecture-section'>
          <h3>⚙️ System Architecture</h3>
          <div className='architecture-diagram'>
            <div className='diagram-box'>
              <strong>Data Sources</strong>
              <div className='diagram-note'>(Manual or Automated)</div>
              <div className='arrow'>↓</div>
            </div>
            
            <div className='diagram-box'>
              <strong>Input Normalization</strong>
              <div className='diagram-note'>Power (W), Occupancy, Time Context</div>
              <div className='arrow'>↓</div>
            </div>
            
            <div className='diagram-box highlight'>
              <strong>AI Reasoning Engine</strong>
              <div className='diagram-note'>ML Signal + Context → Waste Decision</div>
              <div className='arrow'>↓</div>
            </div>
            
            <div className='diagram-box'>
              <strong>Actionable Insights</strong>
              <div className='diagram-note'>Waste Type, Cost, Recommendations, Explanation</div>
            </div>
          </div>
          <p className='architecture-note'>
            The reasoning engine doesn't care whether data comes from manual input (demo) or automated sources (production). 
            It processes the same signal, applies the same rules, produces the same insights.
          </p>
        </div>
      </div>

      <h3 style={{marginTop: '40px'}}>Enter Appliance Details</h3>
      <p style={{color: '#666', fontSize: '0.95em'}}>
        Provide appliance and occupancy information. In production, these values would be automatically gathered from smart meters and sensors.
      </p>
      <PredictionForm />
    </div>
  )
}
