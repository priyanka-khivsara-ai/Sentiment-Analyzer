FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy frontend source code
COPY . .

# Expose port
EXPOSE 5173

# Run Vite development server, binding to all network interfaces
CMD ["npm", "run", "dev", "--", "--host"]
