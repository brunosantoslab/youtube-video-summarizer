FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

# Copy application code
COPY frontend/ .

# Expose port
EXPOSE 3000

# Command to run the application
CMD ["npm", "run", "dev"]