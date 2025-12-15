'use client'

export default function Testimonials() {
  const testimonials = [
    {
      quote: "Nzila transformed our export business. We've successfully shipped 47 vehicles to Nigeria in just 6 months with zero issues.",
      author: "Michael Chen",
      role: "Owner, Toronto Auto Exports",
      location: "Toronto, ON",
      image: "🚗"
    },
    {
      quote: "La plateforme bilingue rend tout tellement plus facile. Nous avons trouvé des acheteurs qualifiés en moins de 48 heures.",
      author: "Marie Dubois",
      role: "Directrice, Montréal Véhicules",
      location: "Montreal, QC",
      image: "🚙"
    },
    {
      quote: "As a broker, Nzila's automated commission system saves me hours every week. It's professional, transparent, and reliable.",
      author: "James Okonkwo",
      role: "Export Broker",
      location: "Vancouver, BC → Lagos",
      image: "🤝"
    }
  ]

  const partners = [
    {
      name: "IRAP Eligible",
      badge: "🏆",
      description: "Industrial Research Assistance Program"
    },
    {
      name: "CDAP Approved",
      badge: "✓",
      description: "Canada Digital Adoption Program"
    },
    {
      name: "MEIE Supported",
      badge: "🇨🇦",
      description: "Ministère de l'Économie"
    },
    {
      name: "Secure Platform",
      badge: "🔒",
      description: "Bank-grade encryption"
    }
  ]

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl sm:text-5xl font-extrabold text-gray-900 mb-4">
            Trusted by Industry Leaders
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Hear from dealers and brokers who are growing their international business with Nzila
          </p>
        </div>

        {/* Testimonials */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          {testimonials.map((testimonial, index) => (
            <div
              key={index}
              className="bg-gradient-to-br from-gray-50 to-white border-2 border-gray-200 rounded-2xl p-8 hover:shadow-xl transition duration-300"
            >
              {/* Quote Icon */}
              <div className="text-5xl text-nzila-green-500 mb-4">"</div>

              {/* Quote */}
              <p className="text-gray-700 mb-6 leading-relaxed">
                {testimonial.quote}
              </p>

              {/* Author */}
              <div className="flex items-center gap-4">
                <div className="text-4xl">
                  {testimonial.image}
                </div>
                <div>
                  <div className="font-bold text-gray-900">{testimonial.author}</div>
                  <div className="text-sm text-gray-600">{testimonial.role}</div>
                  <div className="text-xs text-gray-500">{testimonial.location}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Partner Badges */}
        <div className="bg-gradient-to-r from-nzila-blue-50 to-nzila-green-50 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">
            Recognized & Supported By
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {partners.map((partner, index) => (
              <div
                key={index}
                className="bg-white rounded-xl p-6 text-center hover:shadow-lg transition duration-300"
              >
                <div className="text-4xl mb-3">{partner.badge}</div>
                <div className="font-bold text-gray-900 mb-1">{partner.name}</div>
                <div className="text-xs text-gray-600">{partner.description}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Association Logos Placeholder */}
        <div className="mt-12 text-center">
          <p className="text-sm text-gray-500 mb-4">Member of:</p>
          <div className="flex flex-wrap justify-center items-center gap-8 opacity-50">
            <div className="bg-gray-100 px-8 py-4 rounded-lg">
              <span className="font-semibold text-gray-700">Canadian Auto Dealers Assoc.</span>
            </div>
            <div className="bg-gray-100 px-8 py-4 rounded-lg">
              <span className="font-semibold text-gray-700">West African Trade Council</span>
            </div>
            <div className="bg-gray-100 px-8 py-4 rounded-lg">
              <span className="font-semibold text-gray-700">International Shipping Alliance</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
