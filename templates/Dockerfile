# Generic multi-stage Dockerfile template.
# Adjust: base image, build stage, runtime stage, and exposed port.

# ---------- Build stage ----------
# Use a pinned digest or exact version — never `latest`.
FROM node:22-bookworm-slim AS build
# Example for Python: FROM python:3.12-slim
# Example for Go:      FROM golang:1.24-bookworm AS build

WORKDIR /app

# Install dependencies first (better layer caching)
COPY package.json package-lock.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# ---------- Runtime stage ----------
FROM node:22-bookworm-slim AS runtime

ENV NODE_ENV=production
ENV PORT=8080

WORKDIR /app

# Copy only what's needed to run (adjust to your output layout)
COPY --from=build /app/package.json .
COPY --from=build /app/package-lock.json .
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist

# Non-root user for security
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8080

CMD ["node", "dist/index.js"]