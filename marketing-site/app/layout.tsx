import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

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
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
