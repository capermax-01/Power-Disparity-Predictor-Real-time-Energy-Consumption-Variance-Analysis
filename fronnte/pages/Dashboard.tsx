
import React, { useState } from 'react';

const Dashboard: React.FC = () => {
  const [time, setTime] = useState(14);
  const [power, setPower] = useState(1250);

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-2xl bg-surface-dark border border-slate-800 shadow-xl">
          <div className="flex justify-between items-start mb-4">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">Model Accuracy</p>
            <span className="material-symbols-outlined text-emerald-500">trending_up</span>
          </div>
          <div className="flex items-baseline gap-2">
            <h3 className="text-4xl font-black tracking-tighter">98.4%</h3>
            <span className="text-xs text-emerald-500 font-bold">+0.2%</span>
          </div>
          <div className="mt-5 w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div className="bg-emerald-500 h-full w-[98.4%]"></div>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-surface-dark border border-slate-800 shadow-xl">
          <div className="flex justify-between items-start mb-4">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">Model Type</p>
            <span className="material-symbols-outlined text-primary">psychology</span>
          </div>
          <h3 className="text-3xl font-black tracking-tighter">Random Forest</h3>
          <p className="text-xs text-slate-500 mt-2 font-bold uppercase tracking-widest">Version 2.1-stable</p>
        </div>

        <div className="p-6 rounded-2xl bg-surface-dark border border-slate-800 shadow-xl">
          <div className="flex justify-between items-start mb-4">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">System Status</p>
            <span className="material-symbols-outlined text-emerald-500">check_circle</span>
          </div>
          <h3 className="text-3xl font-black tracking-tighter text-emerald-400">Online</h3>
          <p className="text-xs text-slate-500 mt-2 font-bold uppercase tracking-widest">Uptime: 14d 2h 12m</p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
        {/* Predictor Form */}
        <div className="xl:col-span-7 bg-surface-dark rounded-2xl border border-slate-800 p-8 shadow-xl">
          <div className="flex items-center gap-4 mb-8">
            <div className="size-12 bg-primary/10 rounded-xl flex items-center justify-center text-primary">
              <span className="material-symbols-outlined text-3xl">analytics</span>
            </div>
            <div>
              <h2 className="text-2xl font-black tracking-tight">Interactive Predictor</h2>
              <p className="text-sm text-slate-500">Configure parameters for a single inference request.</p>
            </div>
          </div>

          <form className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-widest">Appliance ID</label>
                <input
                  className="w-full bg-background-dark border-slate-800 rounded-xl py-3 px-4 text-sm focus:ring-primary focus:border-primary transition-all placeholder:text-slate-600"
                  placeholder="e.g. HVAC-001"
                  type="text"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-widest">Category</label>
                <select className="w-full bg-background-dark border-slate-800 rounded-xl py-3 px-4 text-sm focus:ring-primary focus:border-primary transition-all">
                  <option>HVAC Units</option>
                  <option>Industrial Lighting</option>
                  <option>Heavy Machinery</option>
                </select>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-widest">Time of Day (Hour)</label>
                <span className="text-lg font-black text-primary">{time}:00</span>
              </div>
              <input
                className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-primary"
                max="23"
                min="0"
                type="range"
                value={time}
                onChange={(e) => setTime(parseInt(e.target.value))}
              />
              <div className="flex justify-between text-[10px] text-slate-500 font-bold">
                <span>00:00</span>
                <span>06:00</span>
                <span>12:00</span>
                <span>18:00</span>
                <span>23:59</span>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-widest">Current Power Reading (W)</label>
              <div className="relative">
                <input
                  className="w-full bg-background-dark border-slate-800 rounded-xl py-3 px-4 text-sm focus:ring-primary focus:border-primary transition-all"
                  type="number"
                  value={power}
                  onChange={(e) => setPower(parseInt(e.target.value))}
                />
                <span className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 text-[10px] font-black tracking-widest">WATTS</span>
              </div>
            </div>

            <button className="w-full py-4 bg-primary hover:bg-primary/90 text-white rounded-xl font-black text-lg transition-all flex items-center justify-center gap-3 shadow-lg shadow-primary/20" type="button">
              <span className="material-symbols-outlined">cycle</span>
              Run Inference
            </button>
          </form>
        </div>

        {/* Prediction Result */}
        <div className="xl:col-span-5 flex flex-col gap-6">
          <div className="bg-surface-dark rounded-2xl border border-slate-800 p-8 shadow-xl relative overflow-hidden flex-1 flex flex-col">
            <div className="flex justify-between items-center mb-10">
              <h2 className="text-xl font-black tracking-tight">Prediction Result</h2>
              <div className="px-3 py-1 bg-amber-500/10 text-amber-400 rounded-full text-[10px] font-bold uppercase tracking-widest border border-amber-500/20">Medium Risk</div>
            </div>

            <div className="flex-1 flex flex-col items-center justify-center">
              <div className="relative w-72 h-36 overflow-hidden">
                <div className="absolute w-72 h-72 border-[24px] border-slate-800 rounded-full"></div>
                <div 
                  className="absolute w-72 h-72 border-[24px] border-amber-500 rounded-full" 
                  style={{ clipPath: 'polygon(0 50%, 50% 50%, 50% 0, 0 0)' }}
                ></div>
                <div className="absolute w-1.5 h-36 bg-white left-1/2 -translate-x-1/2 origin-bottom rotate-[-45deg]"></div>
              </div>
              <div className="text-center -mt-4">
                <h4 className="text-6xl font-black tracking-tighter">412.5</h4>
                <p className="text-slate-500 font-bold uppercase text-[10px] tracking-widest mt-2">Predicted Disparity (W)</p>
              </div>
            </div>

            <div className="mt-8 space-y-6">
              <div className="space-y-2">
                <div className="flex justify-between text-[10px] font-black uppercase tracking-widest text-slate-500">
                  <span>Confidence Score</span>
                  <span className="text-primary">94%</span>
                </div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-primary w-[94%]"></div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-background-dark border border-slate-800 rounded-xl">
                  <p className="text-[10px] text-slate-500 uppercase font-black tracking-widest mb-1">Lower Bound</p>
                  <p className="text-lg font-black tracking-tight">389 W</p>
                </div>
                <div className="p-4 bg-background-dark border border-slate-800 rounded-xl">
                  <p className="text-[10px] text-slate-500 uppercase font-black tracking-widest mb-1">Upper Bound</p>
                  <p className="text-lg font-black tracking-tight">435 W</p>
                </div>
              </div>
            </div>
            
            <div className="absolute -bottom-16 -right-16 size-48 bg-primary/5 blur-3xl rounded-full"></div>
          </div>

          <div className="bg-primary/10 rounded-2xl border border-primary/20 p-6 flex items-center gap-4 group cursor-pointer hover:bg-primary/15 transition-all">
            <div className="size-14 rounded-xl bg-primary flex items-center justify-center text-white shadow-lg shadow-primary/30">
              <span className="material-symbols-outlined text-3xl">sensors</span>
            </div>
            <div>
              <h4 className="text-lg font-black text-primary tracking-tight">Node Analysis Active</h4>
              <p className="text-sm text-primary/70 font-medium">Analyzing grid patterns from Sector 7-G</p>
            </div>
            <button className="ml-auto text-primary group-hover:translate-x-1 transition-transform">
              <span className="material-symbols-outlined text-3xl">arrow_forward</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
