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
    <section id="how-it-works" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl sm:text-5xl font-extrabold text-gray-900 mb-4">
            How It Works
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            From listing to delivery, Nzila streamlines every step of the international vehicle export process
          </p>
        </div>

        {/* Steps */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              {/* Connector Line (hidden on mobile, last item) */}
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-16 left-full w-full h-0.5 bg-gradient-to-r from-gray-300 to-transparent -translate-x-1/2 z-0" />
              )}

              {/* Step Card */}
              <div className="relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition duration-300 p-8 z-10">
                {/* Step Number */}
                <div className={`inline-block bg-gradient-to-r ${step.color} text-white text-sm font-bold px-4 py-1 rounded-full mb-4`}>
                  {step.number}
                </div>

                {/* Icon */}
                <div className="text-5xl mb-4">
                  {step.icon}
                </div>

                {/* Title */}
                <h3 className="text-xl font-bold text-gray-900 mb-3">
                  {step.title}
                </h3>

                {/* Description */}
                <p className="text-gray-600 leading-relaxed">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Process Flow Illustration */}
        <div className="mt-16 text-center">
          <div className="inline-flex items-center gap-4 bg-white rounded-full px-8 py-4 shadow-lg">
            <span className="text-2xl">🇨🇦</span>
            <span className="text-gray-400">→</span>
            <span className="text-2xl">🚢</span>
            <span className="text-gray-400">→</span>
            <span className="text-2xl">🌍</span>
            <span className="text-gray-400">→</span>
            <span className="text-2xl">🇳🇬🇨🇮🇬🇭</span>
          </div>
        </div>
      </div>
    </section>
  )
}
