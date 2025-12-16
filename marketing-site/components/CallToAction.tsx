'use client'

import { useState } from 'react'

export default function CallToAction() {
  const [email, setEmail] = useState('')
  const [role, setRole] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // In production, this would send to your backend/Supabase
    console.log('Form submitted:', { email, role })
    setSubmitted(true)
    setTimeout(() => {
      setSubmitted(false)
      setEmail('')
      setRole('')
    }, 3000)
  }

  return (
    <section id="contact" className="relative py-24 overflow-hidden">
      {/* Background Image with Overlay */}
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900/95 via-slate-900/90 to-amber-900/90 z-10"></div>
        <img 
          src="https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?q=80&w=2070" 
          alt="Luxury vehicles"
          className="w-full h-full object-cover"
        />
      </div>
      
      <div className="relative z-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left Column - CTA Text */}
          <div>
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber-500/20 border border-amber-500/30 backdrop-blur-sm mb-6">
              <span className="text-amber-400 font-semibold">🚀 Get Started</span>
            </div>
            <h2 className="text-4xl sm:text-5xl font-extrabold mb-6 text-white">
              Ready to Expand Your Export Business?
            </h2>
            <p className="text-xl text-slate-200 mb-10 leading-relaxed">
              Join hundreds of Canadian dealers already using Nzila to reach verified buyers across West Africa.
            </p>

            {/* Benefits List */}
            <ul className="space-y-5 mb-10">
              <li className="flex items-start gap-4 group">
                <span className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-lg flex items-center justify-center text-white font-bold group-hover:scale-110 transition-transform">✓</span>
                <span className="text-slate-100">Access to pre-qualified buyers in 8+ African countries</span>
              </li>
              <li className="flex items-start gap-4 group">
                <span className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-lg flex items-center justify-center text-white font-bold group-hover:scale-110 transition-transform">✓</span>
                <span className="text-slate-100">Automated documentation and compliance workflows</span>
              </li>
              <li className="flex items-start gap-4 group">
                <span className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-lg flex items-center justify-center text-white font-bold group-hover:scale-110 transition-transform">✓</span>
                <span className="text-slate-100">Transparent commission tracking and instant payouts</span>
              </li>
              <li className="flex items-start gap-4 group">
                <span className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-lg flex items-center justify-center text-white font-bold group-hover:scale-110 transition-transform">✓</span>
                <span className="text-slate-100">Real-time shipment tracking from port to destination</span>
              </li>
            </ul>

            {/* Contact Options */}
            <div className="space-y-4 bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-6">
              <div className="flex items-center gap-4 group">
                <span className="text-3xl group-hover:scale-110 transition-transform">📧</span>
                <a href="mailto:info@nzilaexport.com" className="text-white hover:text-amber-400 transition font-medium">
                  info@nzilaexport.com
                </a>
              </div>
              <div className="flex items-center gap-4 group">
                <span className="text-3xl group-hover:scale-110 transition-transform">📞</span>
                <span className="text-slate-100 font-medium">+1 (416) 555-NZILA (Canada)</span>
              </div>
              <div className="flex items-center gap-4 group">
                <span className="text-3xl group-hover:scale-110 transition-transform">🌍</span>
                <span className="text-slate-100 font-medium">+234 (0) 1 555-8888 (Nigeria)</span>
              </div>
            </div>
          </div>

          {/* Right Column - Lead Capture Form */}
          <div className="bg-white rounded-2xl shadow-2xl p-10 text-gray-900 border-4 border-amber-500/20">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-amber-500 to-amber-600 rounded-2xl mb-4 shadow-lg">
                <span className="text-3xl">🚀</span>
              </div>
              <h3 className="text-3xl font-bold text-slate-900">Get Started Today</h3>
            </div>

            {submitted ? (
              <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 border-4 border-emerald-500 rounded-2xl p-8 text-center">
                <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-full text-white text-4xl mb-4 shadow-lg">✓</div>
                <div className="text-2xl font-bold text-emerald-800 mb-3">Thank You!</div>
                <div className="text-emerald-700 font-medium">We'll be in touch within 24 hours.</div>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Email */}
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address *
                  </label>
                  <input
                    type="email"
                    id="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-nzila-green-500 focus:border-transparent transition"
                    placeholder="your@email.com"
                  />
                </div>

                {/* Role */}
                <div>
                  <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-2">
                    I am a... *
                  </label>
                  <select
                    id="role"
                    required
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-nzila-green-500 focus:border-transparent transition"
                  >
                    <option value="">Select your role</option>
                    <option value="dealer">Vehicle Dealer</option>
                    <option value="broker">Export Broker</option>
                    <option value="buyer">West African Buyer</option>
                    <option value="investor">Investor/Funder</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                {/* Company */}
                <div>
                  <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-2">
                    Company Name (optional)
                  </label>
                  <input
                    type="text"
                    id="company"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-nzila-green-500 focus:border-transparent transition"
                    placeholder="Your Company"
                  />
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  className="w-full bg-gradient-to-r from-nzila-green-500 to-nzila-green-600 hover:from-nzila-green-600 hover:to-nzila-green-700 text-white font-bold py-4 rounded-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition duration-200"
                >
                  Request Access →
                </button>

                <p className="text-xs text-gray-500 text-center mt-4">
                  By submitting, you agree to our Terms of Service and Privacy Policy
                </p>
              </form>
            )}

            {/* Quick Links */}
            <div className="mt-6 pt-6 border-t border-gray-200 flex justify-center gap-4">
              <a href="#" className="text-sm text-nzila-blue-600 hover:underline">
                Dealer Onboarding
              </a>
              <span className="text-gray-300">|</span>
              <a href="#" className="text-sm text-nzila-blue-600 hover:underline">
                Apply as Broker
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
