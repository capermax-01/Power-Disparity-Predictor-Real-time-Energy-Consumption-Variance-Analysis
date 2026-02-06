
import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar: React.FC = () => {
  const navItems = [
    { label: 'Dashboard', icon: 'dashboard', path: '/dashboard' },
    { label: 'Batch Prediction', icon: 'layers', path: '/batch' },
    { label: 'Appliance Catalog', icon: 'database', path: '/catalog' },
    { label: 'Model Insights', icon: 'analytics', path: '/insights' },
    { label: 'Documentation', icon: 'auto_stories', path: '/docs' },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 flex flex-col bg-background-dark hidden lg:flex">
      <div className="p-8 flex items-center gap-3">
        <div className="size-10 bg-primary rounded-lg flex items-center justify-center text-white shadow-lg shadow-primary/20">
          <span className="material-symbols-outlined text-2xl font-bold">bolt</span>
        </div>
        <div>
          <h1 className="font-black text-sm tracking-tight uppercase">Power Predictor</h1>
          <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">AI Monitoring</p>
        </div>
      </div>

      <nav className="flex-1 px-4 space-y-2 mt-4">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `
              flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200
              ${isActive 
                ? 'bg-primary text-white shadow-lg shadow-primary/20 font-bold' 
                : 'text-slate-400 hover:bg-slate-800 hover:text-slate-100'}
            `}
          >
            <span className="material-symbols-outlined text-[22px]">{item.icon}</span>
            <span className="text-sm font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-6 mt-auto">
        <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
          <div className="flex items-center gap-2 mb-2">
            <span className="size-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Engine Status</span>
          </div>
          <p className="text-xs font-semibold">Reliability: 98.4%</p>
          <div className="w-full bg-slate-700 h-1 rounded-full mt-2 overflow-hidden">
            <div className="bg-primary h-full w-[98.4%]"></div>
          </div>
        </div>
        <button className="w-full bg-primary text-white py-3 rounded-xl text-sm font-bold flex items-center justify-center gap-2 mt-4 shadow-lg shadow-primary/20 hover:brightness-110 transition-all">
          <span className="material-symbols-outlined text-[20px]">add</span>
          New Prediction
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
