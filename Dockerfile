FROM node:26.13.1-alpine@sha256:6bd9ab43c0ec0190ca7b2d193906cb8b7edf6e7f4afa43ddeccd6452710bffb5 AS frontend-builder
RUN npm install -g pnpm@12.21.0
WORKDIR /app/gui
COPY gui/package.json gui/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY gui/ ./
RUN pnpm build

FROM ghcr.io/astral-sh/uv:0.13.8@sha256:5cc1805e2426484abca4ad46ea783bab281fdb225fd82d8ce6d66a81254bac85 AS uv
FROM cgr.dev/chainguard/python:latest-dev@sha256:2f28d53bc0da2b0dcaabc5fc7aab2a69730466a9da4ffaa9bcf3019c3ff9905a AS python-builder
USER root
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_PYTHON_DOWNLOADS=never UV_PYTHON=/usr/bin/python3
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY provisionR/ ./provisionR/
COPY main.py ./
COPY --from=frontend-builder /app/provisionR/static ./provisionR/static
RUN uv sync --locked --no-dev --no-editable && mkdir /data

FROM cgr.dev/chainguard/python:latest@sha256:1f18c1d5b8b986ee00542f2528899b1b68484b9991a80d7c5bcb819e931ddf69
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
