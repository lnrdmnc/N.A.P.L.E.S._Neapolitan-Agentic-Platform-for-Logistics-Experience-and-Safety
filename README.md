# N.A.P.L.E.S. — Neapolitan Agentic Platform for Logistics, Experience and Safety

Sistema di agenti AI per la resilienza urbana di Napoli: cinque agenti (Rischio, Mobilità, Folla, Comunicazione e un Orchestratore) gestiscono traffico ed eventi critici insieme alla control room comunale, e l'operatore approva sempre le decisioni. Progetto per la challenge 05 di Fastweb + Vodafone, The Big Hack 2026. Ogni evento sismico mostrato è una simulazione. Il concept completo è in [docs/PROGETTO.md](docs/PROGETTO.md).

Il repository si chiamava in precedenza `CoScienze-TheBigHack2026`.

## Stato attuale

Il modulo agenti funziona: i cinque agenti percorrono lo scenario simulato del Maradona e producono piani, avvisi, indicatori e registro, esposti via API. La web app non c'è ancora; il piano (docs/PIANO.md) è in corso. Il dettaglio è in [docs/STATO.md](docs/STATO.md).

## Come avviare

Serve [uv](https://docs.astral.sh/uv/).

- `make check`: file base, `.env` non tracciato, lint e test degli agenti, contratto API allineato.
- `make agents-run`: API degli agenti su http://localhost:8000, documentazione su http://localhost:8000/docs.
- `make contracts`: rigenera `contracts/agenti.openapi.json` dopo aver cambiato modelli o API.

## Struttura del repository

- `CLAUDE.md`: regole di lavoro per Claude Code, lette in automatico
- `README.md`: stato e registro delle modifiche
- `Makefile`: `make check`, eseguito prima di ogni commit, e i comandi degli agenti
- `.env.example`: nomi delle variabili d'ambiente, senza valori
- `agents/`: modulo agenti in Python (API FastAPI, scenario, test); vedi [agents/README.md](agents/README.md)
- `contracts/`: contratti tra i moduli; vedi [contracts/README.md](contracts/README.md)
- `docs/PROGETTO.md`: concept del progetto
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
| 2026-11-14 | 15:30 | repo | Tolti i marcatori di conflitto rimasti in README.md e docs/STATO.md |
| 2026-11-14 | 15:22 | repo | docs/TEAM.md: aggiornata l'email dei commit di Leonardo Monaco |
| 2026-11-14 | 15:20 | agents | Modulo agenti in Python: cinque agenti, scenario Maradona simulato, registro a hash, indicatori, API e contratto OpenAPI |
| 2026-11-14 | 15:00 | docs | Approccio quantistico tra gli sviluppi futuri in PROGETTO.md (ottimizzazione QUBO, firme post-quantum) |
| 2026-11-14 | 14:55 | docs | Decisioni in PROGETTO.md: web app PWA con due viste e gestione degli alert con formato CAP |
| 2026-11-14 | 14:40 | repo | Checklist di consegna in docs/STATO.md, team da cinque persone in CLAUDE.md |
| 2026-11-14 | 14:22 | repo | Aggiunta docs/TEAM.md e regola dei Co-authored-by nei commit |
| 2026-11-14 | 14:13 | repo | Preparazione del repository: regole, stato, ipotesi, concept, `make check` minimo |
