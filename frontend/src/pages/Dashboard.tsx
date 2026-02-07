import React, { useEffect, useState } from 'react'
import { API_BASE_URL } from '../constants'
import '../styles/dashboard.css'

interface Alert {
  alert_id: string
  severity: string
  title: string
  device_id: string
  device_category: string
  cost_impact: {
    daily_inr: number
    monthly_inr: number
    annual_inr: number
  }
  waste_type: string
  location: {
    floor: string
    zone: string
  }
}

interface BuildingReport {
  building_id: string
  report_date: string
  summary: {
    total_alerts: number
    critical: number
    high: number
    open: number
  }
  cost_impact: {
    daily_inr: number
    monthly_inr: number
    annual_inr: number
    potential_savings_annual_inr: number
  }
  top_waste_leaks: Alert[]
  waste_by_category: Record<string, number>
  waste_by_floor: Record<string, number>
  waste_by_type: Record<string, number>
  recommendations: {
    total: number
    approved: number
    projected_payback_months: number
  }
}

export default function Dashboard(){
  const [report, setReport] = useState<BuildingReport | null>(null)
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedFloor, setSelectedFloor] = useState<string | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  // Fetch building report and alerts
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)

        // Fetch building report
        const reportRes = await fetch(`${API_BASE_URL}/building-report?building_id=BUILDING_01`)
        if (!reportRes.ok) throw new Error('Failed to fetch building report')
        const reportData = await reportRes.json()
        setReport(reportData)

        // Fetch all alerts
        let url = `${API_BASE_URL}/alerts?status=open`
        if (selectedFloor) url += `&floor=${selectedFloor}`
        if (selectedCategory) url += `&device_category=${selectedCategory}`

        const alertsRes = await fetch(url)
        if (!alertsRes.ok) throw new Error('Failed to fetch alerts')
        const alertsData = await alertsRes.json()
        setAlerts(alertsData.alerts || [])
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [selectedFloor, selectedCategory])

  const getSeverityColor = (severity: string): string => {
    switch (severity.toLowerCase()) {
      case 'critical': return '#c41e3a'
      case 'high': return '#ff6600'
      case 'medium': return '#ffcc00'
      case 'low': return '#00cc00'
      default: return '#666'
    }
  }

  const getSeverityEmoji = (severity: string): string => {
    switch (severity.toLowerCase()) {
      case 'critical': return '🔴'
      case 'high': return '🟠'
      case 'medium': return '🟡'
      case 'low': return '🟢'
      default: return '⚪'
    }
  }

  const getWasteEmoji = (type: string): string => {
    switch (type) {
      case 'phantom_load': return '👻'
      case 'post_occupancy': return '⏰'
      case 'inefficient_usage': return '⚙️'
      case 'normal': return '✅'
      default: return '❓'
    }
  }

  if (loading) return <div className='dashboard'><p>Loading dashboard...</p></div>
  if (error) return <div className='dashboard error'><p>Error: {error}</p></div>
  if (!report) return <div className='dashboard'><p>No data available</p></div>

  return (
    <div className='dashboard'>
      <h1>🏢 Building Energy Waste Dashboard</h1>
      <p className='dashboard-subtitle'>Insights-First View: See Savings Before Graphs</p>

      {/* KEY METRICS CARDS - INSIGHTS FIRST */}
      <section className='metrics-section'>
        <h2>💰 Financial Impact</h2>
        <div className='metrics-grid'>
          <div className='metric-card critical'>
            <div className='metric-label'>Annual Waste Cost</div>
            <div className='metric-value'>₹{report.cost_impact.annual_inr.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
            <div className='metric-subtext'>Energy leaking from {report.summary.total_alerts} issues</div>
          </div>

          <div className='metric-card highlight'>
            <div className='metric-label'>Potential Savings</div>
            <div className='metric-value'>₹{report.cost_impact.potential_savings_annual_inr.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
            <div className='metric-subtext'>If all recommendations implemented</div>
          </div>

          <div className='metric-card'>
            <div className='metric-label'>Daily Loss</div>
            <div className='metric-value'>₹{report.cost_impact.daily_inr.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
            <div className='metric-subtext'>{report.summary.open} issues need attention</div>
          </div>

          <div className='metric-card'>
            <div className='metric-label'>ROI Timeline</div>
            <div className='metric-value'>{report.recommendations.projected_payback_months.toFixed(1)} months</div>
            <div className='metric-subtext'>Average payback for recommendations</div>
          </div>
        </div>
      </section>

      {/* TOP 3 WASTE LEAKS - ACTION ORIENTED */}
      <section className='top-waste-section'>
        <h2>🎯 Top 3 Waste Leaks (Ranked by Cost)</h2>
        <p className='section-description'>These are the highest-impact issues you should address first. Each includes specific recommendations.</p>
        
        <div className='waste-leaks-list'>
          {report.top_waste_leaks && report.top_waste_leaks.length > 0 ? (
            report.top_waste_leaks.map((leak, idx) => (
              <div key={leak.alert_id} className={`waste-leak-card rank-${idx + 1}`}>
                <div className='leak-header'>
                  <span className='rank-badge'>#{idx + 1}</span>
                  <span className='severity-badge' style={{ backgroundColor: getSeverityColor(leak.severity) }}>
                    {getSeverityEmoji(leak.severity)} {leak.severity.toUpperCase()}
                  </span>
                </div>
                
                <h3>{getWasteEmoji(leak.waste_type)} {leak.title}</h3>
                
                <div className='leak-details'>
                  <div className='detail-row'>
                    <span className='detail-label'>Device:</span>
                    <span className='detail-value'>{leak.device_category.toUpperCase()} ({leak.device_id})</span>
                  </div>
                  {leak.location.floor && (
                    <div className='detail-row'>
                      <span className='detail-label'>Location:</span>
                      <span className='detail-value'>{leak.location.floor}{leak.location.zone ? ` - ${leak.location.zone}` : ''}</span>
                    </div>
                  )}
                  <div className='detail-row'>
                    <span className='detail-label'>Waste Type:</span>
                    <span className='detail-value'>{leak.waste_type.replace(/_/g, ' ').toUpperCase()}</span>
                  </div>
                </div>

                <div className='  cost-impact'>
                  <div className='cost-item'>
                    <span className='cost-label'>Daily</span>
                    <span className='cost-value'>₹{leak.cost_impact.daily_inr.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
                  </div>
                  <div className='cost-item'>
                    <span className='cost-label'>Monthly</span>
                    <span className='cost-value'>₹{leak.cost_impact.monthly_inr.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
                  </div>
                  <div className='cost-item highlight'>
                    <span className='cost-label'>Annual</span>
                    <span className='cost-value'>₹{leak.cost_impact.annual_inr.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
                  </div>
                </div>

                <button className='action-button' onClick={() => alert(`View recommendations for ${leak.alert_id}`)}>
                  📋 View Recommendations
                </button>
              </div>
            ))
          ) : (
            <p className='no-data'>No significant waste detected. Great job!</p>
          )}
        </div>
      </section>

      {/* ALERT SUMMARY */}
      <section className='alerts-section'>
        <h2>🚨 All Alerts ({report.summary.total_alerts})</h2>
        
        <div className='filter-bar'>
          <label>
            Filter by Floor:
            <select value={selectedFloor || ''} onChange={(e) => setSelectedFloor(e.target.value || null)}>
              <option value=''>All Floors</option>
              {Object.keys(report.waste_by_floor).map(floor => (
                <option key={floor} value={floor}>{floor}</option>
              ))}
            </select>
          </label>
          <label>
            Filter by Category:
            <select value={selectedCategory || ''} onChange={(e) => setSelectedCategory(e.target.value || null)}>
              <option value=''>All Categories</option>
              {Object.keys(report.waste_by_category).map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </label>
        </div>

        <div className='alert-status-grid'>
          <div className='status-card critical'>
            <span className='status-count'>{report.summary.critical}</span>
            <span className='status-label'>Critical</span>
          </div>
          <div className='status-card high'>
            <span className='status-count'>{report.summary.high}</span>
            <span className='status-label'>High</span>
          </div>
          <div className='status-card'>
            <span className='status-count'>{report.summary.open}</span>
            <span className='status-label'>Open</span>
          </div>
        </div>

        {alerts.length > 0 ? (
          <div className='alerts-table'>
            {alerts.map(alert => (
              <div key={alert.alert_id} className='alert-row'>
                <div className='alert-severity' style={{ backgroundColor: getSeverityColor(alert.severity) }}></div>
                <div className='alert-content'>
                  <div className='alert-title'>{alert.title}</div>
                  <div className='alert-meta'>
                    {alert.location.floor && <span>{alert.location.floor}</span>}
                    <span>{alert.device_category}</span>
                    <span>₹{alert.cost_impact.annual_inr.toLocaleString('en-IN', { maximumFractionDigits: 0 })}/year</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className='no-data'>No alerts matching filters.</p>
        )}
      </section>

      {/* BREAKDOWN BY CATEGORY AND TYPE */}
      <section className='breakdown-section'>
        <div className='breakdown-card'>
          <h3>💡 Waste by Device Category</h3>
          {Object.entries(report.waste_by_category).length > 0 ? (
            <ul className='breakdown-list'>
              {Object.entries(report.waste_by_category)
                .sort((a, b) => b[1] - a[1])
                .map(([cat, cost]) => (
                  <li key={cat}>
                    <span>{cat.toUpperCase()}</span>
                    <span class='cost'>₹{cost.toLocaleString('en-IN', { maximumFractionDigits: 0 })}/yr</span>
                  </li>
                ))}
            </ul>
          ) : (
            <p>No data</p>
          )}
        </div>

        <div className='breakdown-card'>
          <h3>🏢 Waste by Floor</h3>
          {Object.entries(report.waste_by_floor).length > 0 ? (
            <ul className='breakdown-list'>
              {Object.entries(report.waste_by_floor)
                .sort((a, b) => b[1] - a[1])
                .map(([floor, cost]) => (
                  <li key={floor}>
                    <span>{floor}</span>
                    <span className='cost'>₹{cost.toLocaleString('en-IN', { maximumFractionDigits: 0 })}/yr</span>
                  </li>
                ))}
            </ul>
          ) : (
            <p>No data</p>
          )}
        </div>

        <div className='breakdown-card'>
          <h3>🔍 Waste by Type</h3>
          {Object.entries(report.waste_by_type).length > 0 ? (
            <ul className='breakdown-list'>
              {Object.entries(report.waste_by_type)
                .sort((a, b) => b[1] - a[1])
                .map(([type, cost]) => (
                  <li key={type}>
                    <span>{type.replace(/_/g, ' ').toUpperCase()}</span>
                    <span className='cost'>₹{cost.toLocaleString('en-IN', { maximumFractionDigits: 0 })}/yr</span>
                  </li>
                ))}
            </ul>
          ) : (
            <p>No data</p>
          )}
        </div>
      </section>

      {/* RECOMMENDATIONS SUMMARY */}
      {report.recommendations.total > 0 && (
        <section className='recommendations-summary'>
          <h2>✅ Recommendations Available</h2>
          <div className='rec-summary'>
            <div className='rec-stat'>
              <span className='rec-number'>{report.recommendations.total}</span>
              <span className='rec-text'>Total recommendations</span>
            </div>
            <div className='rec-stat'>
              <span className='rec-number'>{report.recommendations.approved}</span>
              <span className='rec-text'>Approved for implementation</span>
            </div>
            <div className='rec-stat highlight'>
              <span className='rec-number'>{report.recommendations.projected_payback_months.toFixed(1)}</span>
              <span className='rec-text'>Months average payback</span>
            </div>
          </div>
          <button className='cta-button' onClick={() => window.location.hash = '#recommendations'}>
            View All Recommendations →
          </button>
        </section>
      )}
    </div>
  )
}

