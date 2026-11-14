# Stato del progetto

## Scadenze

| Quando          | Cosa                                                          |
| --------------- | ------------------------------------------------------------- |
| sab 14/11 14:30 | piano approvato, contratti e moduli definiti                  |
| sab 14/11 16:30 | simulatore e scenario con Rischio, Mobilità e Orchestratore   |
| sab 14/11 18:30 | control room, lato utente e indicatori a confronto            |
| sab 14/11 20:30 | stop lavori: stato salvato, esecuzione demo registrata        |
| dom 15/11 08:30 | ripresa                                                       |
| dom 15/11 10:30 | stop alle nuove funzionalità                                  |
| dom 15/11 11:30 | pacchetto di consegna pronto                                  |
| dom 15/11 12:00 | consegna                                                      |

## Consegna: regole che possono escluderci

Dal regolamento ufficiale. Da spuntare prima delle 12:00 di domenica.

- [ ] Scheda progetto su hackathon.codemotion.com: titolo, descrizione, challenge scelta, link ai materiali, link al video pitch, nome e telefono del referente.
- [ ] Video pitch di **massimo 3 minuti**: oltre si viene esclusi.
- [ ] Link ai materiali accessibile alla giuria: repository pubblico.
- [ ] Almeno **2 checkpoint** con i mentor: senza, il progetto non è valido.
- [ ] Almeno una persona del team presente alla premiazione (dalle 16:00 di domenica).
- [ ] Nome del team senza riferimenti, nemmeno parziali, a marchi o ragioni sociali.

## Chi sta lavorando su cosa

| Compito | Chi | Da quando | Nota |
| --- | --- | --- | --- |
| Piano con moduli, contratti e compiti (docs/PIANO.md) | Leonardo Schiavo | sab 14/11 14:30 | Prompt principale: produce il piano, nessun codice |
| Web app: backend FastAPI (backend/) e frontend React PWA (frontend/, viste /control-room e /cittadino) | Francesco Sannella | sab 14/11 15:20 | Prima lo scheletro; API degli agenti e contratti da concordare con Leonardo Monaco |

## Fatto

- Preparazione del repository: CLAUDE.md, .gitignore, .env.example, README.md, docs/STATO.md, docs/IPOTESI.md, docs/STAND.md, docs/FEEDBACK.md, Makefile con `make check`.
- docs/TEAM.md con i componenti del team e regola dei Co-authored-by in CLAUDE.md. Email dei commit di Leonardo Monaco aggiornata il 14/11.
- docs/PROGETTO.md (concept) e docs/GUIDA.md (guida del team) aggiunti.
- Checklist di consegna dal regolamento; CLAUDE.md aggiornato a cinque persone. Sottotitolo della challenge verificato sulla pagina italiana: «la città che Ci pensa».
- Decisioni in docs/PROGETTO.md: web app PWA con due viste, `/control-room` e `/cittadino` (sezione 6.1); gestione degli alert in tre casi con formato CAP semplificato (sezione 6.2). Il piano deve tenerne conto.
- Modulo agenti in Python (`agents/`): Rischio, Mobilità, Folla, Comunicazione, Orchestratore con regole deterministiche; scenario Maradona simulato; registro a catena di hash; indicatori con e senza coordinamento; API FastAPI (`make agents-run`, porta 8000). Contratto in `contracts/agenti.openapi.json`. 12 test; `make check` ora esegue anche lint e test degli agenti.

## Prossimi compiti liberi

- Piano con moduli, contratti e compiti (Prompt principale, `fable` a `max`, plan mode): produce docs/PIANO.md.
- Stand: fare le domande dello sponsor e degli organizzatori e scrivere le risposte in docs/STAND.md.
- Chiave del modello: procurarla e metterla in .env.
- Web app: collegare `/control-room` e `/cittadino` alle API degli agenti (percorso demo in `agents/README.md`).
- Agenti: dati INGV reali via FDSN con copia in cache, al posto delle scosse simulate quando servono.
- Agenti: testi dell'Orchestratore e della Comunicazione riformulati con LLM, con cache; mai per le allerte ufficiali (caso A).
- Agenti: verificare con il team nomi delle stazioni, capacità e soglie in `scenario_maradona.json` e in docs/IPOTESI.md.

## Problemi aperti

- `make check` richiede [uv](https://docs.astral.sh/uv/) installato, perché esegue lint e test degli agenti. Va esteso alla web app quando c'è.
- Su macOS, con il repository sul Desktop sincronizzato, Python ignora il collegamento del pacchetto in `.venv`: test e avvio usano `src` direttamente (già configurato in `pyproject.toml` e nel Makefile).
- docs/PIANO.md non esiste ancora.
- Punti aperti del concept: nome del team, titolo definitivo, feed GTFS (linee e tempo reale), stack, API meteo e mappe e chi ha la chiave. L'elenco completo è in docs/PROGETTO.md.
