import type { Metadata } from 'next'
import { Poppins } from 'next/font/google'
import './globals.css'

const poppins = Poppins({ 
  weight: ['300', '400', '500', '600', '700'],
  subsets: ['latin'],
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Nzila Export Hub - Connect Canadian Dealers with West African Buyers',
  description: 'Export Smarter. Nzila Does the Heavy Lifting. The premier platform for vehicle exports from Canada to West Africa.',
  keywords: 'vehicle export, Canada to Africa, auto trade, West Africa vehicles, Canadian dealers, export platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={poppins.className}>{children}</body>
    </html>
  )
}
