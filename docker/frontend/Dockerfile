# ── Stage 1: Build ────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# VITE_ env vars are baked in at build time.
# Override via: docker compose build --build-arg VITE_API_BASE_URL=/api frontend
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# ── Stage 2: Serve with NGINX ────────────────────────────────────────────────
FROM nginx:alpine

# Copy built SPA files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom NGINX config (SPA routing + API reverse proxy)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
