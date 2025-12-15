'use client'

import { useState } from 'react'

export default function Footer() {
  const [language, setLanguage] = useState<'en' | 'fr'>('en')

  const content = {
    en: {
      company: 'Company',
      about: 'About Nzila',
      careers: 'Careers',
      press: 'Press Kit',
      contact: 'Contact Us',
      platform: 'Platform',
      dealers: 'For Dealers',
      brokers: 'For Brokers',
      buyers: 'For Buyers',
      pricing: 'Pricing',
      resources: 'Resources',
      docs: 'Documentation',
      api: 'API Reference',
      blog: 'Trade Blog',
      support: 'Support Center',
      legal: 'Legal',
      privacy: 'Privacy Policy',
      terms: 'Terms of Service',
      gdpr: 'GDPR Compliance',
      cookies: 'Cookie Policy',
      footer: 'Connecting Canadian vehicle dealers with verified West African buyers.',
      copyright: '© 2024 Nzila Export Hub. All rights reserved.',
      locations: 'Locations'
    },
    fr: {
      company: 'Entreprise',
      about: 'À propos de Nzila',
      careers: 'Carrières',
      press: 'Kit de presse',
      contact: 'Nous contacter',
      platform: 'Plateforme',
      dealers: 'Pour les concessionnaires',
      brokers: 'Pour les courtiers',
      buyers: 'Pour les acheteurs',
      pricing: 'Tarification',
      resources: 'Ressources',
      docs: 'Documentation',
      api: 'Référence API',
      blog: 'Blog commercial',
      support: 'Centre d\'assistance',
      legal: 'Légal',
      privacy: 'Politique de confidentialité',
      terms: 'Conditions d\'utilisation',
      gdpr: 'Conformité RGPD',
      cookies: 'Politique de cookies',
      footer: 'Connexion des concessionnaires de véhicules canadiens avec des acheteurs vérifiés d\'Afrique de l\'Ouest.',
      copyright: '© 2024 Nzila Export Hub. Tous droits réservés.',
      locations: 'Emplacements'
    }
  }

  const t = content[language]

  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 mb-8">
          {/* Brand Column */}
          <div className="lg:col-span-2">
            <div className="text-2xl font-bold text-white mb-4">
              <span className="text-nzila-green-400">Nzila</span> Export Hub
            </div>
            <p className="text-gray-400 mb-4">
              {t.footer}
            </p>
            {/* Language Switcher */}
            <div className="flex gap-2 mb-4">
              <button
                onClick={() => setLanguage('en')}
                className={`px-3 py-1 rounded text-sm font-medium transition ${
                  language === 'en'
                    ? 'bg-nzila-green-500 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                EN
              </button>
              <button
                onClick={() => setLanguage('fr')}
                className={`px-3 py-1 rounded text-sm font-medium transition ${
                  language === 'fr'
                    ? 'bg-nzila-green-500 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                FR
              </button>
            </div>
            {/* Social Links */}
            <div className="flex gap-4">
              <a href="#" className="text-gray-400 hover:text-white transition">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                </svg>
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
              </a>
            </div>
          </div>

          {/* Company Links */}
          <div>
            <h3 className="text-white font-semibold mb-4">{t.company}</h3>
            <ul className="space-y-2">
              <li><a href="#" className="hover:text-white transition">{t.about}</a></li>
              <li><a href="#" className="hover:text-white transition">{t.careers}</a></li>
              <li><a href="#" className="hover:text-white transition">{t.press}</a></li>
              <li><a href="#" className="hover:text-white transition">{t.contact}</a></li>
            </ul>
          </div>

          {/* Platform Links */}
          <div>
            <h3 className="text-white font-semibold mb-4">{t.platform}</h3>
            <ul className="space-y-2">
              <li><a href="#" className="hover:text-white transition">{t.dealers}</a></li>
              <li><a href="#" className="hover:text-white transition">{t.brokers}</a></li>
              <li><a href="#" className="hover:text-white transition">{t.buyers}</a></li>
              <li><a href="#" className="hover:text-white transition">{t.pricing}</a></li>
            </ul>
          </div>

          {/* Resources Links */}
          <div>
            <h3 className="text-white font-semibold mb-4">{t.resources}</h3>
            <ul className="space-y-2">
              <li><a href="#" className="hover:text-white transition">{t.docs}</a></li>
              <li><a href="#" className="hover:text-white transition">{t.api}</a></li>
              <li><a href="#" className="hover:text-white transition">{t.blog}</a></li>
              <li><a href="#" className="hover:text-white transition">{t.support}</a></li>
            </ul>
          </div>
        </div>

        {/* Locations Bar */}
        <div className="border-t border-gray-800 pt-8 mb-8">
          <h3 className="text-white font-semibold mb-4">{t.locations}</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <div className="font-semibold text-white mb-1">🇨🇦 Toronto, Canada</div>
              <div className="text-gray-500">123 Export Street, Toronto, ON M5H 2N2</div>
            </div>
            <div>
              <div className="font-semibold text-white mb-1">🇳🇬 Lagos, Nigeria</div>
              <div className="text-gray-500">Victoria Island, Lagos</div>
            </div>
            <div>
              <div className="font-semibold text-white mb-1">🇨🇮 Abidjan, Côte d'Ivoire</div>
              <div className="text-gray-500">Plateau, Abidjan</div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="text-sm text-gray-500">
            {t.copyright}
          </div>
          <div className="flex flex-wrap gap-4 text-sm">
            <a href="#" className="hover:text-white transition">{t.privacy}</a>
            <a href="#" className="hover:text-white transition">{t.terms}</a>
            <a href="#" className="hover:text-white transition">{t.gdpr}</a>
            <a href="#" className="hover:text-white transition">{t.cookies}</a>
          </div>
        </div>
      </div>
    </footer>
  )
}
