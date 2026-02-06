
import React from 'react';
import { Link } from 'react-router-dom';

const Footer: React.FC = () => {
  return (
    <footer className="bg-background-light py-20 px-6 lg:px-20 text-center border-t border-black/5">
      <div className="max-w-2xl mx-auto space-y-6">
        <h2 className="text-4xl lg:text-5xl font-black tracking-tight">Interested in working together?</h2>
        <p className="text-lg text-[#111318]/60">I'm currently available for freelance projects and full-time opportunities.</p>
        <div className="flex justify-center pt-4">
          <Link to="/contact" className="flex min-w-[200px] items-center justify-center rounded-lg h-14 px-10 bg-primary text-white text-base font-bold tracking-wide hover:shadow-xl hover:shadow-primary/30 transition-all">
            Get in Touch
          </Link>
        </div>
        <div className="flex justify-center items-center gap-6 pt-12 text-[#111318]/40">
          <p className="text-sm font-medium">© 2024 Alex Rivera</p>
          <span className="size-1 rounded-full bg-black/20"></span>
          <p className="text-sm font-medium">San Francisco, CA</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
