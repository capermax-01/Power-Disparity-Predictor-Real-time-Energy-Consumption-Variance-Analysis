import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import Home from './pages/Home'
import Predictor from './pages/Predictor'
import Dashboard from './pages/Dashboard'
import Documentation from './pages/Documentation'

export default function App() {
  return (
    <div className="app-root">
      <header className="app-header">
        <h1>Power Disparity Predictor</h1>
        <nav>
          <Link to="/">Home</Link> | <Link to="/predict">Predict</Link> | <Link to="/dashboard">Dashboard</Link> | <Link to="/docs">Docs</Link>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/predict" element={<Predictor />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/docs" element={<Documentation />} />
        </Routes>
      </main>
    </div>
  )
}
