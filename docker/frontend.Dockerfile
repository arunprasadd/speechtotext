FROM node:18-alpine

WORKDIR /app

# Add dependencies for node-gyp and other build tools
RUN apk add --no-cache python3 make g++ gcc

# Copy package.json only
COPY frontend/package.json ./

# Install dependencies
RUN npm install

# Copy app files
COPY frontend/ .

# Set environment variables
ENV NODE_ENV=development
ENV PATH /app/node_modules/.bin:$PATH
ENV NODE_OPTIONS="--max-old-space-size=4096"
ENV CHOKIDAR_USEPOLLING=true
ENV WATCHPACK_POLLING=true

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]