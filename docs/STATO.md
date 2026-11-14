# Stato del progetto

## Scadenze

| Quando          | Cosa                                                          |
| --------------- | ------------------------------------------------------------- |
| sab 14/11 15:45 | piano su main (era 14:30)                                     |
| sab 14/11 16:30 | B0 (struttura del backend e contratti nuovi) e scheletro della web app su main |
| sab 14/11 18:00 | il percorso demo si vede a schermo: linea del tempo, piano con approvazione, avviso sul telefono |
| sab 14/11 18:30 | controllo: se il traguardo delle 18:00 manca, nessuna funzione nuova nel backend finché non c'è |
| sab 14/11 19:30 | simulatore a zone nella sessione, mappa, indicatori a confronto |
| sab 14/11 20:30 | stop lavori: stato salvato, esecuzione demo registrata        |
| dom 15/11 08:30 | ripresa                                                       |
| dom 15/11 10:30 | stop alle nuove funzionalità                                  |
| dom 15/11 11:30 | pacchetto di consegna pronto                                  |
| dom 15/11 12:00 | consegna                                                      |

Le 20:30, le 8:30 e le 12:00 sono orari ufficiali; gli altri sono traguardi interni, rivisti con il piano (docs/PIANO.md, sezione 8).

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
| Web app: backend FastAPI (backend/) e frontend React PWA (frontend/, viste /control-room e /cittadino) | Francesco Sannella | sab 14/11 15:20 | W0 fatto (scheletro); poi C3 e U1. Il backend è un gateway senza logica propria: gli agenti restano sulla 8001 |
| Script del video pitch (docs/VIDEO.md) | Leonardo Schiavo | sab 14/11 16:15 | Solo testo, massimo 3 minuti |
| Sintesi delle idee (docs/IDEE.md) e numeri credibili nel confronto con e senza coordinamento | Leonardo Monaco | sab 14/11 16:22 | Dal check di 4 agenti esperti di smart city; tocca simulazione.py, scenario e IPOTESI.md |

## Fatto

- Preparazione del repository: CLAUDE.md, .gitignore, .env.example, README.md, docs/STATO.md, docs/IPOTESI.md, docs/STAND.md, docs/FEEDBACK.md, Makefile con `make check`.
- docs/TEAM.md con i componenti del team e regola dei Co-authored-by in CLAUDE.md. Email dei commit di Leonardo Monaco aggiornata il 14/11.
- docs/PROGETTO.md (concept) e docs/GUIDA.md (guida del team) aggiunti.
- Checklist di consegna dal regolamento; CLAUDE.md aggiornato a cinque persone. Sottotitolo della challenge verificato sulla pagina italiana: «la città che Ci pensa».
- Decisioni in docs/PROGETTO.md: web app PWA con due viste, `/control-room` e `/cittadino` (sezione 6.1); gestione degli alert in tre casi con formato CAP semplificato (sezione 6.2). Il piano deve tenerne conto.
- Modulo agenti in Python (`agents/`): Rischio, Mobilità, Folla, Comunicazione, Orchestratore con regole deterministiche; scenario Maradona simulato; registro a catena di hash; indicatori con e senza coordinamento; API FastAPI (`make agents-run`). Contratto in `contracts/agenti.openapi.json`. 12 test; `make check` ora esegue anche lint e test degli agenti.
- Piano di lavoro in docs/PIANO.md, costruito sul modulo agenti: decisioni, architettura, contratti da aggiungere, cosa manca rispetto al brief, compiti con dipendenze e prove a mano, orari e tagli. Fonti dati verificate con chiamate reali (INGV, GTFS di ANM ed EAV, Open-Meteo, OSRM): esito nella sezione 10 del piano.
- **B0** — `models/` e `api/` divisi in un file per area con indice; bus dei messaggi (`bus.py`, `GET /api/messaggi?da_seq=`); `affidabilita_minima` nel piano; `origine` degli indicatori; stub con forma definitiva per simulazione, contesto, itinerario, ricezione e modifica del piano; comandi `make prova` (stampa la linea del tempo) e segnaposto `verifica-registro`, `demo`, `web-test`. **API degli agenti sulla porta 8001**, concordata con Francesco Sannella. Corretto lo sciame sismico che generava avvisi a raffica quando le scosse invecchiavano. 21 test.
- **W0, scheletro della web app.** `backend/`: gateway FastAPI sulla porta 8000 che serve la PWA compilata, inoltra ogni `/api/*` agli agenti sulla 8001 (`AGENTS_URL`) e, quando l'operatore approva un piano, spinge gli avvisi ai telefoni sul canale in tempo reale (`/api/events`); 9 test. `frontend/`: PWA React + TypeScript, tipi generati da `contracts/agenti.openapi.json`, stile ispirato a IBM Carbon con font in locale. `/control-room` mostra ora, stato della città, linee ed eventi con affidabilità; `/cittadino` mostra linee e avvisi approvati in diretta. Provato nel browser fino all'approvazione del piano al minuto 72. `make check` esteso alla web app; `make install`, `make backend`, `make frontend`, `make build`.

## Prossimi compiti liberi

Le schede complete, con file, dipendenze, verifica e prova a mano, sono in docs/PIANO.md, sezione 7. `…/` sta per `agents/src/napoles_agents/`.

Subito, in parallelo:

- **S0** — Simulatore a zone, funzione pura (`…/simulatore.py`).
- **L0** — Strato LLM: finto, compatibile OpenAI, Anthropic, cache (`…/llm/`).
- **D1** — Dati: copie in cache e docs/DATI.md, 40 minuti al massimo.
- **H1** — Persone: stand (docs/STAND.md), chiave del modello e chiave Google Maps in `.env`, nome del team, checkpoint con i mentor.
- Verificare con il team nomi delle stazioni, capacità e soglie in `scenario_maradona.json` e in docs/IPOTESI.md.

B0 è su main: sbloccati, backend: **B1** simulatore nella sessione (serve S0), **B2** modifica del piano (non in parallelo con B1), **B3** conferma di ricezione, **B4** indicatori con origine (dopo B1), **B5** testi dal modello (serve L0), **F1–F4** fonti INGV, meteo, GTFS, mappe (serve D1), **B6** itinerario del turista, **P1** strumento di prova, **R1** registro su file e comando di verifica.

Dopo lo scheletro della web app, una schermata per file: **C2** linea del tempo, **C3** piano e decisioni, **U1** avvisi nella vista cittadino, **C5** indicatori, **C4** registro, **C1** mappa a zone, **X1** `make demo` offline, **E1** test nel browser, **N1** «Perché Napoli». Se avanza tempo: U2, C6, U3, X2, U4.

## Problemi aperti

- **Deciso il 14/11: due processi.** `backend/` (porta 8000) è un gateway senza logica: serve la PWA, inoltra agli agenti (porta 8001) e tiene il canale in tempo reale. Per X1 `make demo` deve avviare entrambi.
- La vista cittadino mostra tutti gli avvisi approvati, per ogni profilo e lingua: il filtro per profilo è il compito U1.
- Indicatori: i minuti tra evento e avviso e i minuti per decidere oggi sono ipotesi in ingresso, non risultati. Vanno etichettati così finché il compito B4 non li misura nella sessione (docs/PIANO.md, sezione 9).
- Chiave del modello e chiave Google Maps non ancora in `.env`. Senza la prima la demo usa i testi a regole.
- Le stime del piano non lasciano margine: alle 18:30 vale la linea di taglio (docs/PIANO.md, sezione 8).
- Scenario: l'allerta meteo arriva al minuto 85, prima del fischio finale (95); PROGETTO.md la vuole durante il deflusso. Da valutare se spostarla.
- Dati: il feed GTFS di EAV è etichettato «Prova» nel catalogo e va controllato; la richiesta dei confini dei quartieri a Overpass è stata rifiutata; i termini di Google sulla conservazione delle risposte vanno verificati; il livello di allerta vulcanica va controllato sulla fonte ufficiale.
- Conflitti su README.md e docs/STATO.md: il 14/11 due commit hanno portato marcatori di conflitto su main, poi tolti. Prima di ogni commit: `git pull --rebase` a cartella pulita, e controllare che non restino righe che iniziano con `<<<<<<<`.
- `make check` richiede [uv](https://docs.astral.sh/uv/) per gli agenti e `make install` fatto una volta per la web app (venv in `backend/.venv`, pacchetti in `frontend/node_modules`). Su Windows il controllo del contratto ora legge il file in UTF-8.
- Su macOS, con il repository sul Desktop sincronizzato, Python ignora il collegamento del pacchetto in `.venv`: test e avvio usano `src` direttamente (già configurato in `pyproject.toml` e nel Makefile).
- Punti aperti del concept: nome del team, titolo definitivo. L'elenco completo è in docs/PROGETTO.md.
