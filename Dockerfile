FROM node:26.13.0-alpine@sha256:8996bb5821d62a8fd9bb27c1cb07462f3fdce6e47d640c6a881ead0b064ce216 AS frontend-builder
RUN npm install -g pnpm@12.18.0
WORKDIR /app/gui
COPY gui/package.json gui/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY gui/ ./
RUN pnpm build

FROM ghcr.io/astral-sh/uv:0.13.7@sha256:96f40d3904aad8d0bd010539001d36c8e2188b981e1334471a90c4a1d93bb490 AS uv
FROM cgr.dev/chainguard/python:latest-dev@sha256:898360ca56a2a65c3facdd36a4e6151133a580aa367195261554e82948921ff1 AS python-builder
USER root
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_PYTHON_DOWNLOADS=never UV_PYTHON=/usr/bin/python3
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY provisionR/ ./provisionR/
COPY main.py ./
COPY --from=frontend-builder /app/provisionR/static ./provisionR/static
RUN uv sync --locked --no-dev --no-editable && mkdir /data

FROM cgr.dev/chainguard/python:latest@sha256:1a00964779bf570a8cb2ea4fa086614af19c35069029785c08fcec0c50b66ac0
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
