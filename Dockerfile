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

# Python build stage
FROM python:3.14-slim AS python-builder

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
RUN uv sync --frozen --no-dev

# Gather all required shared libraries for Python and its modules
RUN mkdir -p /dist/lib/x86_64-linux-gnu /dist/lib64 /dist/usr/local/lib /dist/data && \
    # Copy the dynamic linker
    cp /lib64/ld-linux-x86-64.so.2 /dist/lib64/ && \
    # Copy libpython
    cp -r /usr/local/lib/libpython3.14.so* /dist/usr/local/lib/ && \
    # Find all .so files and extract their library dependencies
    find /usr/local/bin/python3.14 \
         /usr/local/lib/python3.14/lib-dynload/*.so \
         /app/.venv/lib/python3.14/site-packages -name '*.so' -type f 2>/dev/null | \
    xargs -I {} ldd {} 2>/dev/null | \
    grep -o '/lib[^ ]*' | sort -u | \
    while read lib; do \
        cp -L "$lib" /dist/lib/x86_64-linux-gnu/ 2>/dev/null || true; \
    done && \
    # Copy SSL certificates
    cp -r /etc/ssl /dist/etc/ssl 2>/dev/null || mkdir -p /dist/etc/ssl

# Distroless final stage - scratch with only what we need
FROM scratch

# Copy shared libraries
COPY --from=python-builder /dist/lib/x86_64-linux-gnu /lib/x86_64-linux-gnu
COPY --from=python-builder /dist/lib64 /lib64
COPY --from=python-builder /dist/usr/local/lib /usr/local/lib
COPY --from=python-builder /dist/etc /etc

# Copy Python interpreter
COPY --from=python-builder /usr/local/bin/python3.14 /usr/local/bin/python3.14

# Copy Python standard library
COPY --from=python-builder /usr/local/lib/python3.14 /usr/local/lib/python3.14

# Copy passwd/group for nonroot user
COPY --from=gcr.io/distroless/python3-debian12:nonroot /etc/passwd /etc/passwd
COPY --from=gcr.io/distroless/python3-debian12:nonroot /etc/group /etc/group

WORKDIR /app

# Copy application and venv from builder
COPY --from=python-builder --chown=65532:65532 /app /app

# Create writable data directory for SQLite database
COPY --from=python-builder --chown=65532:65532 /dist/data /data

# Set environment
ENV PYTHONPATH=/app/.venv/lib/python3.14/site-packages:/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PROVISIONR_DB_PATH=/data/provisionr.db

# Expose port
EXPOSE 8000

# Run as nonroot user (uid 65532)
USER 65532:65532

# Run the application
ENTRYPOINT ["/usr/local/bin/python3.14", "-m", "uvicorn", "provisionR.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
