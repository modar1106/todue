# ============================================================
# Stage 1: Build Frontend Assets
# ============================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package manifests for optimal layer caching
COPY package*.json ./

# Install dependencies strictly
RUN npm ci

# Copy full frontend source
COPY . .

# Build production bundle with Vite
RUN npm run build

# ============================================================
# Stage 2: Production Nginx Server
# ============================================================
FROM nginx:alpine AS runner

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy built distribution assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose HTTP port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q --spider http://127.0.0.1/healthz || exit 1

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
