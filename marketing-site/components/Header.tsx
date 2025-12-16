'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function Header() {
  const [language, setLanguage] = useState<'en' | 'fr'>('en')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const content = {
    en: {
      features: 'Features',
      howItWorks: 'How It Works',
      testimonials: 'Testimonials',
      contact: 'Contact',
      signIn: 'Sign In',
      getStarted: 'Get Started'
    },
    fr: {
      features: 'Fonctionnalités',
      howItWorks: 'Comment Ça Marche',
      testimonials: 'Témoignages',
      contact: 'Contact',
      signIn: 'Se Connecter',
      getStarted: 'Commencer'
    }
  }

  const t = content[language]

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-12 h-12 bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-lg group-hover:scale-105 transition-transform">
              N
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-slate-900 to-amber-900 bg-clip-text text-transparent">
              Nzila Export
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-slate-700 hover:text-amber-600 font-medium transition">
              {t.features}
            </a>
            <a href="#how-it-works" className="text-slate-700 hover:text-amber-600 font-medium transition">
              {t.howItWorks}
            </a>
            <a href="#testimonials" className="text-slate-700 hover:text-amber-600 font-medium transition">
              {t.testimonials}
            </a>
            <a href="#contact" className="text-slate-700 hover:text-amber-600 font-medium transition">
              {t.contact}
            </a>

            <div className="flex gap-2">
              <button
                onClick={() => setLanguage('en')}
                className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition ${
                  language === 'en' 
                    ? 'bg-amber-500 text-white shadow-md' 
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                EN
              </button>
              <button
                onClick={() => setLanguage('fr')}
                className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition ${
                  language === 'fr' 
                    ? 'bg-amber-500 text-white shadow-md' 
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                FR
              </button>
            </div>

            <Link
              href="http://localhost:5173/login"
              className="text-slate-700 hover:text-amber-600 font-semibold transition flex items-center gap-2"
            >
              <span>🔐</span>
              {t.signIn}
            </Link>

            <Link
              href="http://localhost:5173/login"
              className="bg-gradient-to-r from-amber-500 to-amber-600 text-white px-6 py-2.5 rounded-lg font-bold hover:from-amber-600 hover:to-amber-700 transition-all shadow-lg hover:shadow-xl hover:scale-105 transform"
            >
              {t.getStarted}
            </Link>
          </div>

          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden text-slate-700 hover:text-amber-600 transition p-2"
          >
            {mobileMenuOpen ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>

        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-slate-200 bg-white">
            <div className="flex flex-col gap-4">
              <a 
                href="#features" 
                onClick={() => setMobileMenuOpen(false)}
                className="text-slate-700 hover:text-amber-600 font-medium transition px-4 py-2 hover:bg-slate-50 rounded-lg"
              >
                {t.features}
              </a>
              <a 
                href="#how-it-works" 
                onClick={() => setMobileMenuOpen(false)}
                className="text-slate-700 hover:text-amber-600 font-medium transition px-4 py-2 hover:bg-slate-50 rounded-lg"
              >
                {t.howItWorks}
              </a>
              <a 
                href="#testimonials" 
                onClick={() => setMobileMenuOpen(false)}
                className="text-slate-700 hover:text-amber-600 font-medium transition px-4 py-2 hover:bg-slate-50 rounded-lg"
              >
                {t.testimonials}
              </a>
              <a 
                href="#contact" 
                onClick={() => setMobileMenuOpen(false)}
                className="text-slate-700 hover:text-amber-600 font-medium transition px-4 py-2 hover:bg-slate-50 rounded-lg"
              >
                {t.contact}
              </a>

              <div className="flex gap-2 px-4 py-2">
                <button
                  onClick={() => setLanguage('en')}
                  className={`flex-1 px-3 py-2 rounded-lg text-sm font-semibold transition ${
                    language === 'en' 
                      ? 'bg-amber-500 text-white shadow-md' 
                      : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  EN
                </button>
                <button
                  onClick={() => setLanguage('fr')}
                  className={`flex-1 px-3 py-2 rounded-lg text-sm font-semibold transition ${
                    language === 'fr' 
                      ? 'bg-amber-500 text-white shadow-md' 
                      : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  FR
                </button>
              </div>

              <Link
                href="http://localhost:5173/login"
                onClick={() => setMobileMenuOpen(false)}
                className="text-slate-700 hover:text-amber-600 font-semibold transition px-4 py-2 hover:bg-slate-50 rounded-lg flex items-center gap-2"
              >
                <span>🔐</span>
                {t.signIn}
              </Link>

              <Link
                href="http://localhost:5173/login"
                onClick={() => setMobileMenuOpen(false)}
                className="bg-gradient-to-r from-amber-500 to-amber-600 text-white px-6 py-3 rounded-lg font-bold text-center shadow-lg mx-4"
              >
                {t.getStarted}
              </Link>
            </div>
          </div>
        )}
      </nav>
    </header>
  )
}
