# Use a specific Node version for consistency (Debian-based for better native module support)
FROM node:18.20.2

WORKDIR /app

# Copy root package.json and lock file for npm workspaces
COPY package.json package-lock.json ./
COPY frontend/package.json ./frontend/

# Copy the rest of the frontend code
COPY frontend ./frontend

# Install all workspace dependencies at the monorepo root
RUN npm ci

# Rebuild native modules for the current platform
RUN npm rebuild

WORKDIR /app/frontend

# Run build only (lint and tests run in CI/CD, not during image build)
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"] 