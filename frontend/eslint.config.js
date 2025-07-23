import nextPlugin from '@next/eslint-plugin-next';
import nextConfig from 'eslint-config-next';

export default [
  ...nextConfig,
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    plugins: {
      '@next/next': nextPlugin,
    },
    rules: {
      // Add any custom rules here
    },
  },
]; 