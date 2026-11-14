#!/bin/sh
# Avvio nel container: agenti in background sulla 8001, gateway in primo piano su $PORT.
set -e
cd /app/agents
PYTHONPATH=src .venv/bin/uvicorn napoles_agents.api:app --host 127.0.0.1 --port 8001 &
cd /app/backend
export AGENTS_URL=http://127.0.0.1:8001
exec .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8080}"
