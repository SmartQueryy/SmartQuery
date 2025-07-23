# Use a specific Node version for consistency
FROM node:18.20.2-alpine

WORKDIR /app

# Copy root package.json and lock file for npm workspaces
COPY package.json package-lock.json ./
COPY frontend/package.json ./frontend/

# Copy the rest of the frontend code
COPY frontend ./frontend

# Install all workspace dependencies at the monorepo root
RUN npm ci

# HACK: Force install the native rollup binary for Alpine Linux to fix npm bug
# See: https://github.com/npm/cli/issues/4828
RUN npm install --save-dev --arch=x64 --platform=linux --libc=musl rollup

WORKDIR /app/frontend

# Run build only (lint and tests run in CI/CD, not during image build)
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"] 