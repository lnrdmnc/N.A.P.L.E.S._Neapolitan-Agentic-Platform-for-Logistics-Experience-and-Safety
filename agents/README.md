# agents — gli agenti di N.A.P.L.E.S.

Rischio, Mobilità, Folla, Comunicazione e Orchestratore, in Python. Le decisioni seguono regole deterministiche con soglie dichiarate in `docs/IPOTESI.md`: la demo è ripetibile e funziona offline.

- **Espone:** API HTTP su `http://localhost:8001` (`make agents-run`, documentazione su `/docs`). Contratto: `contracts/agenti.openapi.json`.
- **Percorso demo:** `POST /api/reset` → `POST /api/avanza {"t_min": 72}` → `GET /api/messaggi` → `GET /api/piano` → `POST /api/piano/{id}/approva` → `GET /api/avvisi?pubblico=tifoso` → `GET /api/indicatori` → `GET /api/registro`.
- **Struttura:** `models/` e `api/` hanno un file per area con un indice; `bus.py` è la linea del tempo dei messaggi; `motore.py` la sessione; `agenti/` un file per agente.
- **Stub** (forma definitiva, dati finti, campo `stub: true`): `/api/contesto` (F1, F2), `/api/itinerario` (B6).
- **Traffico reale:** `GET /api/traffico`, tempi in auto con traffico da Google Routes API (`fonti/traffico_google.py`, chiave `MAPS_API_KEY`). Mai simulato: senza chiave o senza risposta `disponibile=false` e nessun numero. Risposte in memoria per `TRAFFICO_TTL_S` (600 s) e al massimo `TRAFFICO_MAX_CHIAMATE_GIORNO` (150) chiamate al giorno.
- **Partite al Maradona:** `GET /api/partite`, prossime partite in casa del Napoli da football-data.org (`fonti/partite_football.py`, chiave `FOOTBALL_DATA_API_KEY`). Dato reale; in memoria per `PARTITE_TTL_S` (6 ore); ogni risposta si salva in `data/fonti/partite_maradona.json`, usata se la fonte non risponde (`copia: true`).
- **Modello linguistico (L0):** `llm.scrivi(Richiesta(sistema, testo))` restituisce il testo di Claude (SDK `anthropic`, chiave `LLM_API_KEY`) oppure `None`, e allora si usa il testo a regole: senza chiave, senza rete, rifiuto o testo troncato. Cache su file in `data/llm_cache/`, da committare dopo averla riletta. `GET /api/llm` stato, `POST /api/llm/prova` un avviso di prova su una situazione simulata fissa.
- **Testi del modello (B5):** `Piano.sintesi_modello` (Orchestratore, per l'operatore) e `Alert.messaggio_modello` (Comunicazione, per profilo e lingua) sono scritti da Claude dagli stessi campi a regole, che restano identici. Mai per il caso A. Scartati se aggiungono numeri, parlano di evacuazione o non iniziano con SIMULAZIONE (`llm/controlli.py`). `make llm-cache` registra i testi del percorso demo.
- **Nuovo agente o router:** un file nella cartella e una riga nell'indice (`agenti/__init__.py`, `api/__init__.py`).
- **Registro:** scritto in `agents/var/registro.jsonl` (o `NAPOLES_REGISTRO`); `make verifica-registro` lo verifica.
- **Comandi:** `make agents-test`, `make prova`; dopo aver cambiato modelli o API, `make contracts`.
- **Requisiti:** [uv](https://docs.astral.sh/uv/); al primo avvio crea `.venv` e installa le dipendenze.
