'use client'

import { useEffect, useState } from 'react'

export default function LiveMetrics() {
  const [metrics, setMetrics] = useState({
    vehiclesExported: 0,
    verifiedBuyers: 0,
    activeCountries: 0,
    dealsCompleted: 0
  })

  // Animate numbers on mount
  useEffect(() => {
    const targetMetrics = {
      vehiclesExported: 2847,
      verifiedBuyers: 156,
      activeCountries: 8,
      dealsCompleted: 1923
    }

    const duration = 2000
    const steps = 60
    const interval = duration / steps

    let currentStep = 0
    const timer = setInterval(() => {
      currentStep++
      const progress = currentStep / steps

      setMetrics({
        vehiclesExported: Math.floor(targetMetrics.vehiclesExported * progress),
        verifiedBuyers: Math.floor(targetMetrics.verifiedBuyers * progress),
        activeCountries: Math.floor(targetMetrics.activeCountries * progress),
        dealsCompleted: Math.floor(targetMetrics.dealsCompleted * progress)
      })

      if (currentStep >= steps) {
        clearInterval(timer)
        setMetrics(targetMetrics)
      }
    }, interval)

    return () => clearInterval(timer)
  }, [])

  const metricCards = [
    {
      value: metrics.vehiclesExported.toLocaleString(),
      label: 'Vehicles Exported',
      icon: '🚗',
      color: 'from-blue-500 to-blue-600'
    },
    {
      value: metrics.verifiedBuyers.toLocaleString(),
      label: 'Verified Buyers',
      icon: '✓',
      color: 'from-green-500 to-green-600'
    },
    {
      value: metrics.activeCountries.toLocaleString(),
      label: 'Active Countries',
      icon: '🌍',
      color: 'from-purple-500 to-purple-600'
    },
    {
      value: metrics.dealsCompleted.toLocaleString(),
      label: 'Deals Completed',
      icon: '🤝',
      color: 'from-orange-500 to-orange-600'
    }
  ]

  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl sm:text-5xl font-extrabold text-gray-900 mb-4">
            Live Platform Metrics
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Real-time data showing the growth and reach of the Nzila Export Hub
          </p>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {metricCards.map((metric, index) => (
            <div
              key={index}
              className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition duration-300 p-8 text-center transform hover:-translate-y-1"
            >
              {/* Icon */}
              <div className="text-5xl mb-4">
                {metric.icon}
              </div>

              {/* Value */}
              <div className={`text-4xl font-extrabold bg-gradient-to-r ${metric.color} bg-clip-text text-transparent mb-2`}>
                {metric.value}+
              </div>

              {/* Label */}
              <div className="text-gray-600 font-medium">
                {metric.label}
              </div>
            </div>
          ))}
        </div>

        {/* Geographic Reach */}
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Active Export Corridors
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* From Canada */}
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-4 flex items-center gap-2">
                <span>🇨🇦</span> From Canada
              </h4>
              <ul className="space-y-2 text-gray-600">
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                  Toronto, ON
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                  Montreal, QC
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                  Vancouver, BC
                </li>
              </ul>
            </div>

            {/* To West Africa */}
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-4 flex items-center gap-2">
                <span>🌍</span> To West Africa
              </h4>
              <ul className="space-y-2 text-gray-600">
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  Lagos, Nigeria 🇳🇬
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  Abidjan, Côte d'Ivoire 🇨🇮
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  Accra, Ghana 🇬🇭
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  Dakar, Senegal 🇸🇳
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
