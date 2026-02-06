
import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="h-16 border-b border-slate-800 flex items-center justify-between px-8 bg-background-dark/50 backdrop-blur-md sticky top-0 z-50">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-black tracking-tight text-white hidden md:block">System Dashboard</h2>
        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-500 text-[10px] font-bold uppercase tracking-wider">Live Monitoring</span>
      </div>

      <div className="flex items-center gap-6">
        <div className="relative w-64 lg:w-96 group">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 text-[20px] transition-colors group-focus-within:text-primary">search</span>
          <input
            className="w-full bg-slate-800 border-none rounded-xl py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-primary/50 transition-all placeholder:text-slate-500"
            placeholder="Search assets, logs, or metrics..."
            type="text"
          />
        </div>
        
        <div className="flex items-center gap-4 border-l border-slate-800 pl-6">
          <button className="text-slate-400 hover:text-primary transition-all relative">
            <span className="material-symbols-outlined">notifications</span>
            <span className="absolute -top-0.5 -right-0.5 size-2 bg-rose-500 rounded-full border border-background-dark"></span>
          </button>
          
          <div className="flex items-center gap-3">
            <div className="flex flex-col items-end text-right">
              <span className="text-sm font-bold text-white">Dr. Aris V.</span>
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-tighter">System Architect</span>
            </div>
            <div 
              className="size-9 rounded-full bg-slate-700 bg-cover bg-center border-2 border-primary/20"
              style={{ backgroundImage: `url('https://picsum.photos/seed/aris/100/100')` }}
            ></div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
