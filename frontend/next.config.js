/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
    dirs: [], // Disable ESLint completely
  },
  typescript: {
    ignoreBuildErrors: true,
  },
};

module.exports = nextConfig;
