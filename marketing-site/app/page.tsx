import Header from '@/components/Header'
import Hero from '@/components/Hero'
import HowItWorks from '@/components/HowItWorks'
import Features from '@/components/Features'
import LiveMetrics from '@/components/LiveMetrics'
import Testimonials from '@/components/Testimonials'
import CallToAction from '@/components/CallToAction'
import Footer from '@/components/Footer'

export default function Home() {
  return (
    <>
      <Header />
      <main className="min-h-screen">
        <Hero />
        <HowItWorks />
        <Features />
        <LiveMetrics />
        <Testimonials />
        <CallToAction />
        <Footer />
      </main>
    </>
  )
}
