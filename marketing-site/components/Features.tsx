'use client'

export default function Features() {
  const features = [
    {
      icon: '�',
      title: 'Inventory Management',
      description: 'Centralized dashboard for all your vehicle listings with photos, specs, and pricing',
      gradient: 'from-blue-500 to-blue-600',
      iconBg: 'bg-blue-500/10',
      borderColor: 'border-blue-500/20'
    },
    {
      icon: '✓',
      title: 'Verified Buyer Network',
      description: 'Pre-screened, financially qualified buyers across West Africa',
      gradient: 'from-emerald-500 to-emerald-600',
      iconBg: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/20'
    },
    {
      icon: '💰',
      title: 'Automated Commissions',
      description: 'Transparent commission tracking and automated payouts for dealers and brokers',
      gradient: 'from-amber-500 to-amber-600',
      iconBg: 'bg-amber-500/10',
      borderColor: 'border-amber-500/20'
    },
    {
      icon: '🌍',
      title: 'Bilingual Interface',
      description: 'Full English and French support for seamless international communication',
      gradient: 'from-purple-500 to-purple-600',
      iconBg: 'bg-purple-500/10',
      borderColor: 'border-purple-500/20'
    },
    {
      icon: '📦',
      title: 'Shipment Tracking',
      description: 'Real-time GPS tracking from Canadian ports to African destinations',
      gradient: 'from-orange-500 to-orange-600',
      iconBg: 'bg-orange-500/10',
      borderColor: 'border-orange-500/20'
    },
    {
      icon: '📄',
      title: 'Document Management',
      description: 'Secure upload, verification, and storage of all export documentation',
      gradient: 'from-teal-500 to-teal-600',
      iconBg: 'bg-teal-500/10',
      borderColor: 'border-teal-500/20'
    },
    {
      icon: '📊',
      title: 'Admin Dashboard',
      description: 'Comprehensive analytics, reporting, and deal pipeline management',
      gradient: 'from-pink-500 to-pink-600',
      iconBg: 'bg-pink-500/10',
      borderColor: 'border-pink-500/20'
    },
    {
      icon: '🔒',
      title: 'Secure & Compliant',
      description: 'GDPR, PIPEDA, and Law 25 compliant with bank-grade encryption',
      gradient: 'from-red-500 to-red-600',
      iconBg: 'bg-red-500/10',
      borderColor: 'border-red-500/20'
    }
  ]

  return (
    <section className="py-24 bg-gradient-to-b from-white to-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-20">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber-500/10 border border-amber-500/20 mb-6">
            <span className="text-amber-600 font-semibold">🎯 Features</span>
          </div>
          <h2 className="text-4xl sm:text-5xl font-extrabold text-slate-900 mb-6">
            Everything You Need to Scale Your Export Business
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
            A complete platform built specifically for international vehicle exports from Canada to West Africa
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className={`group relative p-8 rounded-2xl bg-white border-2 ${feature.borderColor} hover:shadow-2xl hover:scale-105 transition-all duration-300`}
            >
              {/* Icon */}
              <div className={`inline-flex items-center justify-center w-16 h-16 rounded-xl ${feature.iconBg} mb-5 group-hover:scale-110 transition-transform`}>
                <span className="text-4xl">{feature.icon}</span>
              </div>
              
              {/* Gradient accent */}
              <div className={`absolute top-0 right-0 w-20 h-20 bg-gradient-to-br ${feature.gradient} opacity-5 rounded-bl-full`}></div>
              
              <h3 className="text-xl font-bold text-slate-900 mb-3">{feature.title}</h3>
              <p className="text-slate-600 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* Additional Features Banner */}
        <div className="mt-20 relative overflow-hidden bg-gradient-to-r from-slate-900 via-amber-900 to-slate-900 rounded-3xl p-12 text-center text-white shadow-2xl">
          <div className="absolute inset-0 opacity-10">
            <img src="https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?q=80&w=2070" alt="Background" className="w-full h-full object-cover" />
          </div>
          <div className="relative z-10">
            <h3 className="text-3xl font-bold mb-8">Built for International Trade</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              <div className="group">
                <div className="text-4xl font-extrabold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-amber-400 to-amber-200 group-hover:scale-110 transition-transform inline-block">24/7</div>
                <div className="text-sm text-slate-300">Support</div>
              </div>
              <div className="group">
                <div className="text-4xl font-extrabold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-emerald-200 group-hover:scale-110 transition-transform inline-block">Multi</div>
                <div className="text-sm text-slate-300">Currency: CAD, USD, XOF</div>
              </div>
              <div className="group">
                <div className="text-4xl font-extrabold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-blue-200 group-hover:scale-110 transition-transform inline-block">AI</div>
                <div className="text-sm text-slate-300">Powered Lead Scoring</div>
              </div>
              <div className="group">
                <div className="text-4xl font-extrabold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-purple-200 group-hover:scale-110 transition-transform inline-block">Auto</div>
                <div className="text-sm text-slate-300">Automated Workflows</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
