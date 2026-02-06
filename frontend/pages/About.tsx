
import React from 'react';
import { Link } from 'react-router-dom';

const About: React.FC = () => {
  return (
    <main className="max-w-[1000px] mx-auto px-6 py-40">
      <section className="mb-24">
        <h1 className="serif-title text-5xl md:text-7xl mb-8 leading-[1.1] max-w-3xl">
          Designing with purpose, crafting with <span className="italic text-primary">passion</span>.
        </h1>
        <div className="w-full h-[400px] bg-cover bg-center rounded-xl mb-12 shadow-xl" 
             style={{ backgroundImage: "url('https://lh3.googleusercontent.com/aida-public/AB6AXuCC8xLhA16SUbo5ATt0BCSXhlQh1JfdcKHynMjLE4HANOC9WWo4LDMj_7Wb5SgLqMYC0VQZA_BpLZHmvrlttMR2fPJncVGnGaCEmHcmKJwYE5e1Cr18e485lyxaKWPG8WjG4aNQHNJU0at_7h5fyMuSfd8fiUpoLk0Rz-ZjbrUrDC8UG-Z7M1cEGzlsGqPxnVQh6Q_kqingceo8GFmcXsod-FbFPCdQy8HONmWJIsSoRpUQ-BVk7wg6nvVqN9sbpFf108G3PRdGqcBS')" }}>
        </div>
      </section>

      <section className="grid grid-cols-12 gap-8 mb-24">
        <div className="col-span-12 md:col-span-7 space-y-8">
          <h2 className="serif-title text-3xl mb-6">My Story</h2>
          <p className="text-lg leading-relaxed text-slate-600">
            I am a multidisciplinary creative focused on building digital experiences that feel human. With over a decade of experience, I bridge the gap between complex functionality and elegant aesthetics.
          </p>
          <p className="text-lg leading-relaxed text-slate-600">
            My journey began in traditional graphic design before transitioning into the digital realm where I now help brands tell their stories through code and pixels. I believe that the best design isn't just about how it looks, but how it solves problems and connects with the soul.
          </p>
          <div className="flex gap-4 pt-4">
            <div className="w-1/2 aspect-square rounded-lg bg-cover bg-center" style={{ backgroundImage: "url('https://picsum.photos/id/48/800/800')" }}></div>
            <div className="w-1/2 aspect-square rounded-lg bg-cover bg-center" style={{ backgroundImage: "url('https://picsum.photos/id/101/800/800')" }}></div>
          </div>
        </div>
        <div className="col-span-12 md:col-span-4 md:col-start-9 space-y-12">
          <div className="bg-white p-8 rounded-xl border border-slate-100 shadow-sm">
            <h3 className="font-bold text-sm uppercase tracking-widest text-primary mb-6">Core Values</h3>
            <ul className="space-y-6">
              <li className="flex items-start gap-3">
                <span className="material-symbols-outlined text-primary text-xl">verified</span>
                <div>
                  <span className="block font-bold">Authenticity</span>
                  <span className="text-sm text-slate-500">True to the craft and user.</span>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <span className="material-symbols-outlined text-primary text-xl">precision_manufacturing</span>
                <div>
                  <span className="block font-bold">Precision</span>
                  <span className="text-sm text-slate-500">Every pixel has a purpose.</span>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <span className="material-symbols-outlined text-primary text-xl">lightbulb</span>
                <div>
                  <span className="block font-bold">Curiosity</span>
                  <span className="text-sm text-slate-500">Always learning, always evolving.</span>
                </div>
              </li>
            </ul>
          </div>
          <div className="px-2">
            <h3 className="font-bold text-sm uppercase tracking-widest text-slate-400 mb-4">Interests</h3>
            <div className="flex flex-wrap gap-2">
              <span className="px-3 py-1 bg-primary/10 text-primary rounded-full text-xs font-bold">Architecture</span>
              <span className="px-3 py-1 bg-primary/10 text-primary rounded-full text-xs font-bold">Typography</span>
              <span className="px-3 py-1 bg-primary/10 text-primary rounded-full text-xs font-bold">Photography</span>
              <span className="px-3 py-1 bg-primary/10 text-primary rounded-full text-xs font-bold">Industrial Design</span>
              <span className="px-3 py-1 bg-primary/10 text-primary rounded-full text-xs font-bold">Open Source</span>
              <span className="px-3 py-1 bg-primary/10 text-primary rounded-full text-xs font-bold">Vinyl Records</span>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-primary rounded-2xl p-12 text-center text-white relative overflow-hidden">
        <div className="relative z-10 max-w-2xl mx-auto">
          <h2 className="serif-title text-4xl mb-6">Ready to start a project?</h2>
          <p className="mb-10 opacity-90 text-lg">Whether you have a specific project in mind or just want to say hi, my inbox is always open.</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/contact" className="bg-white text-primary px-8 py-3 rounded-lg font-bold hover:bg-slate-100 transition-colors inline-flex items-center justify-center gap-2">
              <span className="material-symbols-outlined">mail</span>
              Get in Touch
            </Link>
            <Link to="/work" className="bg-transparent border border-white text-white px-8 py-3 rounded-lg font-bold hover:bg-white/10 transition-colors inline-flex items-center justify-center gap-2">
              View Portfolio
            </Link>
          </div>
        </div>
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-black/10 rounded-full blur-3xl"></div>
      </section>
    </main>
  );
};

export default About;
