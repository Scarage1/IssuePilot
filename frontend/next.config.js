/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  // Enable experimental features for better performance
  experimental: {
    optimizePackageImports: ['lucide-react', 'framer-motion'],
  },
}

module.exports = nextConfig
