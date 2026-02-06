
import React, { useState } from 'react';

const BatchPrediction: React.FC = () => {
  const [jsonText, setJsonText] = useState(`[
  {
    "appliance_id": "HVAC-UNIT-09",
    "power_rating_kw": 4.5,
    "last_fluctuation": 0.12,
    "environment_temp": 24.5,
    "sensor_nodes": ["SN-1", "SN-4"]
  },
  {
    "appliance_id": "REFRIG-04",
    "power_rating_kw": 0.8,
    "last_fluctuation": 0.04,
    "environment_temp": 21.0,
    "sensor_nodes": ["SN-7"]
  },
  {
    "appliance_id": "IND-MOTOR-22",
    "power_rating_kw": 18.2,
    "last_fluctuation": 1.45,
    "environment_temp": 28.2,
    "sensor_nodes": ["SN-2", "SN-5", "SN-9"]
  }
]`);

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in slide-in-from-bottom-4 duration-500">
      <div>
        <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">
          <span>Dashboard</span>
          <span className="material-symbols-outlined text-[14px]">chevron_right</span>
          <span className="text-white">Batch Prediction</span>
        </div>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-4xl font-black tracking-tight mb-2">Batch Prediction & Analysis</h1>
            <p className="text-slate-400 text-lg">Execute bulk predictions by uploading JSON objects for appliance monitoring.</p>
          </div>
          <div className="flex items-center gap-3">
            <button className="px-5 py-3 text-sm font-bold text-slate-300 bg-slate-800 hover:bg-slate-700 rounded-xl transition-all flex items-center gap-2">
              <span className="material-symbols-outlined text-[20px]">delete</span>
              Clear
            </button>
            <button className="px-8 py-3.5 text-sm font-black text-white bg-primary hover:brightness-110 rounded-xl transition-all flex items-center gap-2 shadow-xl shadow-primary/30">
              <span className="material-symbols-outlined text-[20px]">play_arrow</span>
              Run Prediction
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[
          { label: 'Queue Status', val: 'Ready', icon: 'check_circle', color: 'text-primary' },
          { label: 'Total Objects', val: '124', icon: 'data_object', color: 'text-slate-400' },
          { label: 'Avg. Confidence', val: '94.2%', icon: 'trending_up', color: 'text-emerald-500' },
          { label: 'High Risk', val: '12', icon: 'warning', color: 'text-rose-500' },
        ].map((stat) => (
          <div key={stat.label} className="bg-surface-dark p-6 rounded-2xl border border-slate-800 shadow-xl">
            <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">{stat.label}</p>
            <div className="flex items-end justify-between">
              <h3 className={`text-3xl font-black ${stat.label === 'High Risk' ? 'text-rose-400' : ''}`}>{stat.val}</h3>
              <span className={`material-symbols-outlined text-2xl ${stat.color}`}>{stat.icon}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-black flex items-center gap-3">
              <span className="material-symbols-outlined text-primary">code</span>
              Input JSON
            </h2>
            <span className="text-[10px] font-mono bg-slate-800 px-2.5 py-1 rounded-lg text-slate-400 uppercase tracking-widest font-bold">application/json</span>
          </div>
          <div className="relative group">
            <div className="absolute top-5 left-0 w-12 flex flex-col items-center text-slate-600 font-mono text-[11px] leading-[1.75rem] select-none pointer-events-none border-r border-slate-800/50">
              {Array.from({ length: 15 }, (_, i) => <span key={i}>{i + 1}</span>)}
            </div>
            <textarea
              className="w-full h-[500px] bg-background-dark border-slate-800 rounded-2xl p-5 pl-14 font-mono text-sm leading-relaxed focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all resize-none custom-scrollbar outline-none shadow-2xl"
              spellCheck="false"
              value={jsonText}
              onChange={(e) => setJsonText(e.target.value)}
            />
          </div>
          <div className="flex items-center gap-4 p-5 bg-primary/10 rounded-xl border border-primary/20">
            <span className="material-symbols-outlined text-primary text-2xl">info</span>
            <p className="text-sm text-primary font-bold">Validation: Syntax is valid. Ready to process 3 objects.</p>
          </div>
        </div>

        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-black flex items-center gap-3">
              <span className="material-symbols-outlined text-primary">table_chart</span>
              Batch Results
            </h2>
            <div className="flex items-center gap-3">
              <button className="flex items-center gap-1.5 text-[10px] font-black text-slate-500 hover:text-primary transition-all uppercase tracking-widest">
                <span className="material-symbols-outlined text-lg">download</span> CSV
              </button>
              <div className="w-px h-4 bg-slate-800"></div>
              <button className="flex items-center gap-1.5 text-[10px] font-black text-slate-500 hover:text-primary transition-all uppercase tracking-widest">
                <span className="material-symbols-outlined text-lg">terminal</span> JSON
              </button>
            </div>
          </div>
          <div className="bg-surface-dark border border-slate-800 rounded-2xl overflow-hidden flex flex-col h-[500px] shadow-2xl">
            <div className="overflow-x-auto flex-grow custom-scrollbar">
              <table className="w-full text-left border-collapse">
                <thead className="sticky top-0 bg-slate-900/90 backdrop-blur z-10 border-b border-slate-800">
                  <tr>
                    <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">Appliance</th>
                    <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">Disparity</th>
                    <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">Confidence</th>
                    <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">Risk</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {[
                    { name: 'HVAC-UNIT-09', id: '#4092-A', disp: '0.82 kW', conf: 98.2, risk: 'Low', color: 'emerald' },
                    { name: 'IND-MOTOR-22', id: '#8812-C', disp: '4.15 kW', conf: 87.5, risk: 'High', color: 'rose' },
                    { name: 'REFRIG-04', id: '#1105-B', disp: '0.12 kW', conf: 92.0, risk: 'Medium', color: 'slate' },
                  ].map((row) => (
                    <tr key={row.id} className="hover:bg-slate-800/30 transition-colors group">
                      <td className="px-6 py-5">
                        <div className="flex flex-col">
                          <span className="text-sm font-black group-hover:text-primary transition-colors">{row.name}</span>
                          <span className="text-[10px] font-mono text-slate-500">{row.id}</span>
                        </div>
                      </td>
                      <td className="px-6 py-5 text-sm font-mono text-slate-300">{row.disp}</td>
                      <td className="px-6 py-5">
                        <div className="flex flex-col gap-2">
                          <span className="text-xs font-black">{row.conf}%</span>
                          <div className="w-24 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                            <div className={`h-full bg-${row.color === 'slate' ? 'primary' : row.color + '-500'}`} style={{ width: `${row.conf}%` }}></div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-5">
                        <span className={`px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest border border-slate-700
                          ${row.color === 'emerald' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 
                            row.color === 'rose' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' : 
                            'bg-slate-700/50 text-slate-400 border-slate-600/50'}`}>
                          {row.risk}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="p-4 bg-slate-900/50 border-t border-slate-800 flex items-center justify-between">
              <span className="text-xs font-bold text-slate-500">Showing 3 of 124 entities</span>
              <div className="flex items-center gap-3">
                <button className="p-1 hover:text-primary transition-all"><span className="material-symbols-outlined text-lg">chevron_left</span></button>
                <span className="text-xs font-black">1 / 14</span>
                <button className="p-1 hover:text-primary transition-all"><span className="material-symbols-outlined text-lg">chevron_right</span></button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BatchPrediction;
