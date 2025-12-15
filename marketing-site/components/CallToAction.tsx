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
    <section id="contact" className="py-20 bg-gradient-to-br from-nzila-blue-900 via-nzila-blue-800 to-nzila-green-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left Column - CTA Text */}
          <div>
            <h2 className="text-4xl sm:text-5xl font-extrabold mb-6">
              Ready to Expand Your Export Business?
            </h2>
            <p className="text-xl text-blue-100 mb-8">
              Join hundreds of Canadian dealers already using Nzila to reach verified buyers across West Africa.
            </p>

            {/* Benefits List */}
            <ul className="space-y-4 mb-8">
              <li className="flex items-start gap-3">
                <span className="text-nzila-green-400 text-2xl flex-shrink-0">✓</span>
                <span>Access to pre-qualified buyers in 8+ African countries</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-nzila-green-400 text-2xl flex-shrink-0">✓</span>
                <span>Automated documentation and compliance workflows</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-nzila-green-400 text-2xl flex-shrink-0">✓</span>
                <span>Transparent commission tracking and instant payouts</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-nzila-green-400 text-2xl flex-shrink-0">✓</span>
                <span>Real-time shipment tracking from port to destination</span>
              </li>
            </ul>

            {/* Contact Options */}
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <span className="text-2xl">📧</span>
                <a href="mailto:info@nzilaexport.com" className="hover:text-nzila-green-400 transition">
                  info@nzilaexport.com
                </a>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-2xl">📞</span>
                <span>+1 (416) 555-NZILA (Canada)</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-2xl">🌍</span>
                <span>+234 (0) 1 555-8888 (Nigeria)</span>
              </div>
            </div>
          </div>

          {/* Right Column - Lead Capture Form */}
          <div className="bg-white rounded-2xl shadow-2xl p-8 text-gray-900">
            <h3 className="text-2xl font-bold mb-6">Get Started Today</h3>

            {submitted ? (
              <div className="bg-green-50 border-2 border-green-500 rounded-lg p-6 text-center">
                <div className="text-5xl mb-4">✓</div>
                <div className="text-xl font-bold text-green-800 mb-2">Thank You!</div>
                <div className="text-green-700">We'll be in touch within 24 hours.</div>
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
