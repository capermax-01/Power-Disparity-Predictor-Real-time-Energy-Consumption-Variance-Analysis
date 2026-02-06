
import React from 'react';
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip, AreaChart, Area } from 'recharts';

const chartData = [
  { time: '00:00', val: 97.2, truth: 97.0 },
  { time: '04:00', val: 98.5, truth: 98.2 },
  { time: '08:00', val: 97.8, truth: 98.0 },
  { time: '12:00', val: 99.1, truth: 99.0 },
  { time: '16:00', val: 98.2, truth: 98.5 },
  { time: '20:00', val: 98.8, truth: 98.7 },
  { time: '23:59', val: 98.4, truth: 98.4 },
];

const Insights: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-[10px] font-black text-slate-500 uppercase tracking-widest">
            <span>Dashboard</span>
            <span className="material-symbols-outlined text-[14px]">chevron_right</span>
            <span className="text-primary">Model Insights</span>
          </div>
          <h1 className="text-5xl font-black tracking-tight text-white">Model Performance <span className="text-primary">v1.3-beta</span></h1>
          <p className="text-slate-400 text-xl max-w-2xl">Real-time disparity prediction engine health and feature weight analysis.</p>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 px-5 py-3 rounded-xl bg-slate-800 border border-slate-700 font-bold text-sm hover:bg-slate-700 transition-all">
            <span className="material-symbols-outlined text-lg">calendar_today</span>
            Last 24 Hours
          </button>
          <button className="flex items-center gap-2 px-8 py-3 rounded-xl bg-primary text-white font-black text-sm hover:brightness-110 transition-all shadow-xl shadow-primary/30">
            <span className="material-symbols-outlined text-lg">download</span>
            Export Report
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: 'Accuracy', val: '98.42%', icon: 'target', color: 'text-blue-500', trend: '+0.2%' },
          { label: 'Avg. Latency', val: '24.5ms', icon: 'timer', color: 'text-purple-500', trend: '-2ms' },
          { label: 'Server Uptime', val: '99.99%', icon: 'cloud_done', color: 'text-emerald-500', trend: 'Stable' },
          { label: 'Inference Vol.', val: '1.2M', icon: 'database', color: 'text-orange-500', trend: '8.2k/min' },
        ].map(card => (
          <div key={card.label} className="bg-surface-dark p-6 rounded-2xl border border-slate-800 shadow-xl">
            <div className="flex justify-between items-start mb-6">
              <div className={`p-2.5 bg-opacity-10 rounded-xl ${card.color.replace('text', 'bg')}`}>
                <span className={`material-symbols-outlined ${card.color}`}>{card.icon}</span>
              </div>
              <span className={`text-[9px] font-black px-2 py-1 rounded-lg uppercase tracking-widest ${card.trend === 'Stable' ? 'bg-slate-800 text-slate-500' : 'bg-emerald-500/10 text-emerald-400'}`}>
                {card.trend}
              </span>
            </div>
            <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">{card.label}</p>
            <p className="text-3xl font-black text-white">{card.val}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-surface-dark rounded-2xl border border-slate-800 shadow-2xl overflow-hidden flex flex-col">
          <div className="p-8 border-b border-slate-800 flex justify-between items-center">
            <div>
              <h3 className="font-black text-xl tracking-tight">Accuracy Over Time</h3>
              <p className="text-[10px] text-slate-500 uppercase tracking-widest font-black mt-1">Predicted vs Actual Fluctuations</p>
            </div>
            <div className="flex gap-4">
              <span className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest">
                <span className="size-2 rounded-full bg-primary"></span> Predictions
              </span>
              <span className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-slate-500">
                <span className="size-2 rounded-full bg-slate-600"></span> Ground Truth
              </span>
            </div>
          </div>
          <div className="flex-1 p-8 h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#667fea" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#667fea" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
                <YAxis stroke="#475569" fontSize={10} tickLine={false} axisLine={false} domain={[96, 100]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '12px' }}
                  itemStyle={{ fontSize: '12px', fontWeight: 'bold' }}
                />
                <Area type="monotone" dataKey="val" stroke="#667fea" strokeWidth={3} fillOpacity={1} fill="url(#colorVal)" />
                <Line type="monotone" dataKey="truth" stroke="#475569" strokeDasharray="5 5" strokeWidth={2} dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-surface-dark rounded-2xl border border-slate-800 shadow-2xl overflow-hidden flex flex-col">
          <div className="p-8 border-b border-slate-800">
            <h3 className="font-black text-xl tracking-tight">Feature Importance</h3>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-black mt-1">SHAP Value Distributions</p>
          </div>
          <div className="p-8 space-y-8 flex-1">
            {[
              { name: 'power_reading_avg', val: 42 },
              { name: 'hour_of_day', val: 28 },
              { name: 'device_age_months', val: 15 },
              { name: 'ambient_temp_c', val: 9 },
              { name: 'voltage_fluctuation', val: 6 },
            ].map(f => (
              <div key={f.name} className="space-y-3">
                <div className="flex justify-between text-xs font-bold uppercase tracking-widest">
                  <span className="text-slate-400">{f.name}</span>
                  <span className="text-primary font-black">{f.val}%</span>
                </div>
                <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-primary rounded-full transition-all duration-1000" style={{ width: `${f.val}%` }}></div>
                </div>
              </div>
            ))}
            <button className="w-full py-3.5 text-[10px] font-black text-primary border border-primary/20 rounded-xl hover:bg-primary/5 transition-all uppercase tracking-widest mt-6">
              View All 24 Features
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 pb-12">
        <div className="bg-surface-dark rounded-2xl border border-slate-800 shadow-2xl overflow-hidden">
          <div className="p-8 border-b border-slate-800 bg-emerald-500/5">
            <div className="flex items-center gap-4">
              <div className="relative">
                <span className="material-symbols-outlined text-emerald-500 text-4xl">dns</span>
                <span className="absolute -top-1 -right-1 size-3 bg-emerald-500 rounded-full border-2 border-surface-dark animate-pulse"></span>
              </div>
              <div>
                <h3 className="font-black text-xl tracking-tight">Predictor Health</h3>
                <p className="text-[10px] text-emerald-500 font-black uppercase tracking-widest">All nodes operational</p>
              </div>
            </div>
          </div>
          <div className="p-8 space-y-8">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-5 bg-background-dark/50 rounded-2xl border border-slate-800">
                <div className="text-[9px] font-black text-slate-600 uppercase tracking-widest mb-1.5">CPU LOAD</div>
                <div className="text-2xl font-black text-white">12.4%</div>
              </div>
              <div className="p-5 bg-background-dark/50 rounded-2xl border border-slate-800">
                <div className="text-[9px] font-black text-slate-600 uppercase tracking-widest mb-1.5">MEMORY</div>
                <div className="text-2xl font-black text-white">3.2 GB</div>
              </div>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between text-sm font-bold">
                <span className="text-slate-500 uppercase tracking-widest text-[10px]">Error Rate</span>
                <span className="text-white">0.001%</span>
              </div>
              <div className="flex items-center justify-between text-sm font-bold">
                <span className="text-slate-500 uppercase tracking-widest text-[10px]">Model Version</span>
                <span className="px-2 py-0.5 bg-slate-800 rounded-lg text-white font-mono text-[10px]">v1.3.4-prod</span>
              </div>
              <div className="flex items-center justify-between text-sm font-bold">
                <span className="text-slate-500 uppercase tracking-widest text-[10px]">Last Deployment</span>
                <span className="text-white">2 days ago</span>
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 bg-surface-dark rounded-2xl border border-slate-800 shadow-2xl overflow-hidden flex flex-col">
          <div className="p-8 border-b border-slate-800 flex justify-between items-center">
            <h3 className="font-black text-xl tracking-tight">Live Inference Feed</h3>
            <span className="text-[9px] font-black bg-slate-800 px-3 py-1.5 rounded-lg uppercase tracking-[0.2em] text-slate-500">Real-Time</span>
          </div>
          <div className="flex-1 overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-background-dark/30 text-slate-600 uppercase text-[9px] font-black tracking-widest">
                <tr>
                  <th className="px-8 py-4">Inference ID</th>
                  <th className="px-8 py-4">Timestamp</th>
                  <th className="px-8 py-4">Result</th>
                  <th className="px-8 py-4">Confidence</th>
                  <th className="px-8 py-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {[
                  { id: '#inf-882190', ts: '14:22:01.03', res: 'Fluctuation', conf: '99.2', status: 'warning' },
                  { id: '#inf-882189', ts: '14:21:58.92', res: 'Stable', conf: '98.8', status: 'primary' },
                  { id: '#inf-882188', ts: '14:21:55.11', res: 'Stable', conf: '99.5', status: 'primary' },
                  { id: '#inf-882187', ts: '14:21:51.44', res: 'Fluctuation', conf: '96.2', status: 'warning' },
                ].map(row => (
                  <tr key={row.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-8 py-5 font-mono text-[11px] text-slate-400">{row.id}</td>
                    <td className="px-8 py-5 text-xs font-bold text-slate-500">{row.ts}</td>
                    <td className="px-8 py-5">
                      <span className={`px-2 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest 
                        ${row.status === 'warning' ? 'bg-orange-500/10 text-orange-400' : 'bg-primary/10 text-primary'}`}>
                        {row.res}
                      </span>
                    </td>
                    <td className="px-8 py-5 font-black text-sm">{row.conf}%</td>
                    <td className="px-8 py-5 text-right">
                      <button className="text-[10px] font-black text-primary uppercase tracking-widest hover:underline">Inspect</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Insights;
