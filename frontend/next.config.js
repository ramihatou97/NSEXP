/** @type {import('next').NextConfig} */

const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,

  // Neurosurgical-specific image domains
  images: {
    domains: [
      'localhost',
      'neurosurgicalknowledge.com',
      'pubmed.ncbi.nlm.nih.gov',
      'radiopaedia.org',
      'neurosurgicalatlas.com',
      's3.amazonaws.com',
    ],
    formats: ['image/avif', 'image/webp'],
  },

  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws',
    NEXT_PUBLIC_APP_NAME: 'Neurosurgical Knowledge Management System',
    NEXT_PUBLIC_APP_VERSION: '2.0.0',
  },

  // Webpack configuration
  webpack: (config, { isServer }) => {
    // Handle file system fallbacks for browser
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      path: false,
      crypto: false,
    }

    // Optimize for production
    if (!isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          default: false,
          vendors: false,
          visualization: {
            name: 'visualization',
            test: /[\\/]node_modules[\\/](d3|recharts|react-force-graph)/,
            priority: 20,
            reuseExistingChunk: true,
          },
          ui: {
            name: 'ui',
            test: /[\\/]node_modules[\\/](@mui|@emotion|framer-motion|@radix-ui)/,
            priority: 15,
            reuseExistingChunk: true,
          },
          editor: {
            name: 'editor',
            test: /[\\/]node_modules[\\/](@tiptap|lowlight)/,
            priority: 10,
            reuseExistingChunk: true,
          },
          common: {
            name: 'common',
            minChunks: 2,
            priority: 5,
            reuseExistingChunk: true,
          },
        },
      }
    }

    return config
  },

  // Experimental features for performance
  experimental: {
    optimizeCss: true,
    scrollRestoration: true,
  },

  // Headers for security
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Content-Security-Policy',
            value: process.env.NODE_ENV === 'production'
              ? "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https: wss:;"
              : "default-src 'self' 'unsafe-eval' 'unsafe-inline'; img-src 'self' data: https: blob:; connect-src 'self' http: https: ws: wss:;",
          },
        ],
      },
      // CORS headers for medical image viewing
      {
        source: '/api/images/:path*',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: '*',
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET, OPTIONS',
          },
        ],
      },
    ]
  },

  // Redirects for legacy routes
  async redirects() {
    return [
      {
        source: '/chapters',
        destination: '/library',
        permanent: true,
      },
      {
        source: '/synthesis',
        destination: '/create',
        permanent: true,
      },
    ]
  },

  // Rewrites for API proxy
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/:path*`,
      },
    ]
  },

  // Performance monitoring
  poweredByHeader: false,
  compress: true,
  generateEtags: true,

  // Build output
  output: 'standalone',
  distDir: '.next',

  // TypeScript
  typescript: {
    ignoreBuildErrors: false,
  },

  // ESLint
  eslint: {
    ignoreDuringBuilds: false,
  },
}

module.exports = withBundleAnalyzer(nextConfig)