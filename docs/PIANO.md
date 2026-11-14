# Piano di lavoro — N.A.P.L.E.S.

Scritto sabato 14/11/2026 alle 15:30, partendo da ciò che è già su main. Vale insieme a CLAUDE.md (regole) e a docs/PROGETTO.md (concept, che prevale dove i due differiscono). Chi prende un compito legge la sua riga nella sezione 7 e i contratti nella sezione 5.

## 1. Brief della challenge

Challenge 05 di The Big Hack 2026, «Napoli Agentic City: la città che Ci pensa», proposta da Fastweb + Vodafone.

> A Napoli mobilità, turismo, servizi pubblici e ambiente lavorano separati e faticano a coordinarsi quando arrivano grandi eventi, guasti, allerte o picchi di presenze. La challenge chiede un sistema di agenti AI che collaborano, coordinati da un orchestratore, con due facce: «Regia della città» (agenti che coordinano i servizi) e «Assistenti AI per le persone» (informano, suggeriscono percorsi, prenotano, avvisano su eventi e variazioni). Dati pubblici e simulazioni realistiche con ipotesi spiegate. Basta un prototipo o la simulazione di uno scenario, con pochi servizi che lavorano insieme. Si valutano visione, originalità e concretezza, con benefici misurabili, e va spiegato perché Napoli dovrebbe adottarla.

**Criteri della giuria:** utilità e valore, attinenza alla challenge, chiarezza e completezza, design e user experience, creatività e innovazione. Lo sponsor guarda visione, originalità, concretezza e benefici misurabili.

**Cosa conta per noi.** Un sistema multi-agente non si vede da solo: a schermo servono i messaggi tra agenti mentre accadono, la città che cambia dopo le decisioni approvate e gli stessi indicatori con e senza coordinamento. La logica verificabile (simulatore, vincoli, indicatori, registro) sta fuori dal modello linguistico. Il tema è l'emergenza: un errore di tono costa più di una funzione mancante.

**Consegna:** video pitch di massimo 3 minuti (oltre si viene esclusi), scheda progetto, repository pubblico, 2 checkpoint con i mentor. La lista completa è in docs/STATO.md.

## 2. Dove siamo

Su main alle 15:30 di sabato:

- **Modulo agenti** (`agents/`, Python, di Leonardo Monaco): Rischio, Mobilità, Folla, Comunicazione e Orchestratore a regole deterministiche; scenario Maradona in un file; registro a catena di hash; indicatori con e senza coordinamento; API FastAPI sulla porta 8001 (concordata con la web app; era 8000); 12 test. Copre già i tre casi di alert di PROGETTO.md 6.2 e il formato CAP semplificato.
- **Contratto** tra agenti e web app: `contracts/agenti.openapi.json`, generato dai modelli; `make check` fallisce se non è allineato.
- **Web app** (`frontend/`): presa da Francesco Sannella alle 15:20, in corso.
- **Non c'è ancora:** simulatore a zone, linea del tempo dei messaggi, strato LLM, dati reali, interfaccia, strumento di prova, test nel browser.

## 3. Decisioni

| Tema | Decisione | Da dove viene |
| --- | --- | --- |
| Forma | Una sola web app PWA con due viste, `/control-room` e `/cittadino`. Niente app nativa. | PROGETTO.md 6.1 |
| Stack | Python per agenti e API (FastAPI, pydantic, uv). React + TypeScript per la web app. | Codice su main, confermato il 14/11 |
| Agenti | Decidono con regole e soglie dichiarate in IPOTESI.md. Il modello linguistico scrive solo i testi, con cache, e mai quelli ufficiali del caso A. | agents/README.md |
| Alert | Casi A, B, C e formato CAP semplificato. L'operatore approva, modifica o rifiuta. | PROGETTO.md 6.2 |
| Scenario | Sei passi. L'imprevisto del passo 5 sta nel file di scenario, non si lancia dal vivo. | Confermato il 14/11 |
| Modello | Nessuna chiave per ora. I testi a regole fanno da modello finto; il client reale copre endpoint compatibili OpenAI e Anthropic e si sceglie da `.env`. | Risposta del 14/11 |
| Mappe | Google Maps Platform dal vivo per i tempi con traffico; la copia in cache per la demo offline viene da OpenStreetMap, perché i termini di Google limitano la conservazione delle risposte (da verificare). | Risposta del 14/11 |
| Confronto | «Senza coordinamento» usa lo stesso scenario e lo stesso simulatore; cambia solo ciò che ogni servizio sa e quando. Ogni ritardo ipotizzato è un parametro dichiarato. | Sezione 9 |
| Test nel browser | Playwright, che scarica Chromium (circa 170 MB per PC). È l'unica dipendenza pesante. | Approvato il 14/11 |

**Da decidere subito, a voce: un solo backend.** La riga di Francesco Sannella in STATO.md parla di un secondo backend FastAPI in `backend/`. Questo piano raccomanda di non averlo: l'API degli agenti cresce con gli endpoint nuovi e serve anche la web app compilata, così la demo è un solo processo su una sola porta. Se `backend/` esiste già, resta un punto di avvio che monta l'app degli agenti, senza logica propria.

## 4. Architettura

```
agents/src/napoles_agents/
  agenti/        un file per agente + indice AGENTI (una riga per agente)
  models/        contratti pydantic, un file per area (oggi models.py: va diviso, compito B0)
  api/           un file di endpoint per area + indice dei router (oggi api.py: va diviso, B0)
  motore.py      sessione demo: tempo, agenti, piano, decisioni, avvisi, registro
  bus.py         registro dei fatti della sessione: è il bus che la control room osserva (B0)
  simulatore.py  simulatore a zone, funzione pura (S0)
  simulazione.py confronto con e senza coordinamento
  llm/           client del modello: finto, compatibile OpenAI, Anthropic, cache (L0)
  fonti/         un file per fonte dati + indice: ingv, meteo, gtfs, mappe (F1–F4)
  itinerario.py  verifica dell'itinerario del turista (B6)
  prova.py       strumento di prova del team (P1)
  data/          scenario, rete delle zone, copie in cache delle fonti e del modello
agents/tests/    un file di test per modulo
contracts/       agenti.openapi.json (generato) e README
frontend/src/
  control-room/  una schermata per file + indice
  cittadino/     una schermata per file + indice
  api/           client e tipi generati dal contratto
docs/            PIANO, STATO, IPOTESI, DATI, prove/, demo/
```

Regole che evitano di pestarsi i piedi, oltre a quelle di CLAUDE.md:

- **File caldi divisi per primi.** Oggi `api.py`, `models.py` e `motore.py` servono a quasi ogni compito del backend. Il compito B0 divide i primi due in un file per area; dopo, ogni funzione nuova aggiunge i propri file e una riga in un indice.
- **`motore.py` resta unico:** i compiti che lo toccano (B1, B2) non si fanno in parallelo.
- **Prima lo stub.** Ogni endpoint nuovo entra nel contratto subito, con dati finti (B0). La web app si sviluppa su quelli; chi implementa sostituisce lo stub nel proprio file.
- **Un contratto cambia con un commit dedicato:** modelli, `make contracts`, riga in STATO.md.
- **Il Makefile si tocca una volta:** B0 aggiunge i comandi `prova`, `verifica-registro`, `demo` e `web-test`, che chiamano punti di ingresso riempiti dai compiti successivi.

**Demo offline.** `make demo` compila la web app e la serve dall'API degli agenti: un processo, una porta, nessuna rete. Le due viste leggono la stessa sessione a intervalli di un secondo; un flusso di eventi dal server si aggiunge solo se avanza tempo. Ogni dato esterno e ogni testo del modello arriva da una copia in cache nel repository.

**Limiti di tono, già nei test e da non allentare.** Ogni evento della demo è simulato ed etichettato. Nessun avviso parte senza approvazione. Il testo ufficiale del caso A non si riscrive. Nessuna istruzione di evacuazione. Una notizia non verificata non diventa mai un avviso. Il livello di allerta vulcanica ufficiale compare solo come contesto, con fonte e data della verifica.

## 5. Contratti

Il contratto è `contracts/agenti.openapi.json`. Oggi definisce `StatoCitta`, `Proposta`, `Piano`, `Alert`, `VoceRegistro`, `Indicatori`, `ConfrontoIndicatori` e gli endpoint di sessione, piano, avvisi, indicatori e registro. Il compito B0 aggiunge ciò che segue, con stub a dati finti. I nomi restano in italiano come nel codice esistente.

| Oggetto | Campi | Endpoint |
| --- | --- | --- |
| `Messaggio` | `seq`, `t_min`, `ora`, `da`, `a`, `tipo` (evento, proposta, conflitto, piano, decisione, avviso), `titolo`, `testo`, `affidabilita`, `simulato`, `rif` | `GET /api/messaggi?da_seq=` |
| `StatoZona` | `id`, `nome`, `tipo`, `lat`, `lon`, `capienza`, `persone`, `in_coda`, `carico` | dentro `PassoSimulazione` |
| `SerieSimulazione` | `scenario` (sessione, con_coordinamento, senza_coordinamento), `passo_min` (5), `passi`: `t_min`, `ora`, `zone`, `dentro_stadio`, `arrivati`, `misure_attive` | `GET /api/simulazione?scenario=` |
| `Impatto`, dentro `Piano` | `deflusso_min` e `picco_carico` per zona, con e senza il piano, calcolati dal simulatore | `GET /api/piano` |
| `Piano`, campi nuovi | `affidabilita_minima`, `impatto`; lo `stato` ammette anche `modificato` | `POST /api/piano/{id}/modifica` con `proposte_escluse`, `motivo` |
| `Ricezione` | `avviso`, `visti_reali`, `visti_stimati`, `consegnati_stimati`, `simulato` | `POST /api/avvisi/{id}/visto`, `GET /api/avvisi/ricezione` |
| `Indicatori`, campi nuovi | `congestione_zone`, `origine` di ogni indicatore (calcolato, misurato_in_sessione, ipotesi) | `GET /api/indicatori` |
| `Contesto` | livello vulcanico con fonte e data, ultimi eventi INGV reali, meteo reale, ognuno con `simulato: false` e data della copia | `GET /api/contesto` |
| `Itinerario` | `tappe`, `tratte` (`da`, `a`, `mezzo`, `minuti`, `percorribile`, `motivo`, `alternativa`), `fonte`, `verificato_al_t_min` | `GET /api/itinerario` |

In interfaccia si mostrano sempre `simulato`, `affidabilita` o `certainty`, e la fonte. Un `Alert` inviato porta sempre il `piano_id` approvato.

## 6. Cosa manca rispetto al brief

| Richiesta | Stato su main | Compito |
| --- | --- | --- |
| Simulatore deterministico con zone, capienze, flussi | Solo un modello aggregato, non legato alle decisioni approvate | S0, B1 |
| La città cambia dopo le decisioni approvate | No: gli indicatori non dipendono da cosa approva l'operatore | B1, C1 |
| Messaggi tra agenti su un bus osservabile | Le proposte esistono, la linea del tempo no | B0, C2 |
| Piano motivato con grado di certezza e impatto stimato | Sintesi e affidabilità per proposta sì; impatto no | B0, B1, C3 |
| Approva, modifica, rifiuta | Manca la modifica | B2, C3 |
| Strato LLM sostituibile, con finto e cache | Manca | L0, B5, K1 |
| Dati reali con copia in cache | Mancano; fonti verificate in sezione 10 | D1, F1–F4 |
| Control room e vista cittadino | In corso | W0, C1–C6, U1–U4 |
| Indicatori: congestione per zona; tempi misurati | Manca la congestione; i tempi sono ipotesi in ingresso | B1, B4, C5 |
| Conferma di ricezione degli avvisi | Manca | B3, U1 |
| Registro: comando di verifica | La verifica esiste solo via API | R1 |
| Strumento di prova in docs/prove/ | Manca | P1 |
| Test nel browser con screenshot | Manca | E1 |
| Pagina «Perché Napoli» | Manca | N1 |

## 7. Compiti

Non sono assegnati: si prendono dalla tabella in docs/STATO.md. Le stime sono per una sessione di Claude Code con controllo a mano e commit. `…/` sta per `agents/src/napoles_agents/`.

### Subito, in parallelo

| ID | Compito | File | Stima | Verifica | Il team prova a mano |
| --- | --- | --- | --- | --- | --- |
| B0 | Struttura del backend e stub dei contratti nuovi. Blocca B1–B6, F1–F4, P1. Va fatto da chi conosce il modulo o insieme a lui. | `…/api/`, `…/models/`, `…/bus.py`, `…/motore.py`, `Makefile`, `contracts/` | 45' | I 12 test passano ancora; `GET /api/messaggi` racconta il percorso demo; contratto rigenerato | Leggere i messaggi di un'esecuzione: si capisce chi dice cosa a chi? |
| W0 | Scheletro della web app: due viste, client generato dal contratto, tema. Già preso. | `frontend/` | in corso | `npm run build`; le due viste leggono `/api/stato` | Aprire le due viste affiancate |
| S0 | Simulatore a zone, funzione pura: zone con capienza e coda, linee, ondate, navette, persone informate o no. | `…/simulatore.py`, `…/data/rete_fuorigrotta.json`, `agents/tests/test_simulatore.py` | 50' | Persone conservate; capienza superata diventa coda; stessa entrata, stessa uscita | Zone e capienze di Fuorigrotta, voce per voce |
| L0 | Strato LLM: finto, compatibile OpenAI, Anthropic, cache su file. | `…/llm/`, `agents/tests/test_llm.py`, `.env.example` | 40' | Finto deterministico; risposta registrata riletta identica; nessuna rete nei test | Con la chiave: una chiamata vera |
| D1 | Dati: copie in cache e scheda delle fonti, 40 minuti al massimo. | `docs/DATI.md`, `…/data/fonti/` | 40' | Ogni fonte ha copia, licenza e data | Linee e fermate intorno allo stadio; livello vulcanico sulla fonte ufficiale |
| H1 | Persone: stand, chiave del modello, chiave Google, nome del team, checkpoint. | `docs/STAND.md`, `.env` | — | Una chiamata vera per chiave | — |

### Dopo B0: backend

| ID | Compito | File | Dipende da | Stima | Verifica | Il team prova a mano |
| --- | --- | --- | --- | --- | --- | --- |
| B1 | Simulatore nella sessione: la serie per zona segue le decisioni approvate; `impatto` nel piano. | `…/motore.py`, `…/api/simulazione.py`, `…/simulazione.py` | B0, S0 | 40' | Approvare o no cambia la serie; senza approvazione nessuna misura attiva | Approvare tardi e vedere la coda crescere |
| B2 | Modifica del piano prima dell'approvazione. Non in parallelo con B1. | `…/motore.py`, `…/api/piani.py` | B0 | 25' | La proposta esclusa non genera avvisi; la modifica è nel registro | Escludere le navette e leggere gli avvisi |
| B3 | Conferma di ricezione. | `…/ricezione.py`, `…/api/ricezione.py` | B0 | 25' | Il conteggio cresce solo per avvisi inviati | Aprire la vista cittadino su due dispositivi |
| B4 | Indicatori: congestione per zona, tempi misurati in sessione, origine di ogni numero. Dopo B1. | `…/simulazione.py`, `…/models/indicatori.py` | B1 | 35' | Ogni indicatore dichiara l'origine; cambiando un'ipotesi cambia solo ciò che ne dipende | Rileggere IPOTESI.md accanto alla tabella |
| B5 | Testi dell'Orchestratore e della Comunicazione scritti dal modello, con cache e ripiego sul testo a regole. | `…/agenti/orchestratore.py`, `…/agenti/comunicazione.py` | L0 | 40' | Caso A mai riscritto; numeri e fonti del testo uguali a quelli del piano; senza cache e senza rete esce il testo a regole | Leggere ogni avviso ad alta voce |
| F1 | Fonte INGV: ultimi eventi reali di Campi Flegrei e Vesuvio come contesto. | `…/fonti/ingv.py` | B0, D1 | 25' | Legge dalla cache senza rete; mai mescolati agli eventi simulati | — |
| F2 | Fonte meteo, Open-Meteo. | `…/fonti/meteo.py` | B0, D1 | 20' | Come F1 | — |
| F3 | Fonte GTFS: linee, fermate e tracciati di ANM ed EAV per la mappa. | `…/fonti/gtfs.py` | B0, D1 | 30' | Come F1 | Tracciati sulla mappa |
| F4 | Fonte mappe: Google dal vivo, OpenStreetMap in cache. | `…/fonti/mappe.py` | B0, D1 | 30' | Senza chiave o senza rete usa la cache | — |
| B6 | Itinerario del turista verificato rispetto alle linee sospese. | `…/itinerario.py`, `…/api/itinerario.py` | B0, F4 | 35' | La tratta su linea sospesa viene sostituita; il motivo cita il servizio, non il pericolo | L'alternativa è percorribile davvero? |
| P1 | Strumento di prova: esegue lo scenario e salva messaggi, piano e indicatori. | `…/prova.py`, `docs/prove/` | B0 | 20' | `make prova` gira senza rete in pochi secondi | Leggere tre esecuzioni: decisioni assurde, ripetute o vaghe |
| R1 | Registro su file e comando di verifica. | `…/registro.py` | — | 20' | Una riga cambiata a mano fa fallire `make verifica-registro` | Cambiare una riga e lanciare il comando |
| K1 | Registrazione dei testi del modello nella cache, quando arriva la chiave. | `…/data/llm_cache/` | B5, chiave | 20' | La demo gira dalla cache senza rete | Rileggere tutti i testi registrati |

### Dopo W0: web app, una schermata per file

| ID | Compito | Dipende da | Stima | Verifica | Il team prova a mano |
| --- | --- | --- | --- | --- | --- |
| C2 | Control room: linea del tempo dei messaggi tra agenti | W0, B0 | 30' | Screenshot | Da tre metri si capisce chi parla? |
| C3 | Control room: piano, conflitti, impatto, Approva, Modifica, Rifiuta | W0, B0 | 40' | Screenshot; il rifiuto finisce nel registro | Provare i tre pulsanti |
| U1 | Cittadino: avvisi per profilo e lingua, banner e notifica, conferma di ricezione | W0 | 40' | L'avviso compare solo dopo l'approvazione | Leggerlo da tifoso, residente e turista |
| C5 | Control room: indicatori a confronto, con l'origine di ogni numero | W0 | 30' | Screenshot | Si distingue calcolato da ipotesi? |
| C4 | Control room: registro delle decisioni e verifica | W0 | 20' | Screenshot | — |
| C1 | Control room: mappa a zone disegnata da file locali | W0, B1 | 45' | Screenshot ai minuti 72, 95 e 110 | La zona dello stadio si riconosce? |
| U2 | Cittadino: meteo e traffico per zona | W0, F2, B1 | 25' | Reale e simulato etichettati | — |
| C6 | Control room: contesto reale (livello vulcanico, INGV, meteo) | W0, F1 | 25' | Reale e simulato mai nello stesso riquadro | — |
| U3 | Cittadino: itinerario del turista | W0, B6 | 30' | Screenshot | — |
| N1 | Pagina «Perché Napoli» | W0, STAND.md | 30' | Screenshot | Rilettura con le risposte dello stand |
| X1 | `make demo`: web app compilata servita dall'API, installabile, offline | W0 | 30' | Con la rete staccata la demo gira | Provarla con la rete staccata |
| E1 | Test nel browser del percorso demo, con screenshot | C2, C3, U1, C5, X1 | 40' | `make web-test` | — |
| U4 | Cittadino: storia di Napoli da fonti citate | W0 | 25' | — | Prima cosa che si taglia |
| X2 | Modalità registrata: la web app riproduce una sessione salvata senza API, per un link pubblico | X1 | 40' | — | Solo se avanza tempo |

### Ordine

1. **Percorso demo:** B0, W0, C2, C3, U1, C5, C4, S0, B1, C1, X1, P1, E1, N1.
2. **Rafforzano la demo:** L0, B5, K1, B4, D1, F1, F2, R1, B2, B3.
3. **Se avanza tempo:** F3, F4, B6, U3, C6, U2, X2, U4, e l'esperimento quantistico di PROGETTO.md.

## 8. Orari e linea di taglio

Le stime sommano circa 16 ore di PC più i commit; ne restano circa 20 tra oggi e domattina, da cui vanno tolti checkpoint, prove a mano e video. Non c'è margine: l'ordine della sezione 7 serve a chiudere prima il percorso demo.

| Quando | Traguardo |
| --- | --- |
| sab 15:45 | Piano su main (era 14:30) |
| sab 16:30 | B0 e scheletro della web app su main |
| sab 18:00 | Il percorso demo si vede a schermo: linea del tempo, piano con approvazione, avviso sul telefono |
| sab 18:30 | Controllo: se il traguardo delle 18:00 manca, nessuna funzione nuova nel backend finché non c'è |
| sab 19:30 | Simulatore a zone nella sessione, mappa, indicatori a confronto |
| sab 20:30 | Stop ufficiale: `make demo` offline, screenshot in docs/demo/, tag |
| dom 8:30–10:30 | Testi del modello se c'è la chiave, dati reali, test nel browser, «Perché Napoli» |
| dom 10:30 | Stop alle funzioni; pacchetto, video di 3 minuti, scheda progetto |

Tagli, in quest'ordine: storia di Napoli, modalità registrata, itinerario, fonte GTFS, contesto reale in control room, conferma di ricezione. Il Vesuvio resta solo come seconda area nei dati reali INGV, senza scenario.

## 9. Indicatori: calcolato o ipotesi

Oggi i minuti tra evento e avviso e i minuti per decidere sono parametri dello scenario (3 e 2 con coordinamento, 15 e 20 senza), e da questi dipendono deflusso e picco. Presentati come risultati sarebbero numeri decisi a tavolino. Regole per la demo e il pitch:

- Ogni indicatore dichiara la sua origine: calcolato dal simulatore, misurato nella sessione, oppure ipotesi in ingresso. L'interfaccia la mostra accanto al numero.
- Con coordinamento, i tempi di decisione e di avviso si misurano nella sessione, dal primo evento critico all'approvazione e all'invio.
- Senza coordinamento restano ipotesi dichiarate in IPOTESI.md, e si dice.
- Le ipotesi si fissano prima di guardare i risultati. Se una correzione indebolisce il risultato lo si dice, senza compensare con altre ipotesi.

## 10. Dati verificati il 14/11

Chiamate reali; le copie non sono ancora nel repository: le salva D1.

| Fonte | Esito |
| --- | --- |
| INGV FDSN, `webservices.ingv.it/fdsnws/event/1/query` | Senza chiave, testo e GeoJSON. Eventi reali recenti: Campi Flegrei Md 2.6 il 13/11, Vesuvio Md 2.6 il 12/11. |
| GTFS ANM, `www.anm.it/google/google-transit.zip` | Valido dal 9/11 al 31/12/2026. Linea 1, Linea 6, funicolari, bus e la Linea 2 (agenzia Trenitalia). Non contiene la Cumana. Fermate «Tecchio - Mostra» e «Marino - Stadio Maradona». |
| GTFS EAV, `www.wimob.it/cfile/download.php?file=google-transit.zip` | Contiene Cumana (linea 9) e Circumflegrea (linea 5), con tracciati. Il catalogo Mobility Database lo etichetta «Prova»: orari da controllare. |
| GTFS-RT | Non trovato per Napoli: lo stato delle linee in tempo reale resta simulato. |
| Open-Meteo | Senza chiave. |
| OSRM su OpenStreetMap | Risponde in auto (`router.project-osrm.org`) e a piedi (`routing.openstreetmap.de`). |
| Overpass, confini dei quartieri | Richiesta rifiutata (406): riprovare, o usare gli open data del Comune. |

## 11. Rischi

- **Tempo:** nessun margine. Vale la linea di taglio delle 18:30.
- **Due backend:** va deciso subito (sezione 3).
- **Chiave del modello:** senza, la demo usa i testi a regole. Funziona, ma l'apporto dell'AI si vede meno: la chiave è il compito umano più urgente.
- **Conflitti su README.md e docs/STATO.md:** oggi due commit hanno portato marcatori di conflitto su main. Prima di ogni commit: `git pull --rebase` a cartella pulita, e controllare che non restino righe che iniziano con `<<<<<<<`.
- **Tono:** il post simulato «crolli a Bagnoli, evacuate lo stadio» compare in control room. Va sempre mostrato con l'etichetta «non verificata» e mai nella vista cittadino.

## 12. Differenze tra il prompt del piano e PROGETTO.md

Vale PROGETTO.md:

- Il destinatario principale è il cittadino; l'operatore è il garante. L'avviso sul telefono è un passo obbligato della demo.
- Il passo 5 è allerta meteo più scossa simulata durante il deflusso. Nello scenario attuale l'allerta meteo arriva al minuto 85, dieci minuti prima del fischio finale: da valutare se spostarla dopo il minuto 95.
- Il passo 6 è il bilancio con indicatori e registro.
- Prenotazioni e acquisti restano fuori dal prototipo.
- Il prompt chiedeva passi di cinque minuti e un modulo per cartella alla radice. Il codice su main lavora al minuto dentro un solo pacchetto Python: si tiene così, con la serie per la mappa a passi di cinque minuti.
