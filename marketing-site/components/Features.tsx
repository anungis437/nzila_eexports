'use client'

export default function Features() {
  const features = [
    {
      icon: '📋',
      title: 'Inventory Management',
      description: 'Centralized dashboard for all your vehicle listings with photos, specs, and pricing',
      color: 'bg-blue-50 border-blue-200'
    },
    {
      icon: '✓',
      title: 'Verified Buyer Network',
      description: 'Pre-screened, financially qualified buyers across West Africa',
      color: 'bg-green-50 border-green-200'
    },
    {
      icon: '💰',
      title: 'Automated Commissions',
      description: 'Transparent commission tracking and automated payouts for dealers and brokers',
      color: 'bg-purple-50 border-purple-200'
    },
    {
      icon: '🌍',
      title: 'Bilingual Interface',
      description: 'Full English and French support for seamless international communication',
      color: 'bg-indigo-50 border-indigo-200'
    },
    {
      icon: '📦',
      title: 'Shipment Tracking',
      description: 'Real-time GPS tracking from Canadian ports to African destinations',
      color: 'bg-orange-50 border-orange-200'
    },
    {
      icon: '📄',
      title: 'Document Management',
      description: 'Secure upload, verification, and storage of all export documentation',
      color: 'bg-teal-50 border-teal-200'
    },
    {
      icon: '📊',
      title: 'Admin Dashboard',
      description: 'Comprehensive analytics, reporting, and deal pipeline management',
      color: 'bg-pink-50 border-pink-200'
    },
    {
      icon: '🔒',
      title: 'Secure & Compliant',
      description: 'GDPR, PIPEDA, and Law 25 compliant with bank-grade encryption',
      color: 'bg-red-50 border-red-200'
    }
  ]

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl sm:text-5xl font-extrabold text-gray-900 mb-4">
            Platform Features
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Everything you need to manage international vehicle exports in one powerful platform
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className={`${feature.color} border-2 rounded-xl p-6 hover:shadow-lg transition duration-300 transform hover:-translate-y-1`}
            >
              {/* Icon */}
              <div className="text-4xl mb-4">
                {feature.icon}
              </div>

              {/* Title */}
              <h3 className="text-lg font-bold text-gray-900 mb-2">
                {feature.title}
              </h3>

              {/* Description */}
              <p className="text-gray-600 text-sm leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* Additional Features Banner */}
        <div className="mt-16 bg-gradient-to-r from-nzila-blue-900 to-nzila-green-900 rounded-2xl p-8 text-center text-white">
          <h3 className="text-2xl font-bold mb-4">Built for International Trade</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <div className="text-3xl font-extrabold mb-2">24/7</div>
              <div className="text-sm text-blue-100">Support</div>
            </div>
            <div>
              <div className="text-3xl font-extrabold mb-2">Multi-Currency</div>
              <div className="text-sm text-blue-100">CAD, USD, XOF</div>
            </div>
            <div>
              <div className="text-3xl font-extrabold mb-2">AI-Powered</div>
              <div className="text-sm text-blue-100">Lead Scoring</div>
            </div>
            <div>
              <div className="text-3xl font-extrabold mb-2">Automated</div>
              <div className="text-sm text-blue-100">Workflows</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
