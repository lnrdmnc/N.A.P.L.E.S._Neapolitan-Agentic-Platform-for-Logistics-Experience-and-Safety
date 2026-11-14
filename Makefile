.PHONY: check agents-test agents-run contracts prova verifica-registro demo web-test

AGENTS_PORT ?= 8001

check:
	@for f in CLAUDE.md README.md docs/STATO.md .env.example; do \
		test -f "$$f" || { echo "check: manca $$f"; exit 1; }; \
	done
	@if git ls-files --error-unmatch .env >/dev/null 2>&1; then \
		echo "check: .env e' tracciato da git"; exit 1; \
	fi
	@$(MAKE) --no-print-directory agents-test
	@echo "check: ok"

# Modulo agenti (Python, uv): test, lint e contratto API allineato
agents-test:
	@cd agents && uv run --quiet ruff check . && uv run --quiet ruff format --check . && uv run --quiet pytest -q
	@cd agents && PYTHONPATH=src uv run --quiet python -c "import sys, pathlib; from napoles_agents.contratti import openapi; sys.exit(0 if pathlib.Path('../contracts/agenti.openapi.json').read_text() == openapi() else 'check: contracts/agenti.openapi.json non aggiornato, esegui make contracts')"

# API degli agenti per la web app su http://localhost:8001 (documentazione su /docs)
agents-run:
	cd agents && uv run uvicorn napoles_agents.api:app --app-dir src --port $(AGENTS_PORT) --reload

# Rigenera contracts/agenti.openapi.json dai modelli
contracts:
	cd agents && PYTHONPATH=src uv run python -m napoles_agents.contratti

# Esegue lo scenario approvando ogni piano e stampa la linea del tempo (completato da P1)
prova:
	cd agents && PYTHONPATH=src uv run --quiet python -m napoles_agents.prova

# Verifica del registro su file (compito R1)
verifica-registro:
	@echo "verifica-registro: da implementare nel compito R1 (oggi la verifica è in GET /api/registro)"; exit 1

# Demo offline: web app compilata servita dall'API su una sola porta (compito X1)
demo:
	@echo "demo: da implementare nel compito X1; per ora 'make agents-run' e la web app in sviluppo"; exit 1

# Test nel browser del percorso demo (compito E1)
web-test:
	@echo "web-test: da implementare nel compito E1"; exit 1
