# N.A.P.L.E.S. in un solo container, per Google Cloud Run (docs/DEPLOY.md).
# Agenti su 127.0.0.1:8001 (interni), gateway backend su $PORT con la PWA compilata.

FROM node:22-slim AS web
WORKDIR /app
COPY contracts/ contracts/
COPY frontend/package.json frontend/package-lock.json frontend/
RUN cd frontend && npm ci
COPY frontend/ frontend/
RUN cd frontend && npm run build

FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /usr/local/bin/uv
WORKDIR /app
ENV PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY agents/pyproject.toml agents/uv.lock agents/
RUN cd agents && uv sync --frozen --no-dev --no-install-project
COPY agents/ agents/

COPY backend/requirements.txt backend/
RUN python -m venv backend/.venv && backend/.venv/bin/pip install --no-cache-dir -r backend/requirements.txt
COPY backend/ backend/
COPY --from=web /app/frontend/dist frontend/dist
COPY deploy/start.sh deploy/start.sh

ENV PORT=8080
EXPOSE 8080
CMD ["sh", "deploy/start.sh"]
