/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  pageExtensions: ['ts', 'tsx'],
  output: 'standalone', // <--- ADD THIS LINE
}

module.exports = nextConfig