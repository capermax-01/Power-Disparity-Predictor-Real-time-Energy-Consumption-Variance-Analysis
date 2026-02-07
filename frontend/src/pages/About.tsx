import React from 'react'

export default function About() {
  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      {/* Hero Section */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: '16px',
        padding: '3rem',
        color: 'white',
        marginBottom: '3rem',
        boxShadow: '0 10px 30px rgba(102, 126, 234, 0.3)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23ffffff\' fill-opacity=\'0.05\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
          opacity: 0.3
        }}></div>
        <div style={{ position: 'relative', zIndex: 1 }}>
          <h1 style={{ margin: '0 0 1rem 0', fontSize: '2.5rem', fontWeight: '900' }}>
            About Our Platform
          </h1>
          <p style={{ fontSize: '1.2rem', opacity: 0.95, margin: 0, lineHeight: 1.6 }}>
            AI-powered energy waste detection system that helps buildings reduce costs and carbon footprint
          </p>
        </div>
      </div>

      {/* What We Do */}
      <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '2.5rem',
        marginBottom: '2rem',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
        border: '1px solid #e2e8f0'
      }}>
        <h2 style={{ color: '#1e293b', marginTop: 0, fontSize: '1.75rem', fontWeight: '700' }}>
          🎯 What We Do
        </h2>
        <p style={{ color: '#64748b', fontSize: '1.1rem', lineHeight: 1.8 }}>
          Our AI-Based Energy Waste Detection Engine analyzes smart meter data from buildings to identify 
          energy waste patterns and provide actionable recommendations. We help facility managers and building 
          operators reduce energy costs by detecting:
        </p>
        <ul style={{ color: '#64748b', fontSize: '1.05rem', lineHeight: 1.8 }}>
          <li><strong>Phantom Loads</strong> - Devices consuming power when they should be off</li>
          <li><strong>After-Hours Usage</strong> - HVAC and lighting running when buildings are empty</li>
          <li><strong>Unoccupied Waste</strong> - High energy consumption in unoccupied spaces</li>
        </ul>
      </div>

      {/* How It Works */}
      <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '2.5rem',
        marginBottom: '2rem',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
        border: '1px solid #e2e8f0'
      }}>
        <h2 style={{ color: '#1e293b', marginTop: 0, fontSize: '1.75rem', fontWeight: '700' }}>
          ⚙️ How It Works
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
          {[
            { step: '1', title: 'Upload Data', desc: 'Upload your smart meter CSV data with device readings' },
            { step: '2', title: 'AI Analysis', desc: 'Our AI learns baselines and detects waste patterns' },
            { step: '3', title: 'Get Insights', desc: 'Receive detailed reports with cost calculations' },
            { step: '4', title: 'Take Action', desc: 'Implement recommendations to save energy and money' }
          ].map((item, idx) => (
            <div key={idx} style={{
              padding: '1.5rem',
              background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
              borderRadius: '12px',
              border: '2px solid #bae6fd'
            }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.5rem',
                fontWeight: '900',
                marginBottom: '1rem'
              }}>
                {item.step}
              </div>
              <h3 style={{ margin: '0 0 0.5rem 0', color: '#1e293b', fontSize: '1.1rem' }}>{item.title}</h3>
              <p style={{ margin: 0, color: '#64748b', fontSize: '0.95rem', lineHeight: 1.6 }}>{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Key Features */}
      <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '2.5rem',
        marginBottom: '2rem',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
        border: '1px solid #e2e8f0'
      }}>
        <h2 style={{ color: '#1e293b', marginTop: 0, fontSize: '1.75rem', fontWeight: '700' }}>
          ✨ Key Features
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
          {[
            { icon: '🤖', title: 'AI-Powered Analysis', desc: 'Machine learning algorithms detect patterns humans miss' },
            { icon: '💰', title: 'Cost Calculations', desc: 'Precise daily, monthly, and yearly savings estimates' },
            { icon: '📊', title: 'Detailed Reports', desc: 'Professional energy audit reports with actionable insights' },
            { icon: '⚡', title: 'Real-Time Detection', desc: 'Instant identification of energy waste as it happens' },
            { icon: '🎯', title: 'Priority Ranking', desc: 'Issues ranked by cost impact for maximum ROI' },
            { icon: '🔧', title: 'Automation Rules', desc: 'Smart recommendations for automated energy management' }
          ].map((feature, idx) => (
            <div key={idx} style={{
              padding: '1.25rem',
              background: '#f8fafc',
              borderRadius: '12px',
              border: '1px solid #e2e8f0',
              transition: 'all 0.3s'
            }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{feature.icon}</div>
              <h4 style={{ margin: '0 0 0.5rem 0', color: '#1e293b', fontSize: '1rem' }}>{feature.title}</h4>
              <p style={{ margin: 0, color: '#64748b', fontSize: '0.9rem', lineHeight: 1.5 }}>{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>


    </div>
  )
}
