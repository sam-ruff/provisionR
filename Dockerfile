# Build stage for frontend
FROM node:20-alpine AS frontend-builder

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app/gui

# Copy frontend package files
COPY gui/package.json gui/pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy frontend source
COPY gui/ ./

# Build frontend (outputs to ../provisionR/static)
RUN pnpm generate

# Python backend stage
FROM python:3.14-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy Python project files
COPY pyproject.toml uv.lock* ./
COPY provisionR/ ./provisionR/
COPY main.py ./

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/provisionR/static ./provisionR/static

# Install Python dependencies
RUN uv sync --frozen

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "provisionR.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
