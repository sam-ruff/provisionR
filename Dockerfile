FROM node:26.13.1-alpine@sha256:6bd9ab43c0ec0190ca7b2d193906cb8b7edf6e7f4afa43ddeccd6452710bffb5 AS frontend-builder
RUN npm install -g pnpm@12.21.0
WORKDIR /app/gui
COPY gui/package.json gui/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY gui/ ./
RUN pnpm build

FROM ghcr.io/astral-sh/uv:0.13.9@sha256:d3b601f0c7b118bc1753febf7c41cc80981df678445e0254284eecf84db79a7d AS uv
FROM cgr.dev/chainguard/python:latest-dev@sha256:e2736acdf97f2b1cb59545f4f26317b18a953e90e59fa4c212a782315b248111 AS python-builder
USER root
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_PYTHON_DOWNLOADS=never UV_PYTHON=/usr/bin/python3
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY provisionR/ ./provisionR/
COPY main.py ./
COPY --from=frontend-builder /app/provisionR/static ./provisionR/static
RUN uv sync --locked --no-dev --no-editable && mkdir /data

FROM cgr.dev/chainguard/python:latest@sha256:f33049a06b10d6bd729e08a181094774ca5e9c7b0cf1bbe674aa977cd5258daa
ARG GIT_SHA
ARG VERSION
LABEL org.opencontainers.image.source="https://github.com/sam-ruff/provisionR" \
    org.opencontainers.image.revision="${GIT_SHA}" \
    org.opencontainers.image.version="${VERSION}"
WORKDIR /app
COPY --from=python-builder --chown=65532:65532 /app/.venv /app/.venv
COPY --from=python-builder --chown=65532:65532 /app/provisionR /app/provisionR
COPY --from=python-builder --chown=65532:65532 /data /data
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PROVISIONR_DB_PATH=/data/provisionr.db \
    PROVISIONR_TEMPLATE_DIR=/data/templates
USER 65532:65532
EXPOSE 8000
ENTRYPOINT ["/app/.venv/bin/python", "-m", "uvicorn", "provisionR.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
