# Use a specific Node version for consistency
FROM node:18.20.2-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy the rest of the code
COPY . .

# Run lint, test, and build as part of the image build
RUN npm run lint && npm run test && npm run build

EXPOSE 3000
CMD ["npm", "start"] 