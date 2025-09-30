import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Providers } from './providers'
import { Navigation } from '@/components/layout/Navigation'
import { Footer } from '@/components/layout/Footer'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Neurosurgical Knowledge Management System',
  description: 'Advanced AI-powered platform for neurosurgical knowledge synthesis, management, and clinical decision support',
  keywords: 'neurosurgery, brain surgery, spine surgery, medical knowledge, AI synthesis, clinical guidelines',
  authors: [{ name: 'Neurosurgical Knowledge Team' }],
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#1976d2',
  manifest: '/manifest.json',
  icons: {
    icon: '/favicon.ico',
    apple: '/apple-icon.png',
  },
  openGraph: {
    title: 'Neurosurgical Knowledge Management System',
    description: 'Comprehensive platform for neurosurgical education and practice',
    type: 'website',
    locale: 'en_US',
    siteName: 'NeuroKnowledge',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          <div className="flex min-h-screen flex-col">
            <Navigation />
            <main className="flex-1 bg-gray-50">
              {children}
            </main>
            <Footer />
          </div>
        </Providers>
      </body>
    </html>
  )
}