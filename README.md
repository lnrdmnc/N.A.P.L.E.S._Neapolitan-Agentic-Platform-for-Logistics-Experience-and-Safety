# N.A.P.L.E.S. — Neapolitan Agentic Platform for Logistics, Experience and Safety

Sistema di agenti AI per la resilienza urbana di Napoli: cinque agenti (Rischio, Mobilità, Folla, Comunicazione e un Orchestratore) gestiscono traffico ed eventi critici insieme alla control room comunale, e l'operatore approva sempre le decisioni. Progetto per la challenge 05 di Fastweb + Vodafone, The Big Hack 2026. Ogni evento sismico mostrato è una simulazione. Il concept completo è in [docs/PROGETTO.md](docs/PROGETTO.md).

Il repository si chiamava in precedenza `CoScienze-TheBigHack2026`.

## Stato attuale

Repository appena preparato: regole di team, file di stato e concept. Non c'è ancora codice. Prossimo passo: il piano con moduli, contratti e compiti (docs/PIANO.md). Il dettaglio è in [docs/STATO.md](docs/STATO.md).

## Come avviare

- `make check`: verifica che esistano i file base e che `.env` non sia tracciato (verrà esteso con lint e test).
- Installazione e avvio della demo: da compilare appena esistono.

## Struttura del repository

- `CLAUDE.md`: regole di lavoro per Claude Code, lette in automatico
- `README.md`: stato e registro delle modifiche
- `Makefile`: `make check`, eseguito prima di ogni commit
- `.env.example`: nomi delle variabili d'ambiente, senza valori
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
| 2026-11-14 | 15:00 | docs | Approccio quantistico tra gli sviluppi futuri in PROGETTO.md (ottimizzazione QUBO, firme post-quantum) |
| 2026-11-14 | 14:55 | docs | Decisioni in PROGETTO.md: web app PWA con due viste e gestione degli alert con formato CAP |
| 2026-11-14 | 14:40 | repo | Checklist di consegna in docs/STATO.md, team da cinque persone in CLAUDE.md |
| 2026-11-14 | 14:22 | repo | Aggiunta docs/TEAM.md e regola dei Co-authored-by nei commit |
| 2026-11-14 | 14:13 | repo | Preparazione del repository: regole, stato, ipotesi, concept, `make check` minimo |
