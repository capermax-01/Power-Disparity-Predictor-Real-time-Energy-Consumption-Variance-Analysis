
import React from 'react';
import { Link } from 'react-router-dom';
import { PROJECTS } from '../constants';

const Home: React.FC = () => {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="flex flex-col lg:flex-row min-h-screen pt-20">
        <div className="w-full lg:w-1/2 flex flex-col justify-center px-6 lg:px-20 py-12 lg:py-0">
          <div className="max-w-xl space-y-8">
            <div className="space-y-4">
              <span className="text-primary font-bold tracking-widest text-xs uppercase">Available for freelance</span>
              <h1 className="text-[#111318] text-5xl lg:text-7xl font-black leading-[1.1] tracking-tight">
                Hi, I'm Alex Rivera, a <span className="text-primary">Digital Designer</span>.
              </h1>
              <p className="text-[#111318]/70 text-lg lg:text-xl font-normal leading-relaxed max-w-lg">
                Crafting intuitive digital experiences and visual identities for forward-thinking brands. Based in San Francisco, working globally.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-6">
              <Link to="/work" className="flex min-w-[160px] items-center justify-center rounded-lg h-14 px-8 bg-primary text-white text-base font-bold tracking-wide hover:shadow-lg hover:shadow-primary/20 transition-all">
                View Work
              </Link>
              <Link to="/about" className="flex items-center gap-2 text-base font-bold group">
                Read About Me 
                <span className="material-symbols-outlined group-hover:translate-x-1 transition-transform">arrow_forward</span>
              </Link>
            </div>
            <div className="pt-12 border-t border-black/5 flex gap-8">
              <a className="text-xs font-bold uppercase tracking-widest text-[#111318]/40 hover:text-primary transition-colors" href="#">LinkedIn</a>
              <a className="text-xs font-bold uppercase tracking-widest text-[#111318]/40 hover:text-primary transition-colors" href="#">Dribbble</a>
              <a className="text-xs font-bold uppercase tracking-widest text-[#111318]/40 hover:text-primary transition-colors" href="#">Instagram</a>
            </div>
          </div>
        </div>
        <div className="w-full lg:w-1/2 min-h-[500px] relative overflow-hidden">
          <div className="absolute inset-0 bg-cover bg-center transition-transform duration-700 hover:scale-105" 
               style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuDkBbOX2vtiZO91V0lXAyNl3iwBXlYPz5-br7sduLZHq7jEL3TEerKId5Me1vxuv5yYdLdWrBrSV-D5k6sL7MAsrPEUIs_1jdpyXxAyj6hhLORpo8_Oc_iLlnrsjTtkv6PHNr4b2cM0comwphQ9be01kyqaG-63YcaEEm1jHu8p5NJYqwnaUrxW1uUZieM6jBu3GVRAaIImjFqgvZIgO41g5RX5uUYdwdsH0zb3oxHep3s_EhSSF371wwycpL2eoXJXUEUgF_ar7KFh")' }}>
            <div className="absolute inset-0 bg-gradient-to-t from-background-light/20 to-transparent"></div>
          </div>
          <div className="absolute bottom-10 right-10 hidden xl:flex bg-white/90 backdrop-blur-xl p-6 rounded-xl border border-white/20 shadow-2xl items-center gap-4">
            <div className="size-12 rounded-full bg-primary/20 flex items-center justify-center text-primary">
              <span className="material-symbols-outlined">verified</span>
            </div>
            <div>
              <p className="text-sm font-bold text-[#111318]">6+ Years Exp.</p>
              <p className="text-xs text-[#111318]/60">Digital Product Specialist</p>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Section */}
      <section className="bg-white px-6 lg:px-20 py-24">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-6">
          <div className="max-w-xl">
            <h2 className="text-3xl font-black tracking-tight mb-4">Featured Work</h2>
            <p className="text-[#111318]/60">A selection of projects that showcase my passion for clean aesthetics and functional design.</p>
          </div>
          <Link to="/work" className="text-primary font-bold flex items-center gap-2 hover:underline">
            Explore All Projects <span className="material-symbols-outlined">open_in_new</span>
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          {PROJECTS.slice(0, 4).map((project) => (
            <div key={project.id} className="group cursor-pointer">
              <div className="relative aspect-video rounded-xl overflow-hidden mb-4 shadow-sm">
                <div className="absolute inset-0 bg-cover bg-center group-hover:scale-110 transition-transform duration-500" 
                     style={{ backgroundImage: `linear-gradient(0deg, rgba(0, 0, 0, 0.4) 0%, rgba(0, 0, 0, 0) 100%), url("${project.image}")` }}>
                </div>
              </div>
              <h3 className="text-lg font-bold">{project.title}</h3>
              <p className="text-sm text-[#111318]/60">{project.category}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Home;
