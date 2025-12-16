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
    <section className="py-24 relative overflow-hidden">
      {/* Background with gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-slate-50 to-white"></div>
      
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-20">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber-500/10 border border-amber-500/20 mb-6">
            <span className="text-amber-600 font-semibold">👥 Testimonials</span>
          </div>
          <h2 className="text-4xl sm:text-5xl font-extrabold text-slate-900 mb-6">
            Trusted by Industry Leaders
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
            Hear from dealers and brokers who are growing their international business with Nzila
          </p>
        </div>

        {/* Testimonials */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20">
          {testimonials.map((testimonial, index) => (
            <div
              key={index}
              className="group relative bg-white border-2 border-slate-200 rounded-2xl p-8 hover:shadow-2xl hover:scale-105 hover:border-amber-500/50 transition-all duration-300"
            >
              {/* Quote mark accent */}
              <div className="absolute -top-4 -left-4 w-12 h-12 bg-gradient-to-br from-amber-500 to-amber-600 rounded-full flex items-center justify-center text-white text-3xl font-bold shadow-lg">
                "
              </div>

              {/* Quote */}
              <p className="text-slate-700 mb-8 leading-relaxed italic pt-4">
                {testimonial.quote}
              </p>

              {/* Author */}
              <div className="flex items-center gap-4 pt-4 border-t-2 border-slate-100">
                <div className="w-16 h-16 bg-gradient-to-br from-amber-500/20 to-amber-600/20 rounded-full flex items-center justify-center text-3xl">
                  {testimonial.image}
                </div>
                <div>
                  <div className="font-bold text-slate-900 text-lg">{testimonial.author}</div>
                  <div className="text-sm text-slate-600 font-medium">{testimonial.role}</div>
                  <div className="text-xs text-slate-500">{testimonial.location}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Partner Badges */}
        <div className="relative bg-gradient-to-r from-slate-900 to-amber-900 rounded-3xl p-12 overflow-hidden shadow-2xl">
          <div className="absolute inset-0 opacity-10">
            <img src="https://images.unsplash.com/photo-1578575437130-527eed3abbec?q=80&w=2070" alt="Background" className="w-full h-full object-cover" />
          </div>
          <div className="relative z-10">
            <h3 className="text-3xl font-bold text-white mb-10 text-center">
              Recognized & Supported By
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {partners.map((partner, index) => (
                <div
                  key={index}
                  className="bg-white/10 backdrop-blur-sm border-2 border-white/20 rounded-xl p-6 text-center hover:bg-white/20 hover:scale-105 transition-all duration-300"
                >
                  <div className="text-4xl mb-3">{partner.badge}</div>
                  <div className="font-bold text-white mb-1">{partner.name}</div>
                  <div className="text-xs text-slate-300">{partner.description}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Association Logos Placeholder */}
        <div className="mt-12 text-center">
          <p className="text-sm text-slate-500 mb-6">Member of:</p>
          <div className="flex flex-wrap justify-center items-center gap-8">
            <div className="bg-white border-2 border-slate-200 px-8 py-4 rounded-xl hover:shadow-lg transition-all duration-300">
              <span className="font-semibold text-slate-700">Canadian Auto Dealers Assoc.</span>
            </div>
            <div className="bg-white border-2 border-slate-200 px-8 py-4 rounded-xl hover:shadow-lg transition-all duration-300">
              <span className="font-semibold text-slate-700">West African Trade Council</span>
            </div>
            <div className="bg-white border-2 border-slate-200 px-8 py-4 rounded-xl hover:shadow-lg transition-all duration-300">
              <span className="font-semibold text-slate-700">International Shipping Alliance</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
