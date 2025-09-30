# Multi-stage build for optimal security and size
FROM node:20.18-alpine3.18 AS builder

# Set working directory
WORKDIR /app

# Install dependencies first (better caching)
COPY package*.json ./
RUN npm ci --only=production --silent && npm cache clean --force

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage - serve static files
FROM node:20.18-alpine3.18 AS production

# Install security updates and required packages
RUN apk update && apk upgrade && \
    apk add --no-cache ca-certificates dumb-init curl && \
    rm -rf /var/cache/apk/*

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S frontend -u 1001

# Install serve globally with specific version
RUN npm install -g serve@14.2.3

# Set working directory
WORKDIR /app

# Copy built application
COPY --from=builder --chown=frontend:nodejs /app/dist ./dist

# Switch to non-root user
USER frontend

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start server using serve
ENTRYPOINT ["dumb-init", "--"]
CMD ["serve", "-s", "dist", "-l", "3000"]