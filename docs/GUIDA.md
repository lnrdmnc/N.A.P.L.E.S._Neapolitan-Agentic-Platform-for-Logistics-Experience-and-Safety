# The Big Hack 2026 — N.A.P.L.E.S. con Claude Code

Nov 13, 2026 · @Leonardo

Tutto quello che serve per N.A.P.L.E.S., il progetto del team per la challenge 05 di Fastweb + Vodafone: il concept, i prompt per Claude Code con modello ed effort, le regole per lavorare su tre PC, le domande per lo stand, il lavoro che resta a voi e i template per riportarmelo.

## Il progetto: N.A.P.L.E.S.

N.A.P.L.E.S. (Neapolitan Agentic Platform for Logistics, Experience and Safety) è un sistema di agenti AI per la resilienza urbana: gestisce traffico ed eventi critici insieme alla control room comunale, e l'operatore approva sempre le decisioni.

Il vostro file di progetto, con abstract, problema, soluzione e sviluppi futuri, va salvato nel repository come `docs/PROGETTO.md`: i prompt lo leggono da lì. Io non l'ho visto, quindi qui sotto c'è solo ciò che mi avete riassunto; dove i due differiscono vale il vostro file.

### Agenti

| Agente | Compito | Dati |
| --- | --- | --- |
| Rischio | Segue eventi sismici e vulcanici (Campi Flegrei, Vesuvio) e meteo; separa i dati confermati da quelli incerti | INGV via FDSN, meteo |
| Mobilità | Stato di linee e strade, sospensioni, percorsi alternativi | Feed GTFS dei gestori locali, API di mappe |
| Folla | Stima presenze e deflussi da stadio e stazioni, organizza il deflusso a ondate | Capienze, ISTAT, presenze aggregate simulate |
| Comunicazione | Messaggi a cittadini e turisti, con provenienza dell'allarme | Decisioni approvate dall'operatore |
| Orchestratore | Integra le proposte, risolve i conflitti, presenta il piano alla control room | Messaggi degli altri agenti |

Compiti e fonti di ciascun agente vanno allineati alla tabella del vostro file.

### Scenario demo

1. Partita allo stadio Maradona, città in condizioni normali.
2. Sciame sismico ai Campi Flegrei, simulato.
3. Sospensione di Cumana e Linea 2.
4. Deflusso dallo stadio a ondate, coordinato dagli agenti.
5. Nuovo imprevisto e adattamento del piano.
6. Bilancio: indicatori a confronto e registro delle decisioni. Questo passo è una mia proposta, da sostituire con il sesto del vostro file.

### Funzioni lato utente

- Per tutti: meteo, traffico, emergenze.
- Per il turista, in più: storia di Napoli e itinerario suggerito, verificato sulle mappe.

### Dati e servizi

- Meteo: serve scegliere l'API. Open-Meteo è un candidato senza chiave; Claude Code lo verifica nella fase dati.
- Traffico e mappe: le API con traffico in tempo reale richiedono di norma una chiave e un account di fatturazione. Decidete chi la crea; senza chiave si usano percorsi su OpenStreetMap, senza traffico reale.
- Trasporti: feed GTFS dei gestori locali. Resta da verificare quali linee coprono e se esiste il tempo reale (GTFS-RT).
- Sismica: INGV via FDSN. Open data comunali e regionali, ISTAT.
- Benefici: calcolati nella simulazione, con e senza coordinamento. Nessun numero inventato.

### Registro delle decisioni e blockchain

Il prototipo tiene un registro delle decisioni a prova di manomissione, cioè una catena di hash. È la base dello sviluppo futuro: una blockchain permissioned tra Comune, gestori dei trasporti, Protezione Civile e operatori di telecomunicazioni, con solo hash sulla catena per restare conformi al GDPR. Le due opzioni da valutare sono Hyperledger Fabric o l'ancoraggio degli hash su una blockchain pubblica.

Gli operatori di telecomunicazioni entrano in due punti: dati aggregati sulla presenza di persone e canali di allerta alla popolazione. Nel prototipo le presenze sono simulate; è il collegamento naturale con Fastweb + Vodafone.

### Limiti da rispettare

- Ogni evento sismico della demo è simulato ed etichettato come tale sullo schermo.
- Il sistema affianca le fonti ufficiali, non le sostituisce: INGV e Protezione Civile restano l'autorità, e non si inventano istruzioni di evacuazione.
- L'operatore approva ogni decisione; nessun dato personale.

### Punti aperti

- [ ] Nome del team
- [ ] Titolo definitivo del progetto
- [ ] Verifica dei feed GTFS: linee coperte e tempo reale
- [ ] Scelta dello stack
- [ ] Conferma dello scenario e del sesto passo
- [ ] API meteo e API di mappe: quale, e chi ha la chiave
- [ ] `docs/PROGETTO.md` caricato nel repository

## Sequenza: modello, effort e modalità

Fable 5.2 a max serve solo per il piano e per i blocchi. Tutto il resto va su Opus a xhigh o Sonnet a medium, così il limite del Pro regge fino a domenica.

| Chi e quando | Cosa incollare | Modello | Effort | Modalità |
| --- | --- | --- | --- | --- |
| PC 1, adesso | Prompt 0 | `sonnet` | `medium` | auto |
| PC 2 e 3, dopo il primo push | Clone, poi Prompt di ingresso | `sonnet` | `medium` | auto |
| PC 1, subito dopo | `/clear`, poi il Prompt principale | `fable` | `max` | plan |
| Intanto | Uno di voi va allo stand con le domande | — | — | — |
| Tutti, a piano approvato e a ogni fase | `/clear`, poi «Esegui git pull --rebase, leggi docs/PIANO.md e docs/STATO.md e lavora sul compito \[nome\], oppure proponimi il prossimo libero» | `opus` | `xhigh` | auto |
| A ogni ripresa su un PC | Prompt di ingresso | `sonnet` | `medium` | auto |
| Tornati dallo stand | Template A | `opus` | `xhigh` | plan |
| Un agente decide male | Template B | `opus` | `xhigh` | auto |
| Un dato su Napoli non torna | Template C | `opus` | `xhigh` | auto |
| Una schermata non convince | Template D | `opus` | `xhigh` | auto |
| Dopo un checkpoint o una prova di pitch | Template E | `opus` | `xhigh` | plan |
| Prima di ogni checkpoint | Checkpoint con i mentor | `sonnet` | `medium` | auto |
| Bloccati da più di 20 minuti | Sblocco | `fable` | `max` | auto |
| Sab 18:30 e dom 9:30 circa, un solo PC | Giuria simulata | `opus` | `xhigh` | auto |
| Sab 20:00, ogni PC | Chiusura di sabato | `sonnet` | `medium` | auto |
| Dom 8:30, un solo PC | Ripartenza di domenica | `opus` | `xhigh` | plan |
| Dom 10:30, un solo PC | Consegna | `opus` | `xhigh` | auto |

### Come si imposta

- Modello: `/model fable`, `/model opus`, `/model sonnet`. Cambialo subito dopo `/clear`, così non rilegge la conversazione a prezzo pieno.
- Controllo su Fable: nel selettore `/model` la riga Fable deve indicare 5.2 e non «Requires usage credits». Se lo indica, usa `opus` a `max` al suo posto.
- Effort: `/effort max`, `/effort xhigh`, `/effort medium`; `/effort status` mostra quello attivo. Max vale solo per la sessione in corso.
- Plan mode: da auto premi Shift+Tab tre volte, finché in basso appare «plan mode on», oppure scrivi `/plan` davanti al prompt. Il piano si approva con «Yes, and use auto mode».
- Limite: Fable è incluso nel Pro fino al 16 novembre, entro metà del limite settimanale, e consuma più in fretta. Il reset gratuito in Settings > Usage è il jolly per quando finisce.

Fonti: [modello ed effort](https://code.claude.com/docs/en/model-config), [modalità di permesso](https://code.claude.com/docs/en/permission-modes), [offerta Fable 5.2](https://support.claude.com/en/articles/17506494-claude-fable-5-2-launch-offers).

## Lavorare su tre PC

Il contesto viaggia nel repository, non nelle conversazioni: ogni PC riparte da `git pull` e dai file in `docs/`, che Claude Code rilegge a inizio sessione.

| Si condivide con il pull | Resta su ogni PC |
| --- | --- |
| `CLAUDE.md`: regole, lette in automatico | Cronologia delle chat di Claude Code |
| `docs/PROGETTO.md`, `docs/PIANO.md`: concept e piano | `.env` con le chiavi, da creare partendo da `.env.example` |
| `docs/STATO.md`: punto attuale e chi sta lavorando su cosa | Limiti del piano Pro, che sono per account |
| `docs/IPOTESI.md`, `docs/STAND.md`, `docs/FEEDBACK.md` |  |
| `README.md`: stato e registro delle modifiche |  |

### Avvio

Ogni PC, da `Documenti/Progetti/`. Il nome finale dà alla cartella un nome corto:

```
git clone https://github.com/lnrdmnc/N.A.P.L.E.S._Neapolitan-Agentic-Platform-for-Logistics-Experience-and-Safety.git naples
cd naples
claude
```

Chi aveva già clonato il vecchio repository aggiorna l'indirizzo dalla sua cartella:

```
git remote set-url origin https://github.com/lnrdmnc/N.A.P.L.E.S._Neapolitan-Agentic-Platform-for-Logistics-Experience-and-Safety.git
```

Il PC 1 lancia Prompt 0 e poi il Prompt principale. Gli altri due clonano dopo il primo push e usano il Prompt di ingresso; il piano con Fable si fa una volta sola.

### Moduli e coordinamento

Nessun PC ha un'area riservata: chiunque prende qualunque compito, e a evitare i danni pensa la struttura dei file.

- Un modulo, una cartella: ogni modulo ha i suoi file, i suoi test e un README di dieci righe che dice cosa espone.
- Un file per cosa: un agente, una fonte dati, una schermata stanno ciascuno nel proprio file, così due persone non hanno motivo di aprire lo stesso.
- Contratti prima del codice: i moduli si parlano solo attraverso i formati definiti in `contracts/`, committati subito con dati finti. Ognuno sviluppa e prova il suo pezzo da solo.
- Registro dei moduli: un agente o una schermata nuova si aggiunge con una riga in un indice, senza toccare il codice degli altri.

Per organizzarvi c'è la tabella «Chi sta lavorando su cosa» in `docs/STATO.md`. Prima di iniziare un compito Claude Code fa pull, controlla la tabella, scrive la vostra riga e la manda subito su GitHub; se il compito è già preso si ferma e ve lo dice, e decidete voi.

Restano delicati i file che tutti toccano: `README.md`, `docs/STATO.md`, contratti e dipendenze. La regola è pull subito prima e push subito dopo, con modifiche piccole; in caso di conflitto Claude Code si ferma e conserva il lavoro di entrambi.

### Ciclo di commit

Lo esegue Claude Code su ogni PC, perché è scritto in `CLAUDE.md`:

1. `git pull --rebase origin main`.
2. `make check`.
3. Aggiornamento di `README.md` e di `docs/STATO.md`.
4. Proposta del messaggio di commit e attesa: voi confermate o date un altro nome.
5. Commit e push immediato.

I messaggi seguono Conventional Commits, per esempio `feat(sim): add crowd outflow waves`. Niente `git push --force`.

### Prompt di ingresso

Modello `sonnet`, effort `medium`, modalità auto. Va usato al primo avvio sui PC 2 e 3 e a ogni ripresa.

```
Esegui `git pull --rebase origin main`. Leggi CLAUDE.md, README.md, docs/PROGETTO.md,
docs/PIANO.md, docs/STATO.md e gli ultimi venti commit con `git log --oneline -20`. Controlla
che .env esista e contenga le variabili di .env.example, senza mostrarne i valori.
Dimmi in dieci righe: dove siamo, cosa è cambiato dall'ultima volta, chi sta lavorando su
cosa, quali compiti sono liberi e possono partire subito, cosa è bloccato. Non modificare nulla.
```

## Prompt 0 — Avvio nel repository

Modello `sonnet`, effort `medium`, modalità auto. Lo lancia solo il PC 1: crea regole di team e di commit, file di stato e README, e fa il primo push.

Prima copiate il vostro file di progetto nella cartella come `docs/PROGETTO.md`. Poi `/model sonnet`, `/effort medium` e incollate:

```
Prepara questo repository per The Big Hack 2026 (Napoli, 14-15 novembre 2026). È clonato da
https://github.com/lnrdmnc/N.A.P.L.E.S._Neapolitan-Agentic-Platform-for-Logistics-Experience-and-Safety
Ci lavoriamo in tre, da tre PC, ognuno con Claude Code. Non scrivere codice di prodotto: la
challenge arriva nel prossimo messaggio. Se un file esiste già, aggiornalo senza perdere ciò
che contiene.

1. Esegui `date` e raccogli l'ambiente: sistema operativo, versioni di git, node, npm o pnpm,
   python, uv o pip, docker e GPU se presenti, accesso a internet. Riporta tutto in una tabella.
2. Controlla `git remote -v` e il branch (usa main). Aggiungi un .gitignore per Node e Python,
   che escluda .env, e un .env.example con i nomi delle variabili e senza valori.
3. Crea CLAUDE.md con esattamente il contenuto tra i tag <claude_md>.
4. Crea docs/STATO.md con: Scadenze (la tabella tra i tag <scadenze>); la tabella «Chi sta
   lavorando su cosa» (Compito | Chi | Da quando | Nota), vuota; poi Fatto, Prossimi compiti
   liberi, Problemi aperti.
5. Crea docs/IPOTESI.md con una tabella vuota: Dato o ipotesi | Reale o simulato | Fonte o
   criterio | Dove si vede nella demo. Crea docs/STAND.md e docs/FEEDBACK.md vuoti.
6. Se docs/PROGETTO.md esiste, leggilo. Se manca, dimmelo: lo aggiungiamo noi.
7. Crea README.md: nome e descrizione breve presi da docs/PROGETTO.md, Stato attuale, Come
   avviare, Struttura del repository, Team, Registro delle modifiche (una riga per commit, la
   più recente in alto, con data, ora e modulo).
8. Segui la procedura di commit di CLAUDE.md, compresa la richiesta del nome, e fai il push.
   Se il push chiede credenziali che non hai, fermati e dimmelo.

<claude_md>
# N.A.P.L.E.S. — The Big Hack 2026

## Contesto
- Challenge 05 di Fastweb + Vodafone, «Napoli Agentic City». Il nostro progetto è N.A.P.L.E.S.:
  agenti AI per la resilienza urbana di Napoli, con la control room comunale. Il concept sta in
  docs/PROGETTO.md.
- Tre persone, tre PC, stesso repository, branch main. Consegna domenica 15/11 alle 12:00.
- La giuria valuta: utilità e valore, attinenza alla challenge, chiarezza e completezza, design
  e user experience, creatività e innovazione. Lo sponsor guarda visione, originalità,
  concretezza e benefici misurabili.

## Priorità, in ordine
1. Il percorso demo funziona sempre su main, dall'inizio alla fine.
2. Si vede che gli agenti si coordinano e si misura la differenza con e senza coordinamento.
3. Cura dell'interfaccia lungo il percorso demo.
4. Tutto il resto.

## Lavoro in team
- Il contesto condiviso sta nel repository, non nelle conversazioni. A inizio sessione esegui
  `git pull --rebase origin main`, poi leggi docs/STATO.md e docs/PIANO.md.
- Chiunque può lavorare su qualunque modulo: non ci sono aree riservate. Prima di iniziare un
  compito fai pull e guarda la tabella «Chi sta lavorando su cosa» in docs/STATO.md. Se il
  compito è libero aggiungi la riga e mandala subito su GitHub con un commit di quella sola
  riga, `chore(status): claim <compito>`: è l'unico commit che non richiede la conferma del
  nome. Se è già preso fermati e dimmelo: decidiamo noi come dividerci.
- A compito finito togli la riga e aggiorna Fatto e Prossimi compiti liberi.
- Mai `git push --force` e mai riscrivere la storia di main. Se c'è un conflitto fermati,
  mostra i file e proponi la soluzione che conserva il lavoro di entrambi.
- Le chiavi stanno in .env, che non si committa. Ogni variabile nuova va aggiunta a
  .env.example, senza valore.

## Architettura modulare
- Un modulo, una cartella, con i suoi test e un README di dieci righe che dice cosa espone.
- Un file per cosa: un agente, una fonte dati, una schermata stanno ciascuno nel proprio file.
  Se due compiti richiedono lo stesso file, il file va diviso.
- I moduli comunicano solo attraverso i contratti in contracts/ (stato del simulatore,
  messaggi sul bus, API interne). Nessun import dentro la cartella di un altro modulo.
- Un contratto si cambia con un commit piccolo e dedicato, mandato subito su GitHub, con una
  riga in docs/STATO.md che avvisa gli altri.
- Un agente, un adattatore o una schermata nuova si registra aggiungendo una riga a un indice,
  senza modificare il codice degli altri moduli.
- File che tutti toccano (README.md, docs/STATO.md, contratti, dipendenze, configurazione):
  modifiche minime, pull subito prima e push subito dopo.

## Commit
Per ogni commit, in quest'ordine:
1. `git pull --rebase origin main`.
2. `make check` deve passare.
3. Aggiorna README.md (Stato attuale e una riga nuova in cima al Registro delle modifiche) e
   docs/STATO.md.
4. Mostra `git status` e un riepilogo delle modifiche, proponi il messaggio di commit e chiedi
   al team di confermarlo o di dare un altro nome. Aspetta la risposta: non committare prima.
5. Commit, poi push subito.
Messaggio in formato Conventional Commits, `tipo(ambito): descrizione`: in inglese,
all'imperativo, al massimo 72 caratteri, tipi feat, fix, docs, test, refactor, chore, con il
modulo come ambito. Nel corpo il perché, quando non è ovvio. Un commit contiene una sola
modifica logica; niente segreti e niente file generati.

## Regole di lavoro
- A inizio compito esegui `date` e confronta con le scadenze in docs/STATO.md. Se siamo in
  ritardo proponi cosa tagliare dal fondo delle priorità.
- Lavora un compito alla volta. A compito finito segui la procedura di commit, poi fermati con
  il riepilogo e aspetta il via.
- A inizio compito rileggi docs/STAND.md e docs/FEEDBACK.md: contengono risposte dello sponsor
  e prove fatte a mano dal team, e prevalgono sulle tue ipotesi.
- Ogni dato simulato e ogni ipotesi vanno in docs/IPOTESI.md e sono etichettati nell'interfaccia.
  I dati confermati e quelli incerti si distinguono sempre, anche a schermo.
- Ogni evento sismico o di emergenza della demo è simulato ed etichettato come simulazione. Il
  sistema affianca INGV e Protezione Civile, non li sostituisce, e non inventa istruzioni di
  evacuazione. L'operatore approva ogni decisione. Nessun dato personale.
- Il percorso demo funziona offline: ogni chiamata di rete o a un LLM ha cache o esecuzione
  registrata.
- Chiedi prima di usare servizi a pagamento o dipendenze molto pesanti.
- Interfaccia e materiali per la giuria in italiano; codice e commit in inglese.
- Interfaccia con una direzione visiva precisa e coerente, leggibile su un proiettore.
  Controlla ogni schermata del percorso demo con uno screenshot.
- Nel riepilogo di fine compito distingui ciò che funziona da ciò che è simulato, parziale o
  rotto, allega la prova e chiudi con l'elenco di ciò che il team deve provare a mano.

## Comandi
Da compilare appena esistono: installazione, avvio della demo, make check.

## Compact Instructions
Conserva scadenze, compito in corso, decisioni di architettura, comandi e problemi aperti.
</claude_md>

<scadenze>
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
</scadenze>
```

Le 20:30, le 8:30 e le 12:00 sono orari ufficiali; gli altri sono traguardi interni.

## Prompt principale — N.A.P.L.E.S.

Modello `fable`, effort `max`, plan mode, solo sul PC 1. Produce il piano diviso in moduli e compiti indipendenti e si ferma: l'implementazione parte sui tre PC con `opus` a `xhigh`.

Prima: `/clear`, `/model fable`, `/effort max`, Shift+Tab fino a «plan mode on». Poi incollate:

```
Lavoriamo alla Challenge 05 di The Big Hack 2026, «Napoli Agentic City: la città che Ci pensa»,
proposta da Fastweb + Vodafone. Il nostro progetto è N.A.P.L.E.S. Regole, scadenze e procedura
di commit sono in CLAUDE.md; il concept completo è in docs/PROGETTO.md, che prevale su questo
messaggio dove i due differiscono (segnalami le differenze).

<brief>
A Napoli mobilità, turismo, servizi pubblici e ambiente lavorano separati e faticano a
coordinarsi quando arrivano grandi eventi, guasti, allerte o picchi di presenze. La challenge
chiede un sistema di agenti AI che collaborano, coordinati da un orchestratore, con due facce:
«Regia della città» (agenti che coordinano i servizi) e «Assistenti AI per le persone»
(informano, suggeriscono percorsi, prenotano, avvisano su eventi e variazioni). Dati pubblici
e simulazioni realistiche con ipotesi spiegate. Basta un prototipo o la simulazione di uno
scenario, con pochi servizi che lavorano insieme. Si valutano visione, originalità e
concretezza, con benefici misurabili, e va spiegato perché Napoli dovrebbe adottarla.
</brief>

<progetto>
N.A.P.L.E.S. è un sistema di agenti per la resilienza urbana: traffico ed eventi critici
(Campi Flegrei, Vesuvio) gestiti con la control room comunale. L'operatore approva sempre.
- Agenti: Rischio (eventi sismici e vulcanici, meteo; separa dati confermati e incerti),
  Mobilità (linee, strade, sospensioni, alternative), Folla (presenze e deflussi),
  Comunicazione (messaggi a cittadini e turisti, con provenienza), Orchestratore.
- Scenario demo: partita allo stadio Maradona; sciame sismico ai Campi Flegrei; sospensione
  di Cumana e Linea 2; deflusso dallo stadio a ondate; nuovo imprevisto e adattamento.
- Lato utente, per tutti: meteo, traffico, emergenze. Per il turista, in più: storia di
  Napoli e itinerario suggerito, verificato sulle mappe (tempi e percorribilità reali, anche
  rispetto alle sospensioni in corso).
- Registro delle decisioni a prova di manomissione: catena di hash di ogni proposta,
  approvazione e messaggio inviato, con un comando che ne verifica l'integrità. È la base
  dello sviluppo futuro su blockchain permissioned tra enti, che resta fuori dal prototipo.
- Operatori di telecomunicazioni: presenze aggregate (simulate nel prototipo) e canali di
  allerta alla popolazione.
</progetto>

<cosa_conta>
Un sistema multi-agente non si vede: servono a schermo i messaggi tra agenti mentre accadono,
la città che cambia dopo le decisioni approvate, e gli stessi indicatori calcolati con e senza
coordinamento. Gli agenti non sono deterministici, quindi la demo riproduce un'esecuzione
registrata e la logica verificabile (simulatore, vincoli, indicatori, registro) sta fuori dal
modello.
Il tema è l'emergenza: un errore di tono qui costa più di una funzione mancante. Ogni evento
è simulato ed etichettato, le fonti ufficiali restano l'autorità, e la Comunicazione non
invia nulla senza approvazione dell'operatore.
</cosa_conta>

<da_costruire>
1. Simulatore di città deterministico a passi di cinque minuti: zone, capienze, linee, flussi
   di persone, eventi, sospensioni. Scenario in un file, seed fisso.
2. Dati, con 40 minuti al massimo di ricerca: servizio FDSN di INGV per gli eventi sismici;
   feed GTFS dei gestori locali (verifica quali linee coprono, se includono Cumana e Linea 2
   e se esiste GTFS-RT); un'API meteo senza chiave, se esiste; API di mappe per traffico e
   percorsi secondo la chiave che abbiamo, con ripiego su OpenStreetMap; open data e ISTAT.
   Ciò che non si trova è simulato e scritto in docs/IPOTESI.md. Ogni risposta esterna usata
   nella demo ha una copia in cache.
3. Cinque agenti con strumenti propri e messaggi strutturati su un bus osservabile.
   L'Orchestratore risolve i conflitti e produce un piano motivato, con il grado di certezza
   dei dati su cui si basa.
4. Strato LLM indipendente dal provider, sostituibile da configurazione, con un LLM finto a
   risposte fisse per i test e per lavorare senza chiave. Esecuzioni registrabili e
   rieseguibili dalla cache.
5. Control room: mappa a zone, linea del tempo dei messaggi, proposte con impatto stimato,
   approvazione o rifiuto dell'operatore, registro delle decisioni consultabile.
6. Lato utente: meteo, traffico, emergenze; modalità turista con storia di Napoli e itinerario
   verificato. I testi storici vengono da fonti citate, non inventati.
7. Indicatori con e senza coordinamento sullo stesso scenario: tempo di deflusso dallo stadio,
   congestione per zona, minuti tra evento e avviso, minuti per decidere in control room.
8. Strumento di prova per il team: lancia uno scenario e salva in docs/prove/ messaggi, piano e
   indicatori.
</da_costruire>

<architettura_modulare>
Tre PC lavorano in parallelo e chiunque può prendere qualunque compito: nessuna area è
riservata, quindi è la struttura dei file a rendere difficile pestarsi i piedi. Le regole
sono in CLAUDE.md; il piano le traduce in cartelle.
- Proponi i moduli, ognuno con cartella, test e README propri. Indicativamente: contracts,
  sim, un modulo per agente (rischio, mobilita, folla, comunicazione), orchestrator, ledger,
  llm, un adattatore per fonte dati (ingv, gtfs, meteo, mappe), ui/control-room, ui/app, docs.
- I contratti (stato del simulatore, messaggi sul bus, API interne) sono il primo compito: si
  committano subito, con dati finti, così ogni modulo si sviluppa e si prova da solo prima che
  gli altri esistano.
- Agenti, adattatori e schermate si registrano in un indice, una riga ciascuno.
- Il piano elenca i compiti come unità piccole e indipendenti, un modulo o una sua parte,
  ciascuno con: file che tocca, dipendenze, come si verifica, stima. Segna quali possono
  partire in parallelo subito dopo i contratti. Due compiti paralleli non toccano gli stessi
  file; se succede, dividi il file.
- Non assegnare i compiti a persone: li prendiamo noi dalla tabella in docs/STATO.md.
Se il tempo non basta si taglia in quest'ordine: storia di Napoli, imprevisto dal vivo, Vesuvio.
</architettura_modulare>

<verifica>
- Simulatore: le persone si conservano, una capienza superata diventa coda, stesso seed stesso
  risultato.
- Agenti con l'LLM finto: dato un evento, i messaggi attesi compaiono sul bus, il piano
  rispetta i vincoli e nessun messaggio alla popolazione parte senza approvazione.
- Registro: una modifica a una voce passata fa fallire la verifica dell'integrità.
- Contratti: ogni modulo ha un test che valida ciò che produce e ciò che consuma contro
  contracts/, così una rottura tra moduli emerge prima del commit.
- Lo scenario demo gira dalla cache, senza rete, in meno di tre minuti e produce la tabella
  degli indicatori; un test nel browser lo percorre e salva gli screenshot.
- `make check` esegue tutto questo e resta veloce, perché gira prima di ogni commit.
</verifica>

<modo_di_lavorare>
Leggi docs/PROGETTO.md e docs/STAND.md, poi fammi al massimo cinque domande: provider LLM e
chiavi disponibili (modello, mappe), stack del team, cosa conferma o cambia lo scenario.
Proponi il piano con stack, moduli e contratti, struttura del repository, elenco dei compiti
con dipendenze e orari presi da docs/STATO.md e, per ogni compito, cosa deve provare a mano
il team.
Dopo l'approvazione salva il piano in docs/PIANO.md con il brief in testa, riporta i compiti
liberi in docs/STATO.md, aggiorna il README, segui la procedura di commit e fermati: i compiti
partono in sessioni nuove, sui tre PC.
</modo_di_lavorare>

<consegna>
Demo di tre minuti sui passi dello scenario, con la control room, l'avviso al cittadino e al
turista, gli indicatori a confronto e il registro delle decisioni. Pagina «Perché Napoli»,
docs/IPOTESI.md, README aggiornato.
</consegna>
```

A piano approvato, su ogni PC: `/clear`, `/model opus`, `/effort xhigh`, poi «Esegui git pull --rebase, leggi docs/PIANO.md e docs/STATO.md e lavora sul compito \[nome\], oppure proponimi il prossimo libero».

## Domande da fare allo stand

Uno di voi va allo stand di Fastweb + Vodafone mentre Claude pianifica: la prima domanda decide se avete un modello per gli agenti, le altre orientano cosa mostrare.

| Domanda | Cosa cambia per noi |
| --- | --- |
| Mettete a disposizione modelli, API o crediti (MIIA, FastwebAI)? Con quale endpoint, formato e limiti? | Quale modello usano gli agenti. Se sì, usarlo è un punto a favore. |
| Quale destinatario vi interessa di più: turista, cittadino o sala operativa? | Su quale interfaccia mettere la cura maggiore. |
| Preferite profondità sulla regia o sugli assistenti, o conta il legame tra i due? | Ordine delle fasi 3 e 4 e cosa tagliare. |
| Indicatori calcolati su una simulazione, con ipotesi dichiarate, valgono come benefici misurabili? | Quanto investire nel confronto con e senza coordinamento. |
| Avete o consigliate fonti di dati su Napoli, anche aggregati (presenze, mobilità)? | Cosa resta simulato e cosa diventa reale. |
| Quali vincoli contano per voi: dati in Italia, modelli aperti, privacy, supervisione umana? | Contenuto della pagina «Perché Napoli». |
| Cosa vi ha convinto o deluso nei progetti di agenti che avete già visto? | Cosa evitare nella demo. |
| Prenotazioni e acquisti dall'assistente: vi interessa il lato servizi a pagamento? | Se mostrare l'acquisto simulato o tagliarlo. |

Agli organizzatori di Codemotion:

- In che formato si consegna alle 12:00: repository, video, slide, modulo?
- Quanto dura il pitch, è dal vivo, e chi giudica oltre allo sponsor?
- A che ora sono i due checkpoint obbligatori con i mentor?
- Il repository deve essere pubblico?

Scrivete le risposte in `docs/STAND.md`, anche in forma di appunti, e usate il Template A.

## Dove non intervengo: cosa fate voi

Cinque cose restano a voi, e da queste dipende metà del risultato: la chiave del modello, il giudizio sulle decisioni degli agenti, il realismo su Napoli, l'effetto visivo e il pitch.

| Cosa | Perché tocca a voi | Cosa fare | Quando | Come me lo riportate |
| --- | --- | --- | --- | --- |
| Chiave del modello | Il piano Pro non copre l'API e non posso procurarla | Chiedete allo stand; se non offrono nulla, create una chiave presso un provider, provatela con una chiamata vera e mettetela in `.env` | Entro le 14:00 | Template A |
| Decisioni degli agenti | I test verificano i vincoli, non il buon senso | Lanciate lo scenario tre volte e leggete i messaggi in `docs/prove/`: cercate decisioni assurde, ripetute o motivate in modo vago | Fine fase 2 e fine fase 4 | Template B |
| Realismo su Napoli | La città la conoscete voi | Rileggete `docs/IPOTESI.md` voce per voce: zone, capienze, tempi di percorrenza, linee, afflussi di stadio e porto | Fine fase 1 | Template C |
| Effetto visivo | Controllo gli screenshot, non l'effetto in sala | Aprite la demo su uno schermo grande e guardatela da tre metri: in dieci secondi si capisce cosa sta succedendo? | Fine fase 3 e fase 6 | Template D |
| Pitch e demo dal vivo | Parlate voi | Provate ad alta voce con il cronometro, due volte, e decidete chi parla e chi guida la demo | Sabato sera e domenica alle 9:30 | Template E |

Finché la chiave non c'è, le fasi 1 e 2 procedono lo stesso: il simulatore non usa AI e gli agenti girano con l'LLM finto.

Divisione che regge con tre o più persone: una al terminale con Claude Code, una su stand, dati e ipotesi, una su prove a mano e pitch. Chi prova annota tutto in `docs/FEEDBACK.md`, così resta anche tra una sessione e l'altra.

## Template di feedback

Cinque moduli da compilare e incollare in Claude Code; le parentesi quadre sono i campi. Più è preciso il punto in cui avete visto il problema, meno tempo serve per correggerlo.

### A — Risposte dello stand

Modello `opus`, effort `xhigh`, plan mode.

```
Ho scritto in docs/STAND.md le risposte dello sponsor e degli organizzatori. Leggile insieme a
docs/PIANO.md e docs/STATO.md e dimmi, in ordine di impatto: cosa cambia nel piano, cosa si
taglia, cosa si aggiunge, quale configurazione va aggiornata (provider LLM, destinatario
principale, formato di consegna). Non toccare il codice finché non approvo; poi aggiorna
docs/PIANO.md.

Chiave del modello: [provider e nome della variabile in .env, oppure «non ancora»]
Punti che secondo noi contano di più: [una o due righe]
```

### B — Un agente decide male

Modello `opus`, effort `xhigh`, modalità auto.

```
Un agente ha deciso male. Il caso è annotato anche in docs/FEEDBACK.md.
- Esecuzione: [file in docs/prove/ oppure passi per riprodurla]
- Momento dello scenario: [ora simulata o evento]
- Agente: [Mobilità | Flussi turistici | Servizi pubblici | Meteo e ambiente | Orchestratore]
- Cosa ha fatto: [decisione o messaggio, anche copiato]
- Cosa ci aspettavamo e perché: [...]
- Quanto pesa nella demo: [blocca | si nota | dettaglio]
Riproduci il caso e dimmi se la causa sta nel prompt dell'agente, nei suoi strumenti, nei dati
che riceve o nel simulatore, poi correggi lì. Aggiungi un test con l'LLM finto che fissa il
comportamento atteso, rigenera l'esecuzione registrata se è cambiata e mostrami il prima e il
dopo.
```

### C — Un dato su Napoli non torna

Modello `opus`, effort `xhigh`, modalità auto.

```
Un dato o un'ipotesi su Napoli non è realistico.
- Voce di docs/IPOTESI.md o punto dell'interfaccia: [...]
- Cosa c'è ora: [...]
- Com'è nella realtà, per quel che sappiamo: [...]
- Da dove lo sappiamo: [link | esperienza diretta | mentor]
Aggiorna lo scenario e docs/IPOTESI.md, riesegui il confronto con e senza coordinamento e
dimmi se gli indicatori cambiano in modo rilevante. Se la correzione indebolisce il risultato
dimmelo, senza compensare con altre ipotesi.
```

### D — Una schermata non convince

Modello `opus`, effort `xhigh`, modalità auto.

```
Una schermata del percorso demo non convince. Screenshot: [percorso del file]
- Schermata e momento della demo: [...]
- Cosa non si capisce o disturba, vista su schermo grande: [...]
- Cosa deve capire la giuria in dieci secondi: [...]
- Da non cambiare: [...]
Proponi la correzione in due righe, applicala, salva uno screenshot del prima e del dopo in
docs/demo/ e controlla che il test nel browser passi ancora.
```

### E — Dopo una prova di pitch o un checkpoint

Modello `opus`, effort `xhigh`, plan mode.

```
Abbiamo [provato il pitch | fatto un checkpoint con i mentor].
- Durata misurata: [minuti]
- Dove si è inceppata la demo: [...]
- Domande ricevute: [...]
- Osservazioni dei mentor: [...]
- Cosa secondo noi non è arrivato: [...]
Dimmi le tre modifiche con il miglior rapporto tra impatto e tempo, separando ciò che cambia
nel prodotto da ciò che cambia solo nel racconto. Aspetta il mio via, poi aggiorna
docs/PITCH.md e docs/DEMO.md.
```

## Prompt di fase

Sei prompt brevi per i momenti fissi della gara, ciascuno con il suo modello ed effort.

### Prima di un checkpoint con i mentor

Modello `sonnet`, effort `medium`, modalità auto.

```
Tra poco abbiamo un checkpoint con i mentor. Leggi docs/STATO.md e il codice, esegui make check
e scrivi docs/CHECKPOINT.md, una pagina: cosa funziona oggi con la prova, cosa manca, i tre
rischi maggiori, le tre domande più utili da fare ai mentor su agenti, dati di Napoli e demo,
e la sequenza di 60 secondi per mostrare lo stato attuale. Non modificare il codice.
```

### Quando siete bloccati

Modello `fable`, effort `max`, modalità auto. Dopo, tornate a `opus` e `xhigh`.

```
Siamo bloccati su: [descrizione ed errore completo]. Riproduci il problema con un comando o un
test che fallisce, elenca le cause possibili dalla più probabile, verifica la prima e correggi
la causa, non il sintomo. Se in 20 minuti non è risolto fermati e proponimi due strade:
aggirare il problema con una soluzione più semplice, oppure tagliare la funzione, dicendo cosa
cambierebbe nella demo.
```

### Giuria simulata

Modello `opus`, effort `xhigh`, modalità auto. Sabato verso le 18:00 e domenica alle 9:30.

```
Usa un subagent che non ha visto questa conversazione. Dagli il README, la demo avviata, il
brief della challenge che trovi in docs/PIANO.md e docs/STAND.md, e chiedigli di comportarsi
da giurato esigente di Fastweb + Vodafone: voto da 1 a 10 con motivazione per ciascuno dei
cinque criteri (utilità e valore, attinenza alla challenge, chiarezza e completezza, design e
user experience, creatività e innovazione), se si vede davvero che gli agenti collaborano, i
cinque difetti più gravi trovati usando la demo, le cinque domande più scomode per il pitch.
Poi proponimi le tre correzioni con il miglior rapporto tra impatto e tempo.
```

### Chiusura di sabato, alle 20:00

Modello `sonnet`, effort `medium`, modalità auto.

```
Mancano 30 minuti allo stop di oggi. Non iniziare nulla di nuovo. Porta main in uno stato in
cui make check passa, aggiorna docs/STATO.md (fatto, problemi aperti, piano di domani in ordine
di priorità con stime), salva in docs/demo/ gli screenshot del percorso demo e l'esecuzione
registrata dello scenario, fai commit, push e crea il tag sabato-sera. Dimmi cosa conviene
preparare stasera senza toccare il codice.
```

### Ripartenza di domenica, alle 8:30

Modello `opus`, effort `xhigh`, plan mode.

```
Riprendiamo. Leggi CLAUDE.md, docs/STATO.md, docs/PIANO.md e docs/FEEDBACK.md, esegui `date` e
make check. Abbiamo tempo fino alle 10:30 per le funzionalità e fino alle 11:30 per il
pacchetto di consegna. Proponi cosa fare e cosa tagliare, in ordine, con una stima per voce, e
aspetta il mio via.
```

### Consegna, domenica alle 10:30

Modello `opus`, effort `xhigh`, modalità auto.

```
Stop alle funzionalità: da ora solo correzioni sul percorso demo. Prepara il pacchetto di
consegna.
1. Verifica da zero: clona il repository in una cartella temporanea, segui il README alla
   lettera e controlla che la demo parta dalla cache, senza rete. Correggi il README finché
   funziona.
2. docs/PITCH.md: scaletta di tre minuti (problema di Napoli, per chi, demo, come si coordinano
   gli agenti, benefici misurati, perché Napoli dovrebbe adottarla, prossimi passi) e risposte
   brevi alle domande scomode previste.
3. docs/DEMO.md: copione della demo clic per clic, con il piano B se manca la rete.
4. Screenshot o registrazione del percorso demo come riserva.
5. Riepilogo onesto: cosa è reale, cosa è simulato, cosa non funziona.
Prima di impacchettare chiedimi il formato di consegna richiesto dagli organizzatori.
```

## Fonti e punti da verificare

Il brief viene dalla pagina ufficiale e dagli spunti dello sponsor; comandi e limiti di Claude Code dalla documentazione Anthropic.

### Da verificare

- La pagina non indica né il formato di consegna né la durata del pitch: i tre minuti usati nei prompt sono un'ipotesi.
- Non ho verificato quali dati su Napoli siano scaricabili oggi: il Prompt principale dà a Claude Code 40 minuti per cercarli, poi simula.
- Se `/model fable` non apre Fable 5.2, sceglietelo a mano nel selettore `/model`.

### Fonti

- [The Big Hack 2026, pagina ufficiale](https://go.codemotion.com/big-hack-hackathon-2026/)
- [Spunti di Fastweb + Vodafone per la challenge 05](https://drive.google.com/file/d/1m7_FI-kovQf2YiXaj8_aYtsfCEmlGjl5/view?usp=sharing)
- [Fastweb + Vodafone, strategia AI](https://www.corrierecomunicazioni.it/?p=349938)
- [Claude Code: modello ed effort](https://code.claude.com/docs/en/model-config)
- [Claude Code: modalità di permesso](https://code.claude.com/docs/en/permission-modes)
- [Claude Code: best practice](https://code.claude.com/docs/en/best-practices)
- [Claude Code con il piano Pro](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan)
- [Offerte di lancio di Fable 5.2](https://support.claude.com/en/articles/17506494-claude-fable-5-2-launch-offers)
