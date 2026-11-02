FROM node:26.13.0-alpine@sha256:c6ad9e9c1d80f6eb607c26b4b0a132ff7a2344fad1c78ea3baa2a7d4c8de6d94 AS frontend-builder
RUN npm install -g pnpm@12.16.1
WORKDIR /app/gui
COPY gui/package.json gui/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY gui/ ./
RUN pnpm build

FROM ghcr.io/astral-sh/uv:0.13.6@sha256:af22a52f5eafef3d78e551599d405c02df61919d18028f0cea8eda93bc9986d0 AS uv
FROM cgr.dev/chainguard/python:latest-dev@sha256:b0bc807f4334fea6adaac0f4dfbde255b9938ca957facb26eaed8bb448fce473 AS python-builder
USER root
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_PYTHON_DOWNLOADS=never UV_PYTHON=/usr/bin/python3
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY provisionR/ ./provisionR/
COPY main.py ./
COPY --from=frontend-builder /app/provisionR/static ./provisionR/static
RUN uv sync --locked --no-dev --no-editable && mkdir /data

FROM cgr.dev/chainguard/python:latest@sha256:b5decb00aa1cb65ab71bb3f6632a44bb8e6fd8d661de1f0342fd513a06837b9a
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
