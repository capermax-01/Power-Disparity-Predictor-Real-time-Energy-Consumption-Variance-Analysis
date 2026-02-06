
import React, { useState } from 'react';
import { PROJECTS } from '../constants';

const Work: React.FC = () => {
  const [filter, setFilter] = useState('All Projects');
  const categories = ['All Projects', 'UI/UX Design', 'Branding', 'Photography', 'Motion'];

  const filteredProjects = filter === 'All Projects' 
    ? PROJECTS 
    : PROJECTS.filter(p => p.tag === filter);

  return (
    <main className="flex-1 w-full max-w-[1440px] mx-auto px-6 lg:px-20 py-40">
      <div className="mb-12">
        <h2 className="text-4xl lg:text-5xl font-black mb-4 tracking-tight">Selected Works</h2>
        <p className="text-[#636f88] text-lg max-w-2xl leading-relaxed">
          A curated collection of digital experiences, visual identities, and motion studies focused on elegance and utility.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-2 mb-10 border-b border-[#f0f2f4] pb-6">
        {categories.map((cat) => (
          <button 
            key={cat}
            onClick={() => setFilter(cat)}
            className={`px-5 py-2 rounded-full text-sm font-semibold transition-all ${filter === cat ? 'bg-primary text-white' : 'hover:bg-primary/10 text-[#636f88] hover:text-primary'}`}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="masonry-grid">
        {filteredProjects.map((project) => (
          <div key={project.id} className="masonry-item group cursor-pointer relative overflow-hidden rounded-xl bg-white shadow-sm border border-black/5">
            <img 
              className="w-full h-auto object-cover transition-transform duration-700 group-hover:scale-105" 
              src={project.image} 
              alt={project.title}
            />
            <div className="absolute inset-0 bg-primary/90 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col items-center justify-center p-6 text-center">
              <span className="text-white/80 text-xs font-bold uppercase tracking-widest mb-2">{project.tag}</span>
              <h3 className="text-white text-2xl font-bold">{project.title}</h3>
              <div className="mt-6 size-10 rounded-full border border-white/30 flex items-center justify-center text-white">
                <span className="material-symbols-outlined text-sm">arrow_forward</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </main>
  );
};

export default Work;
