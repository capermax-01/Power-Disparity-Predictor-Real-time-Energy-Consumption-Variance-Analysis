
import React from 'react';
import { EXPERIENCE } from '../constants';

const Resume: React.FC = () => {
  return (
    <main className="px-6 md:px-20 lg:px-40 py-40">
      <div className="max-w-[1200px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12">
        <div className="lg:col-span-8">
          <div className="flex flex-col gap-4 mb-10">
            <h1 className="text-[#111318] text-4xl font-black leading-tight tracking-[-0.033em]">Work Experience</h1>
            <p className="text-[#636f88] text-lg max-w-2xl">A chronological look at my professional journey, focusing on digital product design and creative strategy.</p>
          </div>
          
          <div className="relative space-y-12">
            <div className="absolute left-[19px] top-2 bottom-0 w-[2px] bg-[#dcdfe5]"></div>
            {EXPERIENCE.map((exp) => (
              <div key={exp.id} className="relative pl-12">
                <div className={`absolute left-0 top-1 size-10 rounded-full bg-white border-2 flex items-center justify-center z-10 shadow-sm ${exp.current ? 'border-primary' : 'border-[#dcdfe5]'}`}>
                  <span className={`material-symbols-outlined !text-lg ${exp.current ? 'text-primary' : 'text-[#636f88]'}`}>
                    {exp.id === '1' ? 'work' : 'brush'}
                  </span>
                </div>
                <div className="flex flex-col gap-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <h3 className="text-xl font-bold text-[#111318]">{exp.title}</h3>
                    {exp.current && <span className="px-3 py-1 bg-primary/10 text-primary rounded-full text-xs font-bold uppercase tracking-wider">Present</span>}
                  </div>
                  <p className="text-primary font-semibold text-lg">{exp.company}</p>
                  <p className="text-[#636f88] text-sm mb-4">{exp.period} • {exp.location}</p>
                  <div className="space-y-3 text-[#3c475d] leading-relaxed">
                    {exp.bulletPoints.map((point, idx) => (
                      <div key={idx} className="flex gap-3">
                        <span className="text-primary mt-1">•</span>
                        <p>{point}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="lg:col-span-4 space-y-12">
          <section>
            <div className="flex items-center gap-2 mb-6">
              <span className="material-symbols-outlined text-primary">psychology</span>
              <h2 className="text-xl font-bold text-[#111318] uppercase tracking-tight">Technical Skills</h2>
            </div>
            <div className="space-y-6">
              <div>
                <p className="text-xs font-bold text-[#636f88] uppercase mb-3">Design & Prototyping</p>
                <div className="flex flex-wrap gap-2">
                  {['Figma', 'Adobe CC', 'Protopie', 'Framer', 'Principle'].map(s => (
                    <span key={s} className="px-3 py-1.5 bg-white border border-[#f0f2f4] rounded-lg text-sm font-medium">{s}</span>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-xs font-bold text-[#636f88] uppercase mb-3">Development</p>
                <div className="flex flex-wrap gap-2">
                  {['React', 'Tailwind CSS', 'TypeScript', 'Node.js'].map(s => (
                    <span key={s} className="px-3 py-1.5 bg-white border border-[#f0f2f4] rounded-lg text-sm font-medium">{s}</span>
                  ))}
                </div>
              </div>
            </div>
          </section>

          <section>
            <div className="flex items-center gap-2 mb-6">
              <span className="material-symbols-outlined text-primary">school</span>
              <h2 className="text-xl font-bold text-[#111318] uppercase tracking-tight">Education</h2>
            </div>
            <div className="space-y-6">
              <div className="relative pl-6 before:content-[''] before:absolute before:left-0 before:top-2 before:bottom-0 before:w-1 before:bg-primary/20">
                <h4 className="font-bold text-[#111318]">M.S. Interaction Design</h4>
                <p className="text-sm text-primary font-medium">University of Design & Tech</p>
                <p className="text-xs text-[#636f88]">2014 — 2016</p>
              </div>
            </div>
          </section>

          <section className="p-6 bg-white rounded-xl border border-[#f0f2f4]">
            <h2 className="text-lg font-bold mb-4">Let's Connect</h2>
            <div className="space-y-4">
              <a className="flex items-center gap-3 text-sm text-[#636f88] hover:text-primary transition-colors" href="mailto:hello@designer.com">
                <span className="material-symbols-outlined !text-xl">alternate_email</span>
                <span>hello@designer.com</span>
              </a>
              <a className="flex items-center gap-3 text-sm text-[#636f88] hover:text-primary transition-colors" href="#">
                <span className="material-symbols-outlined !text-xl">public</span>
                <span>linkedin.com/in/prodesigner</span>
              </a>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
};

export default Resume;
