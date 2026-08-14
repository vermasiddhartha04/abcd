# ==========================================================
# Stage 1: Build React/Vite application
# ==========================================================

FROM node:22-alpine AS builder

WORKDIR /app

COPY frontend/package*.json ./

RUN npm install

COPY frontend/ .

RUN npm run build


# ==========================================================
# Stage 2: Serve production build
# ==========================================================

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

# SPA routing support
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
