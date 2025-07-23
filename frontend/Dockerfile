# Use a specific Node version for consistency
FROM node:18.20.2-alpine

WORKDIR /app

# Copy frontend package files
COPY package.json package-lock.json ./

# Install dependencies (this will install all workspace dependencies)
RUN npm ci

# Copy the frontend code
COPY . ./

# Skip lint for now due to config issues, run test and build
RUN npm run test && npm run build

EXPOSE 3000
CMD ["npm", "start"] 