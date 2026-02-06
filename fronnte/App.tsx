
import React from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import BatchPrediction from './pages/BatchPrediction';
import Docs from './pages/Docs';
import Catalog from './pages/Catalog';
import Insights from './pages/Insights';

const App: React.FC = () => {
  return (
    <Router>
      <div className="flex min-h-screen bg-background-dark text-slate-100 overflow-hidden">
        <Sidebar />
        <div className="flex-1 flex flex-col h-screen overflow-hidden">
          <Header />
          <main className="flex-1 overflow-y-auto custom-scrollbar p-6 lg:p-8">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/batch" element={<BatchPrediction />} />
              <Route path="/docs" element={<Docs />} />
              <Route path="/catalog" element={<Catalog />} />
              <Route path="/insights" element={<Insights />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
};

export default App;
