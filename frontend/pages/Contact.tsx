
import React from 'react';

const Contact: React.FC = () => {
  return (
    <main className="flex-1 flex items-center justify-center px-6 md:px-12 lg:px-20 py-40">
      <div className="max-w-[1100px] w-full grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-24 items-start">
        <div className="flex flex-col space-y-8">
          <div className="space-y-4">
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-[#111318]">Let's Connect</h1>
            <p className="text-lg text-gray-600 max-w-md leading-relaxed">
              Whether you have a project in mind or just want to say hi, my inbox is always open. I'll get back to you as soon as possible.
            </p>
          </div>
          <div className="space-y-6 pt-4">
            <div className="flex items-center gap-4">
              <div className="size-12 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                <span className="material-symbols-outlined">mail</span>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">Email</p>
                <p className="text-lg font-medium">hello@creative.com</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="size-12 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                <span className="material-symbols-outlined">location_on</span>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">Location</p>
                <p className="text-lg font-medium">San Francisco, CA</p>
              </div>
            </div>
          </div>
          <div className="pt-8">
            <p className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-4">Follow me</p>
            <div className="flex gap-4">
              {['Instagram', 'LinkedIn', 'Twitter'].map((p) => (
                <a key={p} className="group flex flex-col items-center gap-2" href="#">
                  <div className="size-11 rounded-full border border-gray-200 flex items-center justify-center transition-all group-hover:bg-primary group-hover:border-primary group-hover:text-white text-gray-600">
                    <span className="material-symbols-outlined !text-[20px]">
                      {p === 'Instagram' ? 'photo_camera' : p === 'LinkedIn' ? 'work' : 'alternate_email'}
                    </span>
                  </div>
                  <span className="text-[10px] font-bold uppercase tracking-tighter opacity-0 group-hover:opacity-100 transition-opacity">{p}</span>
                </a>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-white p-8 md:p-10 rounded-xl border border-gray-100 shadow-sm">
          <form className="space-y-6" onSubmit={(e) => e.preventDefault()}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-gray-700" htmlFor="name">Name</label>
                <input className="w-full px-4 py-3 rounded-lg border-gray-200 bg-transparent focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none text-sm" id="name" placeholder="John Doe" type="text"/>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-semibold text-gray-700" htmlFor="email">Email Address</label>
                <input className="w-full px-4 py-3 rounded-lg border-gray-200 bg-transparent focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none text-sm" id="email" placeholder="john@example.com" type="email"/>
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-700" htmlFor="subject">Subject</label>
              <select className="w-full px-4 py-3 rounded-lg border-gray-200 bg-transparent focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none text-sm" id="subject">
                <option>General Inquiry</option>
                <option>New Project Proposal</option>
                <option>Collaboration</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-700" htmlFor="message">Message</label>
              <textarea className="w-full px-4 py-3 rounded-lg border-gray-200 bg-transparent focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none text-sm resize-none" id="message" placeholder="Tell me about your project..." rows={5}></textarea>
            </div>
            <button className="w-full py-4 bg-primary text-white rounded-lg font-bold text-sm tracking-wide transition-all hover:bg-primary/90 flex items-center justify-center gap-2 group" type="submit">
              Send Message
              <span className="material-symbols-outlined !text-[18px] group-hover:translate-x-1 transition-transform">send</span>
            </button>
          </form>
        </div>
      </div>
    </main>
  );
};

export default Contact;
