# agents — gli agenti di N.A.P.L.E.S.

Rischio, Mobilità, Folla, Comunicazione e Orchestratore, in Python. Le decisioni seguono regole deterministiche con soglie dichiarate in `docs/IPOTESI.md`: la demo è ripetibile e funziona offline.

- **Espone:** API HTTP su `http://localhost:8000` (`make agents-run`, documentazione interattiva su `/docs`). Contratto: `contracts/agenti.openapi.json`.
- **Percorso demo:** `POST /api/reset` → `POST /api/avanza {"t_min": 72}` → `GET /api/piano` → `POST /api/piano/{id}/approva` → `GET /api/avvisi?pubblico=tifoso` → `GET /api/indicatori` → `GET /api/registro`.
- **Scenario:** `src/napoles_agents/data/scenario_maradona.json` (timeline, capacità, soglie: tutto simulato).
- **Nuovo agente:** un file in `src/napoles_agents/agenti/` con `proponi(stato, scenario) -> list[Proposta]` e una riga in `agenti/__init__.py`.
- **Test:** `make agents-test`. Dopo aver cambiato modelli o API: `make contracts`.
- **Requisiti:** [uv](https://docs.astral.sh/uv/); al primo avvio `uv` crea `.venv` e installa le dipendenze.
