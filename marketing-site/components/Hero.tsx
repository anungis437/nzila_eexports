'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function Hero() {
  const [language, setLanguage] = useState<'en' | 'fr'>('en')

  const content = {
    en: {
      tagline: 'Export Smarter. Nzila Does the Heavy Lifting.',
      subtitle: 'The premier platform connecting Canadian vehicle dealers with verified West African buyers across Nigeria, Côte d\'Ivoire, Ghana, and beyond.',
      cta: 'Get Started',
      ctaSecondary: 'Watch Demo',
      trustedBy: 'Trusted by dealers across Canada'
    },
    fr: {
      tagline: 'Exportez Intelligemment. Nzila Fait le Travail Lourd.',
      subtitle: 'La plateforme de premier plan reliant les concessionnaires de véhicules canadiens aux acheteurs vérifiés d\'Afrique de l\'Ouest au Nigeria, en Côte d\'Ivoire, au Ghana et au-delà.',
      cta: 'Commencer',
      ctaSecondary: 'Voir la Démo',
      trustedBy: 'Approuvé par des concessionnaires partout au Canada'
    }
  }

  const t = content[language]

  return (
    <div className="relative bg-gradient-to-br from-nzila-blue-900 via-nzila-blue-800 to-nzila-green-900 text-white overflow-hidden">
      {/* Language Switcher */}
      <div className="absolute top-4 right-4 z-20 flex gap-2">
        <button
          onClick={() => setLanguage('en')}
          className={`px-3 py-1 rounded-md text-sm font-medium transition ${
            language === 'en' ? 'bg-white text-nzila-blue-900' : 'bg-white/20 hover:bg-white/30'
          }`}
        >
          EN
        </button>
        <button
          onClick={() => setLanguage('fr')}
          className={`px-3 py-1 rounded-md text-sm font-medium transition ${
            language === 'fr' ? 'bg-white text-nzila-blue-900' : 'bg-white/20 hover:bg-white/30'
          }`}
        >
          FR
        </button>
      </div>

      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <svg className="absolute h-full w-full" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
              <path d="M 32 0 L 0 0 0 32" fill="none" stroke="white" strokeWidth="0.5"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>
      </div>

      {/* Content */}
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
        <div className="text-center">
          {/* Logo/Brand */}
          <div className="mb-8">
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight mb-4">
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-nzila-green-400 to-white">
                Nzila
              </span>
              <span className="text-white"> Export Hub</span>
            </h1>
          </div>

          {/* Tagline */}
          <p className="text-3xl sm:text-4xl lg:text-5xl font-extrabold mb-6 text-balance">
            {t.tagline}
          </p>

          {/* Subtitle */}
          <p className="text-xl sm:text-2xl text-blue-100 mb-12 max-w-3xl mx-auto text-balance">
            {t.subtitle}
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
            <Link
              href="#contact"
              className="w-full sm:w-auto px-8 py-4 bg-nzila-green-500 hover:bg-nzila-green-600 text-white font-bold text-lg rounded-lg shadow-xl hover:shadow-2xl transform hover:scale-105 transition duration-200"
            >
              {t.cta} →
            </Link>
            <Link
              href="#how-it-works"
              className="w-full sm:w-auto px-8 py-4 bg-white/10 hover:bg-white/20 backdrop-blur-sm text-white font-bold text-lg rounded-lg border-2 border-white/30 transition duration-200"
            >
              {t.ctaSecondary}
            </Link>
          </div>

          {/* Trust Indicator */}
          <div className="text-center">
            <p className="text-sm text-blue-200 mb-4">{t.trustedBy}</p>
            <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
              <div className="bg-white/10 px-6 py-3 rounded-lg backdrop-blur-sm">
                <span className="text-sm font-semibold">🇨🇦 Canada</span>
              </div>
              <div className="bg-white/10 px-6 py-3 rounded-lg backdrop-blur-sm">
                <span className="text-sm font-semibold">🇳🇬 Nigeria</span>
              </div>
              <div className="bg-white/10 px-6 py-3 rounded-lg backdrop-blur-sm">
                <span className="text-sm font-semibold">🇨🇮 Côte d'Ivoire</span>
              </div>
              <div className="bg-white/10 px-6 py-3 rounded-lg backdrop-blur-sm">
                <span className="text-sm font-semibold">🇬🇭 Ghana</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Wave Divider */}
      <div className="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="w-full h-16 sm:h-24">
          <path d="M0,0 C300,100 900,100 1200,0 L1200,120 L0,120 Z" fill="white"/>
        </svg>
      </div>
    </div>
  )
}
