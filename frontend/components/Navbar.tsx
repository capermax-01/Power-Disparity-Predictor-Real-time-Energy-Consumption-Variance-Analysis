
import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar: React.FC = () => {
  const location = useLocation();
  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-6 lg:px-20 bg-background-light/80 backdrop-blur-md border-b border-black/5">
      <div className="flex items-center gap-3">
        <Link to="/" className="flex items-center gap-3">
          <div className="size-6 text-primary">
            <svg fill="currentColor" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
              <path d="M44 11.2727C44 14.0109 39.8386 16.3957 33.69 17.6364C39.8386 18.877 44 21.2618 44 24C44 26.7382 39.8386 29.123 33.69 30.3636C39.8386 31.6043 44 33.9891 44 36.7273C44 40.7439 35.0457 44 24 44C12.9543 44 4 40.7439 4 36.7273C4 33.9891 8.16144 31.6043 14.31 30.3636C8.16144 29.123 4 26.7382 4 24C4 21.2618 8.16144 18.877 14.31 17.6364C8.16144 16.3957 4 14.0109 4 11.2727C4 7.25611 12.9543 4 24 4C35.0457 4 44 7.25611 44 11.2727Z"></path>
            </svg>
          </div>
          <h2 className="text-lg font-bold tracking-tight">Alex Rivera</h2>
        </Link>
      </div>
      <nav className="hidden md:flex items-center gap-10">
        <Link className={`text-sm font-medium hover:text-primary transition-colors ${isActive('/work') ? 'text-primary' : ''}`} to="/work">Work</Link>
        <Link className={`text-sm font-medium hover:text-primary transition-colors ${isActive('/about') ? 'text-primary' : ''}`} to="/about">About</Link>
        <Link className={`text-sm font-medium hover:text-primary transition-colors ${isActive('/resume') ? 'text-primary' : ''}`} to="/resume">Resume</Link>
        <Link className={`text-sm font-medium hover:text-primary transition-colors ${isActive('/blog') ? 'text-primary' : ''}`} to="/blog">Blog</Link>
        <Link className={`text-sm font-medium hover:text-primary transition-colors ${isActive('/contact') ? 'text-primary' : ''}`} to="/contact">Contact</Link>
        <Link to="/contact" className="bg-primary hover:bg-primary/90 text-white px-6 py-2.5 rounded-lg text-sm font-bold tracking-wide transition-all">
          Let's Talk
        </Link>
      </nav>
      <button className="md:hidden">
        <span className="material-symbols-outlined">menu</span>
      </button>
    </header>
  );
};

export default Navbar;
