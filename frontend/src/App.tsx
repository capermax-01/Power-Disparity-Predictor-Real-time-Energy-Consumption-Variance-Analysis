import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import DataUpload from './pages/DataUpload'
import About from './pages/About'

export default function App() {
  return (
    <div className="app-root">
      <header className="app-header">
        <h1>🔍 AI-Based Energy Waste Detection Engine</h1>
        <p className="subtitle">Turn invisible energy waste into actionable insights and cost savings</p>
        <nav>
          <Link to="/">Insights</Link> | 
          <Link to="/about">About</Link>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<DataUpload />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>
    </div>
  )
}


