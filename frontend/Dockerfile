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

WORKDIR /app/frontend

# Run lint, test, and build as part of the image build
RUN npm run lint && npm run test && npm run build

EXPOSE 3000
CMD ["npm", "start"] 