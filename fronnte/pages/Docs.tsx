
import React from 'react';

const Docs: React.FC = () => {
  return (
    <div className="flex flex-col lg:flex-row h-full -m-6 lg:-m-8 overflow-hidden bg-background-dark">
      {/* Doc Sidebar */}
      <aside className="w-full lg:w-72 border-r border-slate-800 overflow-y-auto custom-scrollbar p-6 space-y-10 shrink-0">
        <div>
          <h5 className="px-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">Getting Started</h5>
          <ul className="space-y-1">
            {['Introduction', 'Authentication', 'Errors & Limits'].map(item => (
              <li key={item}>
                <button className="w-full text-left px-4 py-2 text-sm font-semibold text-slate-400 hover:bg-slate-800 hover:text-white rounded-xl transition-all">{item}</button>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h5 className="px-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">Power API</h5>
          <ul className="space-y-1">
            <li className="px-4 py-2.5 bg-primary/10 text-primary rounded-xl flex items-center justify-between font-bold text-sm">
              <span>Predict</span>
              <span className="text-[10px] font-black uppercase px-1.5 py-0.5 bg-primary/20 rounded">POST</span>
            </li>
            {['Batch Predict', 'Model Info', 'History'].map(item => (
              <li key={item} className="px-4 py-2 text-sm font-semibold text-slate-400 hover:text-white cursor-pointer transition-all flex items-center justify-between">
                <span>{item}</span>
                <span className="text-[10px] font-black uppercase text-slate-600">GET</span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h5 className="px-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">SDKs</h5>
          <ul className="space-y-1 px-4 text-sm font-semibold text-slate-400">
            <li className="py-2 hover:text-white cursor-pointer">Node.js</li>
            <li className="py-2 hover:text-white cursor-pointer">Python</li>
          </ul>
        </div>
      </aside>

      {/* Main Doc Content */}
      <main className="flex-1 overflow-y-auto custom-scrollbar p-10 lg:p-14 bg-background-dark">
        <div className="max-w-4xl">
          <nav className="flex items-center gap-2 text-[10px] font-black text-slate-500 uppercase tracking-widest mb-6">
            <span>API Reference</span>
            <span className="material-symbols-outlined text-[14px]">chevron_right</span>
            <span className="text-primary">Endpoints</span>
            <span className="material-symbols-outlined text-[14px]">chevron_right</span>
            <span>Predict Power Fluctuations</span>
          </nav>
          
          <div className="flex items-center gap-4 mb-6">
            <span className="px-3 py-1 bg-emerald-500/10 text-emerald-500 rounded-lg font-black text-xs uppercase tracking-widest border border-emerald-500/20">POST</span>
            <span className="font-mono text-slate-500 text-lg">/v2/predict</span>
          </div>
          
          <h1 className="text-5xl font-black text-white tracking-tighter mb-6">Predict Power Fluctuations</h1>
          <p className="text-xl text-slate-400 leading-relaxed mb-12">
            This endpoint analyzes real-time appliance data to predict potential power disparities and voltage fluctuations. Provide the appliance ID and current voltage metrics to receive a confidence-scored prediction within 50ms.
          </p>

          <hr className="border-slate-800 mb-12" />

          <section className="space-y-12">
            <div>
              <h3 className="text-2xl font-black text-white mb-8">Request Parameters</h3>
              <div className="space-y-8">
                <div className="pb-8 border-b border-slate-800">
                  <div className="flex items-center gap-4 mb-2">
                    <span className="font-mono font-bold text-primary text-lg">appliance_id</span>
                    <span className="text-[10px] font-black px-2 py-0.5 bg-slate-800 text-slate-500 rounded-lg uppercase tracking-widest">string</span>
                    <span className="text-[10px] font-black text-rose-500 uppercase tracking-widest">Required</span>
                  </div>
                  <p className="text-slate-400">The unique identifier for the registered appliance in your dashboard.</p>
                </div>
                
                <div className="pb-8 border-b border-slate-800">
                  <div className="flex items-center gap-4 mb-2">
                    <span className="font-mono font-bold text-primary text-lg">voltage_metrics</span>
                    <span className="text-[10px] font-black px-2 py-0.5 bg-slate-800 text-slate-500 rounded-lg uppercase tracking-widest">object</span>
                    <span className="text-[10px] font-black text-rose-500 uppercase tracking-widest">Required</span>
                  </div>
                  <p className="text-slate-400 mb-6">An object containing the current electrical readings of the device.</p>
                  
                  <div className="pl-8 border-l-4 border-slate-800 space-y-8">
                    <div>
                      <div className="flex items-center gap-3 mb-1">
                        <span className="font-mono font-bold text-slate-300">rms_voltage</span>
                        <span className="text-[10px] font-black text-slate-600 uppercase tracking-widest">number</span>
                      </div>
                      <p className="text-sm text-slate-500">The Root Mean Square voltage currently detected.</p>
                    </div>
                    <div>
                      <div className="flex items-center gap-3 mb-1">
                        <span className="font-mono font-bold text-slate-300">frequency</span>
                        <span className="text-[10px] font-black text-slate-600 uppercase tracking-widest">number</span>
                      </div>
                      <p className="text-sm text-slate-500">The grid frequency in Hz (standard is 50/60).</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      </main>

      {/* Code Playground */}
      <aside className="w-[500px] hidden xl:flex flex-col bg-slate-900 border-l border-slate-800 shrink-0">
        <div className="h-14 flex items-center justify-between px-6 border-b border-slate-800 bg-slate-950/50">
          <div className="flex items-center gap-2">
            <button className="px-4 py-1.5 text-xs font-black text-white bg-primary rounded-xl shadow-lg shadow-primary/20">Node.js</button>
            <button className="px-4 py-1.5 text-xs font-black text-slate-500 hover:text-white transition-all">Python</button>
            <button className="px-4 py-1.5 text-xs font-black text-slate-500 hover:text-white transition-all">cURL</button>
          </div>
          <button className="text-slate-500 hover:text-white transition-all"><span className="material-symbols-outlined text-xl">content_copy</span></button>
        </div>
        
        <div className="flex-1 p-8 font-mono text-sm leading-relaxed overflow-y-auto custom-scrollbar">
          <div className="mb-12">
            <div className="text-slate-600 mb-3 italic">// Sample Predict Request</div>
            <pre className="text-slate-300">
              <span className="text-rose-400">const</span> sdk = <span className="text-purple-400">require</span>(<span className="text-emerald-400">'@pdp/sdk'</span>);{'\n'}
              <span className="text-rose-400">const</span> client = <span className="text-rose-400">new</span> sdk.Client({'{'}{'\n'}
              {'  '}apiKey: <span className="text-emerald-400">'YOUR_API_KEY'</span>{'\n'}
              {'}'});{'\n'}{'\n'}
              <span className="text-rose-400">const</span> result = <span className="text-rose-400">await</span> client.<span className="text-blue-400">predict</span>({'{'}{'\n'}
              {'  '}appliance_id: <span className="text-emerald-400">'dev_7812x'</span>,{'\n'}
              {'  '}voltage_metrics: {'{'}{'\n'}
              {'    '}rms_voltage: <span className="text-amber-400">231.4</span>,{'\n'}
              {'    '}frequency: <span className="text-amber-400">60.02</span>{'\n'}
              {'  '}{'}'}{'\n'}
              {'}'});
            </pre>
          </div>
          
          <div className="mt-12">
            <div className="flex items-center justify-between mb-6">
              <div className="text-slate-600 uppercase text-[10px] font-black tracking-widest">Response Body</div>
              <div className="flex items-center gap-2">
                <span className="size-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span className="text-xs font-black text-emerald-500 tracking-widest">200 OK</span>
              </div>
            </div>
            <div className="bg-slate-950 rounded-2xl p-6 border border-slate-800 shadow-2xl">
              <pre className="text-emerald-400/80">
                {'{'}{'\n'}
                {'  '}<span className="text-emerald-400">"id"</span>: <span className="text-slate-400">"pred_91283712"</span>,{'\n'}
                {'  '}<span className="text-emerald-400">"object"</span>: <span className="text-slate-400">"prediction"</span>,{'\n'}
                {'  '}<span className="text-emerald-400">"disparity_score"</span>: <span className="text-amber-400">0.12</span>,{'\n'}
                {'  '}<span className="text-emerald-400">"risk_level"</span>: <span className="text-slate-400">"low"</span>,{'\n'}
                {'  '}<span className="text-emerald-400">"metadata"</span>: {'{'}{'\n'}
                {'    '}<span className="text-emerald-400">"confidence"</span>: <span className="text-amber-400">0.9982</span>{'\n'}
                {'  '}{'}'}{'\n'}
                {'}'}
              </pre>
            </div>
          </div>
        </div>
        
        <div className="p-6 border-t border-slate-800 bg-slate-950/50">
          <button className="w-full bg-primary hover:brightness-110 text-white py-3.5 rounded-xl text-sm font-black transition-all flex items-center justify-center gap-3 shadow-xl shadow-primary/30">
            <span className="material-symbols-outlined text-lg">play_arrow</span>
            Test Live Request
          </button>
        </div>
      </aside>
    </div>
  );
};

export default Docs;
