#!/bin/bash
# Avvio nel container: agenti sulla 8001 (interni), gateway su $PORT.
# Il gateway parte solo quando gli agenti rispondono; se uno dei due processi si ferma,
# il container esce e Cloud Run lo riavvia, invece di restare acceso a metà.
set -euo pipefail

cd /app/agents
PYTHONPATH=src .venv/bin/uvicorn napoles_agents.api:app --host 127.0.0.1 --port 8001 &
AGENTI=$!

for _ in $(seq 1 60); do
  if .venv/bin/python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/api/stato', timeout=1)" 2>/dev/null; then
    break
  fi
  if ! kill -0 "$AGENTI" 2>/dev/null; then
    echo "start: gli agenti non sono partiti" >&2
    exit 1
  fi
  sleep 0.5
done

cd /app/backend
AGENTS_URL=http://127.0.0.1:8001 .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8080}" &
GATEWAY=$!

trap 'kill -TERM "$AGENTI" "$GATEWAY" 2>/dev/null' TERM INT
wait -n "$AGENTI" "$GATEWAY"
STATO=$?
echo "start: un processo si è fermato (uscita $STATO), chiudo il container" >&2
kill -TERM "$AGENTI" "$GATEWAY" 2>/dev/null || true
exit "$STATO"
