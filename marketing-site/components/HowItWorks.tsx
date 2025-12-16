'use client'

export default function HowItWorks() {
  const steps = [
    {
      number: '01',
      icon: '🚗',
      title: 'List Your Inventory',
      description: 'Canadian dealers upload vehicle details, photos, and documentation to the secure platform.',
      color: 'from-blue-500 to-blue-600'
    },
    {
      number: '02',
      icon: '✓',
      title: 'Verification & Matching',
      description: 'Our team verifies listings and connects you with pre-qualified, verified West African buyers.',
      color: 'from-nzila-green-500 to-nzila-green-600'
    },
    {
      number: '03',
      icon: '🤝',
      title: 'Deal & Documentation',
      description: 'Brokers facilitate negotiations. Automated workflows handle contracts, payments, and export paperwork.',
      color: 'from-purple-500 to-purple-600'
    },
    {
      number: '04',
      icon: '📦',
      title: 'Ship & Track',
      description: 'Real-time shipment tracking from Canadian ports to West African destinations. Complete transparency.',
      color: 'from-orange-500 to-orange-600'
    }
  ]

  return (
    <section id="how-it-works" className="relative py-24 bg-slate-900 overflow-hidden">
      {/* Background Image */}
      <div className="absolute inset-0 z-0 opacity-10">
        <img 
          src="https://images.unsplash.com/photo-1580674684081-7617fbf3d745?q=80&w=2070" 
          alt="African highway"
          className="w-full h-full object-cover"
        />
      </div>
      
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-20">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber-500/20 border border-amber-500/30 backdrop-blur-sm mb-6">
            <span className="text-amber-400 font-semibold">⚙️ Process</span>
          </div>
          <h2 className="text-4xl sm:text-5xl font-extrabold text-white mb-6">
            How It Works
          </h2>
          <p className="text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed">
            From listing to delivery, Nzila streamlines every step of the international vehicle export process
          </p>
        </div>

        {/* Steps */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <div key={index} className="relative group">
              {/* Connector Arrow (hidden on mobile, last item) */}
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-20 left-1/2 w-full h-1 -z-10">
                  <div className="absolute inset-0 bg-gradient-to-r from-amber-500/30 to-transparent"></div>
                  <div className="absolute right-0 top-1/2 -translate-y-1/2 w-0 h-0 border-l-8 border-l-amber-500/30 border-y-4 border-y-transparent"></div>
                </div>
              )}
              
              <div className="relative bg-white/10 backdrop-blur-md rounded-2xl p-8 border-2 border-white/20 hover:bg-white/20 hover:border-amber-500/50 hover:scale-105 transition-all duration-300 shadow-2xl">
                {/* Step Number Badge */}
                <div className={`absolute -top-4 -right-4 flex items-center justify-center w-14 h-14 rounded-full bg-gradient-to-br ${step.color} text-white font-bold text-xl shadow-lg`}>
                  {step.number}
                </div>
                
                {/* Icon */}
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-white/10 border border-white/20 mb-6 group-hover:scale-110 transition-transform">
                  <span className="text-5xl">{step.icon}</span>
                </div>
                
                {/* Content */}
                <h3 className="text-2xl font-bold text-white mb-4">{step.title}</h3>
                <p className="text-slate-300 leading-relaxed">{step.description}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Process Flow Illustration */}
        <div className="mt-20 text-center">
          <div className="inline-flex items-center gap-6 bg-white/10 backdrop-blur-md border-2 border-white/20 rounded-full px-12 py-6 shadow-2xl">
            <span className="text-4xl animate-pulse">🇨🇦</span>
            <span className="text-amber-400 text-2xl">→</span>
            <span className="text-4xl">🚢</span>
            <span className="text-amber-400 text-2xl">→</span>
            <span className="text-4xl">🌍</span>
            <span className="text-amber-400 text-2xl">→</span>
            <span className="text-4xl animate-pulse">🇳🇬 🇨🇮 🇬🇭</span>
          </div>
          <p className="mt-6 text-slate-300 font-semibold">Canada to West Africa in 4 Simple Steps</p>
        </div>
      </div>
    </section>
  )
}
