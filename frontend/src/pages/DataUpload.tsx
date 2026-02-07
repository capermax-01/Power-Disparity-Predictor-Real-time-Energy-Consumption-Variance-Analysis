import React, { useState } from 'react'
import { API_BASE_URL } from '../constants'
import '../styles/upload.css'

interface IngestionSummary {
  total_records: number
  valid_records: number
  invalid_records: number
  validity_percent: number
  data_gaps?: any[]
  quality_issues?: any
}

interface WasteIssue {
  title: string
  location: string
  device: string
  time_period: string
  extra_energy_kwh: number
  cost_per_day: number
  action: string
  reason: string
  severity: string
}

interface EnergyAnalysis {
  summary: {
    total_energy_kwh: number
    energy_wasted_kwh: number
    money_lost_today: number
    monthly_savings_potential: number
    efficiency_score: number
  }
  issues: WasteIssue[]
  cost_savings: {
    daily_loss: number
    monthly_loss: number
    yearly_loss: number
  }
  automation_suggestions: string[]
  conclusion: string
}

interface UploadResult {
  file: string
  status: string
  ingestion_summary: IngestionSummary
  energy_analysis: EnergyAnalysis
}

export default function DataUpload(){
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<UploadResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError(null)
    }
  }

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) {
      setError('Please select a file')
      return
    }

    try {
      setUploading(true)
      setError(null)

      const formData = new FormData()
      formData.append('file', file)

      const res = await fetch(`${API_BASE_URL}/upload-csv`, {
        method: 'POST',
        body: formData
      })

      const data = await res.json()
      
      if (!res.ok) {
        const errorMsg = data.detail || res.statusText
        throw new Error(Array.isArray(errorMsg) ? errorMsg[0]?.msg : errorMsg)
      }

      setResult(data)
      setFile(null)
    } catch (err: any) {
      setError(err.message || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className='upload-container'>
      <div className='upload-card'>
        <h2>📤 Upload Smart Meter Data</h2>
        <p className='upload-subtitle'>
          Upload CSV files with building energy consumption data for pattern analysis
        </p>

        <div className='upload-info'>
          <h3>Required CSV Columns:</h3>
          <ul className='columns-list'>
            <li><strong>timestamp</strong> - ISO format (2025-02-07T14:30:00)</li>
            <li><strong>device_id</strong> - Unique device identifier</li>
            <li><strong>device_category</strong> - Type of device (hvac, lighting, etc.)</li>
            <li><strong>power_w</strong> - Power consumption in watts</li>
            <li><strong>occupancy_status</strong> - occupied, unoccupied, or unknown (optional)</li>
            <li><strong>location_floor</strong> - Building floor (optional)</li>
            <li><strong>location_zone</strong> - Zone/area identifier (optional)</li>
          </ul>
        </div>

        <form onSubmit={handleUpload} className='upload-form'>
          <div className='file-input-wrapper'>
            <input
              type='file'
              accept='.csv'
              onChange={handleFileChange}
              disabled={uploading}
              className='file-input'
              id='csv-file'
            />
            <label htmlFor='csv-file' className='file-label'>
              {file ? `📄 ${file.name}` : '📁 Choose CSV File'}
            </label>
          </div>

          <button
            type='submit'
            disabled={uploading || !file}
            className='upload-button'
          >
            {uploading ? 'Uploading...' : 'Upload Data'}
          </button>
        </form>

        {error && (
          <div className='error-message'>
            ❌ {error}
          </div>
        )}

        {result && result.energy_analysis && (
          <div className='analysis-report'>
            {/* Summary Section */}
            <div className='report-header'>
              <h2>🔹 Energy Analysis Report</h2>
              <p className='report-subtitle'>AI-Powered Waste Detection & Cost Analysis</p>
            </div>

            {/* Key Metrics */}
            <div className='metrics-grid'>
              <div className='metric-card'>
                <div className='metric-label'>Total Energy Used</div>
                <div className='metric-value'>{result.energy_analysis.summary.total_energy_kwh} kWh</div>
              </div>
              <div className='metric-card waste'>
                <div className='metric-label'>Energy Wasted</div>
                <div className='metric-value'>{result.energy_analysis.summary.energy_wasted_kwh} kWh</div>
              </div>
              <div className='metric-card cost'>
                <div className='metric-label'>Money Lost Today</div>
                <div className='metric-value'>₹{result.energy_analysis.summary.money_lost_today}</div>
              </div>
              <div className='metric-card savings'>
                <div className='metric-label'>Monthly Savings Potential</div>
                <div className='metric-value'>₹{result.energy_analysis.summary.monthly_savings_potential}</div>
              </div>
            </div>

            {/* Efficiency Score */}
            <div className='efficiency-section'>
              <h3>Efficiency Score</h3>
              <div className='efficiency-bar-container'>
                <div 
                  className='efficiency-bar' 
                  style={{
                    width: `${result.energy_analysis.summary.efficiency_score}%`,
                    backgroundColor: result.energy_analysis.summary.efficiency_score >= 80 ? '#4caf50' : 
                                   result.energy_analysis.summary.efficiency_score >= 60 ? '#ff9800' : '#f44336'
                  }}
                >
                  <span className='efficiency-text'>{result.energy_analysis.summary.efficiency_score}%</span>
                </div>
              </div>
            </div>

            {/* Issues Found */}
            {result.energy_analysis.issues.length > 0 && (
              <div className='issues-section'>
                <h3>🔴 Main Issues Found</h3>
                {result.energy_analysis.issues.map((issue, idx) => (
                  <div key={idx} className={`issue-card severity-${issue.severity}`}>
                    <div className='issue-header'>
                      <h4>{issue.title}</h4>
                      <span className={`severity-badge ${issue.severity}`}>
                        {issue.severity.toUpperCase()}
                      </span>
                    </div>
                    
                    <div className='issue-details'>
                      <div className='issue-row'>
                        <span className='label'>📍 Where:</span>
                        <span>{issue.location}</span>
                      </div>
                      <div className='issue-row'>
                        <span className='label'>🔌 Device:</span>
                        <span>{issue.device}</span>
                      </div>
                      <div className='issue-row'>
                        <span className='label'>⏰ Time:</span>
                        <span>{issue.time_period}</span>
                      </div>
                      <div className='issue-row'>
                        <span className='label'>⚡ Extra Energy:</span>
                        <span>{issue.extra_energy_kwh} kWh</span>
                      </div>
                      <div className='issue-row cost-highlight'>
                        <span className='label'>💰 Cost per Day:</span>
                        <span className='cost-value'>₹{issue.cost_per_day}</span>
                      </div>
                    </div>

                    <div className='issue-reason'>
                      <strong>🧠 Why This Was Flagged:</strong>
                      <p>{issue.reason}</p>
                    </div>

                    <div className='issue-action'>
                      <strong>✅ What to Do:</strong>
                      <p>{issue.action}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {result.energy_analysis.issues.length === 0 && (
              <div className='no-issues'>
                <h3>✅ Great News!</h3>
                <p>No significant energy waste detected. Your system is operating efficiently.</p>
              </div>
            )}

            {/* Cost Breakdown */}
            <div className='cost-section'>
              <h3>💰 Cost & Savings</h3>
              <div className='cost-grid'>
                <div className='cost-item'>
                  <span className='cost-label'>Daily Loss:</span>
                  <span className='cost-amount'>₹{result.energy_analysis.cost_savings.daily_loss}</span>
                </div>
                <div className='cost-item'>
                  <span className='cost-label'>Monthly Loss:</span>
                  <span className='cost-amount'>₹{result.energy_analysis.cost_savings.monthly_loss}</span>
                </div>
                <div className='cost-item highlight'>
                  <span className='cost-label'>Yearly Estimate:</span>
                  <span className='cost-amount'>₹{result.energy_analysis.cost_savings.yearly_loss}</span>
                </div>
              </div>
            </div>

            {/* Automation Suggestions */}
            {result.energy_analysis.automation_suggestions.length > 0 && (
              <div className='automation-section'>
                <h3>🤖 Suggested Automation</h3>
                <ul className='automation-list'>
                  {result.energy_analysis.automation_suggestions.map((rule, idx) => (
                    <li key={idx}>{rule}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Conclusion */}
            <div className='conclusion-section'>
              <h3>🧾 Summary</h3>
              <p className='conclusion-text'>{result.energy_analysis.conclusion}</p>
            </div>

            {/* Ingestion Details (Collapsible) */}
            <details className='ingestion-details'>
              <summary>📊 Data Ingestion Details</summary>
              <div className='ingestion-content'>
                <div className='ingestion-row'>
                  <span>Total Records:</span>
                  <span>{result.ingestion_summary.total_records}</span>
                </div>
                <div className='ingestion-row'>
                  <span>Valid Records:</span>
                  <span className='valid'>{result.ingestion_summary.valid_records}</span>
                </div>
                <div className='ingestion-row'>
                  <span>Invalid Records:</span>
                  <span>{result.ingestion_summary.invalid_records}</span>
                </div>
                <div className='ingestion-row'>
                  <span>Data Quality:</span>
                  <span>{result.ingestion_summary.validity_percent}%</span>
                </div>
              </div>
            </details>
          </div>
        )}

        <div className='sample-csv'>
          <h3>📋 Sample CSV Format:</h3>
          <pre className='csv-sample'>{`timestamp,device_id,device_category,power_w,occupancy_status,location_floor,location_zone
2025-02-07T14:30:00,hvac_101,hvac,3500.0,occupied,Floor 3,Zone A
2025-02-07T14:30:00,lighting_102,lighting,2000.0,occupied,Floor 3,Zone A
2025-02-07T15:30:00,hvac_101,hvac,3500.0,occupied,Floor 3,Zone A
2025-02-07T23:00:00,hvac_101,hvac,1200.0,unoccupied,Floor 3,Zone A`}</pre>
        </div>

        <div className='upload-benefits'>
          <h3>🎯 After Upload, The System Will:</h3>
          <ul className='benefits-list'>
            <li>✓ Establish energy baselines for each device</li>
            <li>✓ Detect phantom loads and post-occupancy waste</li>
            <li>✓ Identify anomalies and unusual patterns</li>
            <li>✓ Generate prioritized alerts ranking by cost impact</li>
            <li>✓ Suggest specific, actionable recommendations</li>
            <li>✓ Calculate ROI and payback periods</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
