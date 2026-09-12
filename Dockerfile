FROM node:24.17.0-alpine@sha256:156b55f92e98ccd5ef49578a8cea0df4679826564bad1c9d4ef04462b9f0ded6 AS frontend-builder
RUN corepack enable && corepack prepare pnpm@10.30.3 --activate
WORKDIR /app/gui
COPY gui/package.json gui/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY gui/ ./
RUN pnpm build

FROM ghcr.io/astral-sh/uv:0.12.6@sha256:88bc6eb1ccd4b82efd0e1b530caffabddf50dc2bf612e66c14ea25b8ee8a4d3d AS uv
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
