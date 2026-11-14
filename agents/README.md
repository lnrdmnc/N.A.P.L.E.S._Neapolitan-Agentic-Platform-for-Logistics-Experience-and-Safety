# agents — gli agenti di N.A.P.L.E.S.

Rischio, Mobilità, Folla, Comunicazione e Orchestratore, in Python. Le decisioni seguono regole deterministiche con soglie dichiarate in `docs/IPOTESI.md`: la demo è ripetibile e funziona offline.

- **Espone:** API HTTP su `http://localhost:8001` (`make agents-run`, documentazione su `/docs`). Contratto: `contracts/agenti.openapi.json`.
- **Percorso demo:** `POST /api/reset` → `POST /api/avanza {"t_min": 72}` → `GET /api/messaggi` → `GET /api/piano` → `POST /api/piano/{id}/approva` → `GET /api/avvisi?pubblico=tifoso` → `GET /api/indicatori` → `GET /api/registro`.
- **Struttura:** `models/` e `api/` hanno un file per area con un indice; `bus.py` è la linea del tempo dei messaggi; `motore.py` la sessione; `agenti/` un file per agente.
- **Stub** (forma definitiva, dati finti, campo `stub: true`): `/api/simulazione` (S0, B1), `/api/contesto` (F1, F2), `/api/itinerario` (B6), `/api/avvisi/ricezione` e `/visto` (B3).
- **Nuovo agente o router:** un file nella cartella e una riga nell'indice (`agenti/__init__.py`, `api/__init__.py`).
- **Comandi:** `make agents-test`, `make prova`; dopo aver cambiato modelli o API, `make contracts`.
- **Requisiti:** [uv](https://docs.astral.sh/uv/); al primo avvio crea `.venv` e installa le dipendenze.
