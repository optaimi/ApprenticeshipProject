import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'JH Product Validation',
  description: 'Validate products against head office data',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        <div className="min-h-screen">
          {children}
        </div>
      </body>
    </html>
  )
}
