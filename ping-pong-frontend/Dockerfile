FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN yarn install

# Copy source code
COPY . .

# Expose port
EXPOSE 5173

# Start development server with host binding for Docker
CMD ["yarn", "dev", "--host", "0.0.0.0"]
