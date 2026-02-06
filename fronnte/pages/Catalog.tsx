
import React from 'react';

const Catalog: React.FC = () => {
  const appliances = [
    { name: 'Smart Fridge Pro', brand: 'LG Model S-240', cat: 'Kitchen', max: '0.85', mean: '0.42', status: 'Optimized', icon: 'kitchen', color: 'emerald' },
    { name: 'Industrial HVAC', brand: 'Daikin VRV 5', cat: 'HVAC', max: '4.50', mean: '2.18', status: 'High Load', icon: 'hvac', color: 'primary' },
    { name: 'Smart Washer', brand: 'Bosch Series 8', cat: 'Laundry', max: '2.20', mean: '0.85', status: '', icon: 'local_laundry_service', color: 'slate' },
    { name: 'Induction Range', brand: 'Samsung Flex', cat: 'Kitchen', max: '3.70', mean: '1.12', status: 'Syncing', icon: 'oven_gen', color: 'amber' },
    { name: 'Eco Heat Pump', brand: 'Mitsubishi Z-Series', cat: 'HVAC', max: '3.20', mean: '1.45', status: 'Optimized', icon: 'heat_pump', color: 'emerald' },
    { name: 'Silent Dishwasher', brand: 'Miele G7000', cat: 'Kitchen', max: '1.50', mean: '0.58', status: '', icon: 'dishwasher', color: 'slate' },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-black text-slate-500 uppercase tracking-widest mb-3">
            <span>Catalog</span>
            <span className="material-symbols-outlined text-[14px]">chevron_right</span>
            <span className="text-white">All Appliances</span>
          </div>
          <h2 className="text-4xl font-black tracking-tight text-white">Appliance Catalog</h2>
          <p className="text-slate-400 mt-2 text-lg">Manage power disparity models for individual units.</p>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 px-5 py-3 bg-slate-800 rounded-xl text-sm font-bold hover:bg-slate-700 transition-all">
            <span className="material-symbols-outlined text-lg">filter_list</span>
            Filter
          </button>
          <button className="flex items-center gap-2 px-8 py-3 bg-primary text-white rounded-xl text-sm font-black hover:brightness-110 transition-all shadow-xl shadow-primary/30">
            <span className="material-symbols-outlined text-lg">add</span>
            New Appliance
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-3 items-center">
        {['All Appliances', 'Kitchen', 'HVAC Systems', 'Laundry', 'Entertainment'].map((tab, i) => (
          <button key={tab} className={`px-6 py-2.5 rounded-full text-xs font-black uppercase tracking-widest transition-all
            ${i === 0 ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700'}`}>
            {tab}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {appliances.map((app) => (
          <div key={app.name} className="group relative bg-surface-dark border border-slate-800 rounded-2xl overflow-hidden hover:border-primary transition-all duration-300 shadow-xl hover:shadow-2xl hover:shadow-primary/10">
            <div className="h-52 bg-slate-900/50 flex items-center justify-center relative">
              <span className="material-symbols-outlined text-7xl text-slate-700 group-hover:text-primary transition-colors duration-500">{app.icon}</span>
              {app.status && (
                <div className={`absolute top-5 right-5 px-3 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest border border-current bg-opacity-10
                  ${app.color === 'emerald' ? 'bg-emerald-500 text-emerald-400 border-emerald-500/20' : 
                    app.color === 'amber' ? 'bg-amber-500 text-amber-400 border-amber-500/20' : 
                    'bg-primary text-primary border-primary/20'}`}>
                  {app.status}
                </div>
              )}
            </div>
            
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h3 className="font-black text-xl text-white tracking-tight">{app.name}</h3>
                  <p className="text-xs text-slate-500 font-bold uppercase tracking-widest mt-1">{app.cat} • {app.brand}</p>
                </div>
                <span className="material-symbols-outlined text-slate-600 hover:text-primary cursor-pointer transition-colors">more_vert</span>
              </div>
              
              <div className="grid grid-cols-2 gap-4 mb-8">
                <div className="p-4 bg-background-dark/50 rounded-2xl border border-slate-800/50 group-hover:bg-background-dark/80 transition-all">
                  <p className="text-[9px] text-slate-600 uppercase font-black tracking-widest mb-1.5">Max Power</p>
                  <p className="text-2xl font-black text-white">{app.max} <span className="text-xs font-bold text-slate-600">kW</span></p>
                </div>
                <div className="p-4 bg-background-dark/50 rounded-2xl border border-slate-800/50 group-hover:bg-background-dark/80 transition-all">
                  <p className="text-[9px] text-slate-600 uppercase font-black tracking-widest mb-1.5">Mean 12h</p>
                  <p className="text-2xl font-black text-white">{app.mean} <span className="text-xs font-bold text-slate-600">kWh</span></p>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex -space-x-3">
                  <div className="size-7 rounded-full border-2 border-surface-dark bg-primary/20 flex items-center justify-center text-[10px] font-black text-primary">AI</div>
                  <div className="size-7 rounded-full border-2 border-surface-dark bg-slate-700 flex items-center justify-center text-[10px] font-black text-slate-400">ML</div>
                </div>
                <button className="text-xs font-black text-primary hover:underline flex items-center gap-1.5 uppercase tracking-widest">
                  View Specs
                  <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="pt-10 flex justify-center pb-12">
        <button className="px-12 py-4 rounded-2xl border border-slate-800 font-black text-slate-400 hover:bg-slate-800 hover:text-white transition-all uppercase tracking-widest text-xs">
          Load More Appliances
        </button>
      </div>
    </div>
  );
};

export default Catalog;
