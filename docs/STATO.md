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
| Traffico reale da Google (Maps JavaScript con livello traffico, Routes API per i tempi) e messa online su Cloud Run | Leonardo Schiavo | sab 14/11 16:50 | Mappa e traffico fatti, resta il deploy (docs/DEPLOY.md). Era: Nuovo endpoint `/api/traffico` negli agenti (contratto), mappa in control room, Dockerfile |

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
- **Check di 4 agenti esperti di smart city** (cittadini, turisti, telco e mobilità, giuria): sintesi, idee per stasera, visione per il pitch e tagli motivati in [docs/IDEE.md](IDEE.md).
- **Numeri credibili.** Corretto il bug per cui il ritardo d'informazione «senza coordinamento» non aveva effetto; capacità ricalibrate su ordini di grandezza realistici (navette 100/min invece di 500, Linea 2 80 invece di 400); tabella di sensibilità in docs/IPOTESI.md e in `make prova`. Nuovo risultato: deflusso 47 → 66 minuti, picco 22.180 → 39.400 persone; anche senza l'ipotesi sui percorsi a piedi il coordinamento vince (58 → 66 minuti). 23 test.
- **Script del video pitch** in docs/VIDEO.md: otto scene, circa 390 parole di voce, chiusura a 2:57. Chiude con gli sviluppi futuri: app per smartphone e controllo in tempo reale con presenze dalle SIM e telecamere di sicurezza, in forma aggregata e anonima. I numeri degli indicatori (scena 5) restano da inserire dopo l'esecuzione finale.
- **Budget anti-allarme e cessato allarme operativo.** Un aggiornamento parte solo se per la persona cambiano gravità o istruzioni (la scossa delle 22:26 non notifica più); `Update` «di nuovo in servizio» quando Cumana e Linea 2 ripartono (minuto 130, simulato); `Cancel` per ogni profilo quando lo sciame si chiude (minuto 162), con rimando alla Protezione Civile per il rischio vulcanico. Il conflitto su Piazzale Tecchio compare una sola volta sulla linea del tempo. **Lo scenario ora dura 170 minuti** (prima 150). Contratto invariato. 28 test.
- **Allerta ufficiale con cornice in inglese per il turista.** Accanto all'originale per tutti parte una versione per il turista: titolo in inglese «SIMULATION – Official alert from … – original Italian text below, not translated», testo ufficiale identico, `references` all'originale. `GET /api/avvisi?pubblico=turista` mostra solo questa versione, senza doppione; residenti e tifosi continuano a ricevere l'originale. Nel contratto cambia solo la descrizione dell'endpoint. 29 test.
- **Web app adattiva.** Deciso il 14/11: control room e vista cittadino si usano sia da telefono sia da computer (PROGETTO.md 6.1). Provate a 375, 768 e 1440 px con i dati dello scenario, senza scorrimento orizzontale. `make backend` e `make frontend` ascoltano anche sulla rete locale: dal telefono sulla stessa Wi-Fi, `http://<IP del PC>:5173`.
- **Viste allineate alle specifiche** (PROGETTO.md 6, 6.1, 6.2; contracts/README.md). Vista cittadino: avvisi letti da `/api/avvisi` (restano dopo una ricarica), con indicazioni operative, certezza, fonte, «simulato», caso A «Allarme ufficiale · testo non modificato» o caso B «Evento rilevato · in attesa di comunicazioni ufficiali», colore per gravità. Control room: tolto il pannello di prova del canale; aggiunti i riquadri «Messaggi tra agenti» (C2) e «Registro delle decisioni» (C4). Tolto `POST /api/events/test` (solo sviluppo); intestazione «Control room comunale · prototipo», non più «Comune di Napoli»; etichette «simulati» e «da verificare» su spettatori, partita e livello vulcanico.
- **Profilo «pendolare flegreo».** **Contratto: `Alert.pubblico` e `GET /api/avvisi?pubblico=` ammettono anche `pendolare`.** Chi rientra verso l'area flegrea riceve la propria catena di avvisi: navette sostitutive «per Bagnoli e Pozzuoli» (destinazioni simulate), linee di nuovo in servizio, cessato allarme, e sempre «prima di rientrare segui la Protezione Civile e il tuo Comune», senza indicazioni sul rischio. 30 test.
- **B2 — Modifica del piano.** `POST /api/piano/{id}/modifica` non è più uno stub: l'operatore esclude proposte, il piano passa a «modificato» (si approva o rifiuta come un piano proposto), si ricalcolano conflitti e sintesi, le proposte escluse non generano avvisi; la modifica va nel registro e sul bus. Si può reincludere una proposta rimodificando. Le allerte ufficiali (caso A) non si possono escludere (409); escludere lo sciame non fa partire il cessato allarme. **Contratto: `Piano` ha i campi `proposte_escluse` e `motivo_modifica`.** 38 test.
- **S0 — Simulatore a zone** (`…/simulatore.py`, `…/data/rete_fuorigrotta.json`). Funzione pura e deterministica, a passi di un minuto: stadio, Piazzale Tecchio, Viale Giochi del Mediterraneo, stazioni Campi Flegrei (L2) e Mostra (Cumana), fermata Marino - Stadio Maradona; coordinate delle fermate dal GTFS ANM. Persone conservate a ogni passo, capienza superata = coda, linee riattivate che tornano a smaltire, persone informate o no. Restituisce già la `SerieSimulazione` del contratto. Risultato sullo scenario: area sgombra in 50 minuti con coordinamento contro 60 senza; le stazioni chiuse non si riempiono mai con coordinamento (senza: fino a 3,7 volte la capienza); picco su Piazzale Tecchio 3,8 contro 5,4 volte la capienza. Non ancora collegato alla sessione: è il compito B1. 47 test.
- **Traffico reale da Google.** `GET /api/traffico` negli agenti (contratto: modelli `Traffico`, `PercorsoTraffico`, `LivelloTraffico`): tempi in auto dallo stadio verso cinque destinazioni con Google Routes API, mai simulati; in memoria 10 minuti, massimo 150 chiamate al giorno. Pannello «Traffico in tempo reale» nella control room con livello traffico di Google Maps al posto del segnaposto della mappa; `GET /api/config` nel backend per la chiave del browser. Chiavi in `.env` (`MAPS_API_KEY`, `MAPS_JS_API_KEY`), da chiedere in privato a Leonardo Schiavo. `Dockerfile` e docs/DEPLOY.md per Cloud Run: deploy non ancora eseguito.
- **B1 — Simulatore nella sessione.** `GET /api/simulazione` non è più uno stub: `scenario=sessione` (predefinito) mostra la città secondo le decisioni approvate fin qui, proiettata fino a fine scenario; `con_coordinamento` e `senza_coordinamento` danno i due casi per lo schermo diviso. Solo ciò che è approvato cambia la città (`…/decisioni.py`): rifiutare o non decidere non attiva nessuna misura. Ogni piano, anche dopo una modifica, porta `impatto`: picco di carico e minuti alla normalità per zona, con e senza quel piano. Sullo scenario: area sgombra 70 minuti dopo il fischio senza approvazioni, 50 approvando al minuto 72, 55 approvando al minuto 101 (il costo del ritardo). 54 test.

## Prossimi compiti liberi

Le schede complete, con file, dipendenze, verifica e prova a mano, sono in docs/PIANO.md, sezione 7. `…/` sta per `agents/src/napoles_agents/`.

Subito, in parallelo:

- **L0** — Strato LLM: finto, compatibile OpenAI, Anthropic, cache (`…/llm/`).
- **D1** — Dati: copie in cache e docs/DATI.md, 40 minuti al massimo.
- **H1** — Persone: stand (docs/STAND.md), chiave del modello e chiave Google Maps in `.env`, nome del team, checkpoint con i mentor.
- Verificare con il team nomi delle stazioni, capacità e soglie in `scenario_maradona.json` e in docs/IPOTESI.md.
- Dal check delle idee (docs/IDEE.md), con S0: **presenze aggregate per cella simulate** come input dell'agente Folla.

B0 è su main: sbloccati, backend: **B3** conferma di ricezione, **B4** indicatori con origine (dopo B1), **B5** testi dal modello (serve L0), **F1–F4** fonti INGV, meteo, GTFS, mappe (serve D1), **B6** itinerario del turista, **P1** strumento di prova, **R1** registro su file e comando di verifica.

Dopo lo scheletro della web app, una schermata per file: **C2** linea del tempo, **C3** piano e decisioni, **U1** avvisi nella vista cittadino, **C5** indicatori, **C4** registro, **C1** mappa a zone, **X1** `make demo` offline, **E1** test nel browser, **N1** «Perché Napoli». Domenica dopo le 10:30: registrazione del video seguendo docs/VIDEO.md. Se avanza tempo: U2, C6, U3, X2, U4.

## Problemi aperti

- **Contratto cambiato il 14/11:** nuovo endpoint `GET /api/traffico` e modelli `Traffico`, `PercorsoTraffico`, `LivelloTraffico`. `make agents-run` e `make backend` ora leggono `.env` se esiste.
- Disagi del trasporto pubblico: Google non li espone via API e per Napoli non esiste un feed GTFS-RT; nella mappa c'è solo il traffico stradale reale.

- **Da sistemare prima della consegna (controllo del 14/11 sui contenuti che non possono restare):**
  - docs/TEAM.md contiene le email personali di tutti e il repository sarà pubblico: usare l'email `noreply` di GitHub, anche in `git config`.
  - Con il deploy pubblico, `/api/reset`, `/api/avanza` e `/api/piano/…/approva` sarebbero chiamabili da chiunque attraverso il gateway: serve una chiave sulle chiamate che cambiano lo stato o una versione pubblica di sola lettura.
  - Riquadri «In costruzione» (C1–C5, U2), comandi `make demo`, `web-test`, `verifica-registro` che oggi falliscono, endpoint `stub: true` degli agenti: da completare o togliere.
  - Testi ufficiali inventati (allerta meteo «Protezione Civile Regione Campania (simulato)»): l'etichetta «simulato» deve restare visibile anche nel video e negli screenshot.
- **Deciso il 14/11: due processi.** `backend/` (porta 8000) è un gateway senza logica: serve la PWA, inoltra agli agenti (porta 8001) e tiene il canale in tempo reale. Per X1 `make demo` deve avviare entrambi.
- La vista cittadino mostra tutti gli avvisi approvati, per ogni profilo e lingua: il filtro per profilo è il compito U1.
- PROGETTO.md 6.2 va corretto: il cell broadcast è unidirezionale e non distingue i profili, quindi la conferma di ricezione esiste solo nella PWA; IT-Alert è della Protezione Civile e le informazioni operative passano da un canale separato su adesione (docs/IDEE.md).
- Dal telefono via Wi-Fi la pagina si apre, ma installazione come app e funzionamento offline non partono: fuori da `localhost` il browser richiede HTTPS. Per la demo sul telefono serve un certificato locale o un tunnel HTTPS (da decidere in X1).
- Indicatori: i minuti tra evento e avviso e i minuti per decidere oggi sono ipotesi in ingresso, non risultati. Vanno etichettati così finché il compito B4 non li misura nella sessione (docs/PIANO.md, sezione 9).
- Chiave del modello e chiave Google Maps non ancora in `.env`. Senza la prima la demo usa i testi a regole.
- Le stime del piano non lasciano margine: alle 18:30 vale la linea di taglio (docs/PIANO.md, sezione 8).
- Scenario: l'allerta meteo arriva al minuto 85, prima del fischio finale (95); PROGETTO.md la vuole durante il deflusso. Da valutare se spostarla.
- Dati: il feed GTFS di EAV è etichettato «Prova» nel catalogo e va controllato; la richiesta dei confini dei quartieri a Overpass è stata rifiutata; i termini di Google sulla conservazione delle risposte vanno verificati; il livello di allerta vulcanica va controllato sulla fonte ufficiale.
- Conflitti su README.md e docs/STATO.md: il 14/11 due commit hanno portato marcatori di conflitto su main, poi tolti. Prima di ogni commit: `git pull --rebase` a cartella pulita, e controllare che non restino righe che iniziano con `<<<<<<<`.
- `make check` richiede [uv](https://docs.astral.sh/uv/) per gli agenti e `make install` fatto una volta per la web app (venv in `backend/.venv`, pacchetti in `frontend/node_modules`). Su Windows il controllo del contratto ora legge il file in UTF-8.
- Su macOS, con il repository sul Desktop sincronizzato, Python ignora il collegamento del pacchetto in `.venv`: test e avvio usano `src` direttamente (già configurato in `pyproject.toml` e nel Makefile).
- Punti aperti del concept: nome del team, titolo definitivo. L'elenco completo è in docs/PROGETTO.md.
