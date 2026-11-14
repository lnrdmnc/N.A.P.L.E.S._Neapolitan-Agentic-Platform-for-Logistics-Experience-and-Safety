# N.A.P.L.E.S. — Neapolitan Agentic Platform for Logistics, Experience and Safety

Sistema di agenti AI per la resilienza urbana di Napoli: cinque agenti (Rischio, Mobilità, Folla, Comunicazione e un Orchestratore) gestiscono traffico ed eventi critici insieme alla control room comunale, e l'operatore approva sempre le decisioni. Progetto per la challenge 05 di Fastweb + Vodafone, The Big Hack 2026. Ogni evento sismico mostrato è una simulazione. Il concept completo è in [docs/PROGETTO.md](docs/PROGETTO.md).

Il repository si chiamava in precedenza `CoScienze-TheBigHack2026`.

## Stato attuale

Il modulo agenti funziona: i cinque agenti percorrono lo scenario simulato del Maradona e producono piani, avvisi, indicatori e registro, esposti via API. Lo scheletro della web app funziona: il backend sulla porta 8000 serve la PWA, inoltra le chiamate agli agenti sulla 8001 e spinge gli avvisi approvati ai telefoni in tempo reale; la control room mostra stato della città ed eventi, la vista cittadino linee e avvisi. Mappa, piano con Approva/Modifica/Rifiuta e indicatori sono ancora da costruire. Il piano di lavoro, con decisioni, contratti da aggiungere, compiti e orari, è in [docs/PIANO.md](docs/PIANO.md). La control room mostra il traffico reale di Google intorno allo stadio (chiavi in `.env`, messa online in [docs/DEPLOY.md](docs/DEPLOY.md)). Lo script del video pitch di 3 minuti è in [docs/VIDEO.md](docs/VIDEO.md). Il dettaglio è in [docs/STATO.md](docs/STATO.md).

## Come avviare

Servono [uv](https://docs.astral.sh/uv/), Python 3.12+ e Node 22+. Alla prima volta: `make install` (dipendenze della web app).

- `make check`: file base, `.env` non tracciato, lint e test degli agenti, contratto API allineato, test del backend, lint e build del frontend.
- `make agents-run`: API degli agenti su http://localhost:8001 (porta concordata con la web app), documentazione su http://localhost:8001/docs.
- `make prova`: tre prove dello scenario (l'operatore approva subito, tardi, mai) con rapporti leggibili in `docs/prove/`; vedi [docs/prove/README.md](docs/prove/README.md).
- `make verifica-registro`: verifica il registro delle decisioni scritto dalla demo (`agents/var/registro.jsonl`); con `FILE=percorso` un altro file. Fallisce e indica la riga se qualcosa è stato cambiato a mano.
- Web app in sviluppo, tre terminali: `make agents-run` (agenti), `make backend` (http://localhost:8000), `make frontend` (http://localhost:5173, si ricarica a ogni modifica).
- `make build`: compila la PWA in `frontend/dist`, servita dal backend su http://localhost:8000.
- `make contracts`: rigenera `contracts/agenti.openapi.json` dopo aver cambiato modelli o API.
- `make llm-cache`: registra i testi di Claude per il percorso demo (serve `LLM_API_KEY` in `.env`).

**Dove guardare in locale.** La porta 8001 è solo l'API degli agenti (`/docs`, `/api/...`): le pagine web stanno sulla 5173 in sviluppo (http://localhost:5173/control-room e http://localhost:5173/cittadino) o sulla 8000 dopo `make build`.

## Messa online

Un comando, da rilanciare uguale per ogni aggiornamento:

```sh
gcloud auth login                       # una volta per PC
gcloud config set project <ID_PROGETTO> # una volta per PC
make deploy
```

Pubblica su Google Cloud Run a Milano: un container con agenti e web app, chiavi da `.env` copiate in Secret Manager, account di servizio dedicato, una sola istanza (la sessione demo sta in memoria), spento quando nessuno lo usa. Alla fine stampa gli indirizzi di control room e vista cittadino. Installazione di gcloud, dettagli e soluzione dei problemi in [docs/DEPLOY.md](docs/DEPLOY.md).

## Struttura del repository

- `CLAUDE.md`: regole di lavoro per Claude Code, lette in automatico
- `README.md`: stato e registro delle modifiche
- `Makefile`: `make check`, eseguito prima di ogni commit, e i comandi degli agenti
- `.env.example`: nomi delle variabili d'ambiente, senza valori
- `agents/`: modulo agenti in Python (API FastAPI, scenario, test); vedi [agents/README.md](agents/README.md)
- `backend/`: gateway FastAPI della web app (porta 8000): serve la PWA, inoltra agli agenti, canale in tempo reale; vedi [backend/README.md](backend/README.md)
- `frontend/`: web app PWA in React, viste `/control-room` e `/cittadino`; vedi [frontend/README.md](frontend/README.md)
- `contracts/`: contratti tra i moduli; vedi [contracts/README.md](contracts/README.md)
- `docs/PROGETTO.md`: concept del progetto
- `docs/PIANO.md`: piano di lavoro (decisioni, architettura, contratti, compiti, orari e tagli)
- `docs/GUIDA.md`: guida del team (prompt, template, regole per i tre PC)
- `docs/TEAM.md`: componenti del team, utenti GitHub ed email per i commit
- `docs/STATO.md`: scadenze, chi lavora su cosa, fatto e compiti liberi
- `docs/IPOTESI.md`: dati simulati e ipotesi
- `docs/STAND.md`: risposte dello sponsor e degli organizzatori
- `docs/FEEDBACK.md`: prove fatte a mano dal team

## Team

Nome del team: da definire. Componenti in [docs/TEAM.md](docs/TEAM.md).

## Registro delle modifiche

| Data | Ora | Modulo | Modifica |
| --- | --- | --- | --- |
| 2026-11-14 | 18:40 | deploy | `make deploy`: messa online su Cloud Run in un comando, chiavi in Secret Manager, account di servizio dedicato, container senza root, regione Milano |
| 2026-11-14 | 18:35 | webapp | C3: piano in control room con Approva, Modifica e Rifiuta, sempre visibili su desktop; gli avvisi approvati arrivano in diretta alla vista cittadino; mappa non più allungata |
| 2026-11-14 | 18:32 | webapp | U1: vista cittadino per profilo (tifoso, residente, pendolare, turista in inglese) e conferma di lettura anonima |
| 2026-11-14 | 18:27 | webapp | C4: registro delle decisioni nella control room, con stato della catena e pulsante di verifica |
| 2026-11-14 | 18:24 | webapp | C5: indicatori con e senza coordinamento nella control room, con l'origine di ogni numero e l'affollamento per zona |
| 2026-11-14 | 18:15 | agents | B5 e K1: sintesi del piano e messaggi per profilo scritti da Claude, con controlli automatici e cache del percorso demo (`make llm-cache`); nuovi campi `sintesi_modello` e `messaggio_modello` |
| 2026-11-14 | 18:15 | agents | Strato LLM (L0): Claude Opus 5.5 con SDK ufficiale, cache su file, ripiego sul testo a regole; `GET /api/llm`, `POST /api/llm/prova` |
| 2026-11-14 | 18:10 | agents | P1: `make prova` salva tre prove in docs/prove/ con controlli automatici; corretto «1 scosse» negli avvisi |
| 2026-11-14 | 18:10 | webapp | Vista cittadino: riquadro «Partite al Maradona» con il calendario reale da football-data.org |
| 2026-11-14 | 18:00 | agents | Partite reali al Maradona: `GET /api/partite` da football-data.org, con copia per l'offline (nuovo nel contratto) |
| 2026-11-14 | 18:03 | webapp, agents | C2: linea del tempo dei messaggi tra agenti nella control room; nomi leggibili di luoghi e agenti nei conflitti |
| 2026-11-14 | 17:43 | agents, contracts | B3: conferma di ricezione reale per telefono anonimo e stime dichiarate; `ConfermaVisto` e nuovi campi di `Ricezione` nel contratto |
| 2026-11-14 | 17:33 | agents | R1: registro delle decisioni scritto su file e `make verifica-registro`, che rileva righe cambiate, tolte o spostate |
| 2026-11-14 | 17:27 | agents | B4: indicatori dal simulatore a zone, congestione per zona, tempi misurati in sessione; sensibilità rivista con lettura onesta |
| 2026-11-14 | 17:20 | agents, webapp | Traffico reale: `GET /api/traffico` da Google Routes API, mappa con livello traffico in control room, chiave del browser da `/api/config`; Dockerfile e docs/DEPLOY.md per Cloud Run |
| 2026-11-14 | 17:19 | agents | B1: la simulazione della sessione segue le decisioni approvate; impatto stimato in ogni piano |
| 2026-11-14 | 17:12 | agents | S0: simulatore a zone di Fuorigrotta, funzione pura con persone conservate, code e linee riattivate |
| 2026-11-14 | 17:04 | agents | B2: modifica del piano reale (esclusione di proposte, registro, niente esclusione delle allerte ufficiali) |
| 2026-11-14 | 17:04 | contracts | `Piano` ha `proposte_escluse` e `motivo_modifica` |
| 2026-11-14 | 16:58 | agents | Profilo «pendolare flegreo» negli avvisi: navette per Bagnoli e Pozzuoli, rimando alla Protezione Civile |
| 2026-11-14 | 16:58 | contracts | `Alert.pubblico` ammette anche `pendolare` |
| 2026-11-14 | 16:50 | webapp | Viste allineate alle specifiche: avvisi con indicazioni operative, certezza e caso A/B; control room con i riquadri previsti; adattive su telefono, tablet e computer; raggiungibili dal telefono sulla stessa Wi-Fi; tolto l'endpoint di prova del canale, etichette «simulato» e «da verificare» sui dati della control room |
| 2026-11-14 | 16:45 | agents | Allerta ufficiale con cornice in inglese per il turista, testo ufficiale identico; filtro avvisi per profilo senza doppioni |
| 2026-11-14 | 16:40 | repo | Tolti i marcatori di conflitto finiti su main con il commit fba8d7e in README.md e docs/STATO.md |
| 2026-11-14 | 16:35 | agents | Budget anti-allarme, cessato allarme operativo (`Cancel`), linee riattivate al minuto 130, conflitto mostrato una volta; scenario di 170 minuti |
| 2026-11-14 | 16:25 | docs | Script del video pitch in docs/VIDEO.md: otto scene entro 3 minuti, con chiusura su app per smartphone e controllo in tempo reale da SIM e telecamere |
| 2026-11-14 | 16:25 | agents | Numeri credibili: corretto il ritardo d'informazione senza coordinamento, capacità ricalibrate, tabella di sensibilità |
| 2026-11-14 | 16:25 | docs | docs/IDEE.md: check di 4 agenti esperti di smart city, idee per stasera, visione e tagli motivati |
| 2026-11-14 | 16:00 | webapp | Scheletro della web app (W0): gateway FastAPI su 8000 verso gli agenti su 8001, canale in tempo reale, PWA React con control room e vista cittadino, tipi generati dal contratto; `make check` esteso alla web app |
| 2026-11-14 | 15:45 | agents | B0: models e api divisi per area, bus dei messaggi, stub dei contratti nuovi, `make prova`, API sulla porta 8001 |
| 2026-11-14 | 15:40 | docs | Piano di lavoro in docs/PIANO.md, costruito sul modulo agenti; compiti liberi e orari aggiornati in docs/STATO.md |
| 2026-11-14 | 15:30 | repo | Tolti i marcatori di conflitto rimasti in README.md e docs/STATO.md |
| 2026-11-14 | 15:22 | repo | docs/TEAM.md: aggiornata l'email dei commit di Leonardo Monaco |
| 2026-11-14 | 15:20 | agents | Modulo agenti in Python: cinque agenti, scenario Maradona simulato, registro a hash, indicatori, API e contratto OpenAPI |
| 2026-11-14 | 15:00 | docs | Approccio quantistico tra gli sviluppi futuri in PROGETTO.md (ottimizzazione QUBO, firme post-quantum) |
| 2026-11-14 | 14:55 | docs | Decisioni in PROGETTO.md: web app PWA con due viste e gestione degli alert con formato CAP |
| 2026-11-14 | 14:40 | repo | Checklist di consegna in docs/STATO.md, team da cinque persone in CLAUDE.md |
| 2026-11-14 | 14:22 | repo | Aggiunta docs/TEAM.md e regola dei Co-authored-by nei commit |
| 2026-11-14 | 14:13 | repo | Preparazione del repository: regole, stato, ipotesi, concept, `make check` minimo |
