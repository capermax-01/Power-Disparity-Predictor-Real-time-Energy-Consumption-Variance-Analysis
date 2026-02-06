
import React from 'react';
import { ARTICLES } from '../constants';

const Blog: React.FC = () => {
  return (
    <main className="flex-1 py-40">
      <div className="mx-auto max-w-[960px] px-6">
        <div className="mb-10 text-center md:text-left">
          <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-4">Blog & Insights</h2>
          <p className="text-[#636f88] text-lg max-w-2xl leading-relaxed">
            Thoughtful explorations of interface design, creative strategy, and the intersection of technology and human psychology.
          </p>
        </div>
        
        <div className="relative mb-16">
          <div className="group flex w-full items-center rounded-xl bg-white border border-[#f0f2f4] shadow-sm transition-all focus-within:ring-2 focus-within:ring-primary/20">
            <div className="flex items-center justify-center pl-5 text-[#636f88]">
              <span className="material-symbols-outlined">search</span>
            </div>
            <input className="w-full border-none bg-transparent px-4 py-4 text-base focus:ring-0 placeholder:text-[#636f88]" placeholder="Search through 150+ articles..." type="text"/>
          </div>
        </div>

        <div className="flex flex-col gap-16 md:gap-20">
          {ARTICLES.map((article) => (
            <article key={article.id} className="group flex flex-col md:flex-row gap-6 md:items-start">
              <div className="aspect-square w-full md:w-[180px] shrink-0 overflow-hidden rounded-xl bg-gray-100">
                <img className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105" src={article.image} alt={article.title} />
              </div>
              <div className="flex flex-1 flex-col">
                <span className="mb-2 text-xs font-semibold uppercase tracking-widest text-[#636f88]">{article.date}</span>
                <h3 className="mb-3 text-2xl font-bold leading-tight group-hover:text-primary transition-colors">
                  <a href="#">{article.title}</a>
                </h3>
                <p className="mb-4 text-[#636f88] leading-relaxed line-clamp-2">{article.description}</p>
                <a className="text-sm font-bold text-primary flex items-center gap-1 group/link" href="#">
                  Read article
                  <span className="material-symbols-outlined text-sm transition-transform group-hover/link:translate-x-1">arrow_forward</span>
                </a>
              </div>
            </article>
          ))}
        </div>

        <div className="mt-20 flex justify-center">
          <button className="rounded-lg border-2 border-primary/20 px-8 py-3 text-sm font-bold text-primary hover:bg-primary/5 transition-colors">
            View older entries
          </button>
        </div>
      </div>

      <section className="mt-24 bg-white border-t border-[#f0f2f4]">
        <div className="mx-auto max-w-[960px] px-6 py-20 text-center">
          <div className="mb-8 inline-flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
            <span className="material-symbols-outlined">mail</span>
          </div>
          <h2 className="mb-3 text-3xl font-bold">Stay Updated</h2>
          <p className="mx-auto mb-10 max-w-md text-[#636f88]">
            Join 2,000+ designers and developers. Get a monthly digest of my latest articles and curated resources.
          </p>
          <form className="mx-auto flex max-w-lg flex-col gap-3 sm:flex-row">
            <input className="flex-1 rounded-lg border-[#f0f2f4] bg-background-light px-4 py-3 text-base focus:border-primary focus:ring-primary/20" placeholder="email@example.com" required type="email"/>
            <button className="rounded-lg bg-primary px-8 py-3 font-bold text-white hover:bg-primary/90 transition-all" type="submit">
              Subscribe
            </button>
          </form>
        </div>
      </section>
    </main>
  );
};

export default Blog;
