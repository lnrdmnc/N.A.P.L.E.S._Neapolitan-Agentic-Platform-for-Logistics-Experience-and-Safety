# N.A.P.L.E.S. — Neapolitan Agentic Platform for Logistics, Experience and Safety

The Big Hack 2026 · Challenge 05 «Napoli Agentic City: la città che Ci pensa» (Fastweb + Vodafone)

## 1. Abstract

N.A.P.L.E.S. è un sistema di agenti AI per la resilienza urbana di Napoli. Nasce da un'osservazione della challenge: mobilità, turismo, servizi pubblici e ambiente sono gestiti da sistemi separati e, davanti a un grande evento o a un'emergenza, ogni servizio agisce per conto proprio proprio quando servirebbe una regia comune.

Il sistema mette a collaborare cinque agenti: Rischio, Mobilità, Folla, Comunicazione e un Orchestratore. Il Rischio segue eventi sismici, vulcanici e meteo e distingue i dati confermati da quelli incerti. La Mobilità valuta linee, strade, sospensioni e percorsi alternativi. La Folla stima presenze e deflussi da stadio e stazioni. La Comunicazione prepara i messaggi per i cittadini, indicando la provenienza dell'allerta. L'Orchestratore integra le proposte, risolve i conflitti e presenta un piano motivato.

Il destinatario principale è il cittadino, che riceve informazioni tempestive e percorsi alternativi su meteo, traffico ed emergenze. Il turista è un caso in più, con la storia di Napoli e un itinerario verificato sulle mappe. L'operatore della control room comunale non è il destinatario: supervisiona e approva ogni decisione degli agenti, e nessun messaggio parte senza il suo via. Ogni proposta, approvazione e messaggio finisce in un registro delle decisioni a prova di manomissione, basato su una catena di hash.

Il prototipo dimostra il sistema su uno scenario simulato: una partita allo stadio Maradona, uno sciame sismico simulato ai Campi Flegrei, la sospensione di Cumana e Linea 2, un deflusso a ondate e un imprevisto durante il deflusso. Gli stessi indicatori sono calcolati con e senza coordinamento tra agenti, così il beneficio si misura nella simulazione invece di essere dichiarato.

N.A.P.L.E.S. affianca INGV e Protezione Civile, che restano l'autorità, e non li sostituisce. Ogni evento sismico mostrato è una simulazione ed è etichettato come tale.

## 2. Traccia della challenge

**Il Contesto e la Sfida**

Napoli è una delle mete turistiche più visitate d'Italia e vuole essere sempre di più una città capace di offrire servizi di qualità anche a chi ci vive ogni giorno.

Mobilità, turismo, servizi pubblici e ambiente sono spesso gestiti da sistemi separati, che faticano a dialogare tra loro. Così, di fronte a un grande evento, un guasto, un'allerta meteo o un picco di arrivi turistici, ogni servizio tende ad agire per conto proprio, proprio quando la città avrebbe più bisogno di una regia comune.

Progetta un sistema di agenti AI capaci di collaborare tra loro: ciascuno si occupa di un servizio o di un problema specifico, mentre un agente orchestratore li coordina, mette insieme le informazioni e propone risposte intelligenti anche quando la situazione cambia.

Scegli tu il problema da risolvere. Pensa, ad esempio, a una giornata in cui Napoli deve gestire contemporaneamente migliaia di persone: una regata dell'America's Cup, una partita di calcio, l'arrivo di più navi da crociera. Oppure un guasto alla metropolitana che cambia improvvisamente i programmi di cittadini e turisti.

E scegli il target, decidendo a chi vuoi rendere la vita più semplice: al turista che cerca alternative a luoghi sovraffollati, al cittadino che deve raggiungere un ufficio pubblico, oppure all'operatore della sala operativa comunale che deve prendere decisioni in pochi minuti. Puoi rivolgerti anche a più destinatari. Decidi quali servizi far collaborare e come l'AI può fare la differenza.

Immagina anche come gli agenti AI possano affiancare cittadini e turisti come assistenti personali, capaci non solo di fornire informazioni, ma anche di suggerire soluzioni, anticipare esigenze e facilitare l'accesso a servizi, prenotazioni e acquisti. Potrebbero nascere così nuovi servizi digitali, utili nella vita quotidiana, e nuove opportunità di business per le imprese del territorio.

Usa le fonti pubbliche che ritieni più utili: open data del Comune e della Regione, trasporto pubblico, dati ISTAT, mappe e meteo. Dove mancano dati reali, puoi utilizzare simulazioni realistiche, spiegando le ipotesi adottate.

Illustra come funziona la tua soluzione: puoi utilizzare un semplice prototipo, una demo o una simulazione di uno scenario concreto, in cui si veda come gli agenti si coordinano e reagiscono ai cambiamenti. Non serve collegare tutta la città: bastano pochi servizi che lavorano insieme.

Vince chi saprà combinare visione, originalità e concretezza, mostrando come la collaborazione tra agenti AI possa produrre benefici tangibili e possibilmente misurabili: meno attese, meno congestione, informazioni più tempestive, decisioni più rapide o nuovi servizi per cittadini e turisti.

Mostraci come funzionerebbe la tua idea, quale differenza potrebbe fare e perché Napoli dovrebbe adottarla.

## 3. Problema e soluzione

### Problema

Quando a Napoli si sovrappongono un grande evento, un'interruzione dei trasporti e un'allerta, i servizi coinvolti (mobilità, protezione civile, gestione delle folle, comunicazione ai cittadini) lavorano su informazioni separate. Chi vive la città, o la visita, si trova senza un quadro unico: sa che la linea è sospesa, ma non quale alternativa è percorribile, né quanto siano certe le notizie che riceve. Le decisioni rischiano di arrivare in ritardo, di contraddirsi o di raggiungere le persone senza chiarire la provenienza e l'attendibilità dell'informazione.

### Soluzione

Un sistema multi-agente coordinato da un Orchestratore, che mette il cittadino al centro:

- ogni agente osserva un ambito e produce proposte strutturate, con il grado di certezza dei dati su cui si basano;
- l'Orchestratore integra le proposte, risolve i conflitti e presenta un unico piano motivato;
- la control room comunale supervisiona: l'operatore approva o rifiuta ogni decisione, e solo quelle approvate diventano messaggi per i cittadini;
- ogni passaggio è registrato in modo verificabile;
- il beneficio si misura confrontando gli stessi indicatori sullo stesso scenario, con e senza coordinamento.

Il prototipo copre pochi servizi che lavorano insieme su uno scenario simulato, come richiesto dalla traccia. Il destinatario principale è il cittadino; il turista è un caso in più, con storia di Napoli e itinerario verificato (sezione 6). L'operatore non è il destinatario del servizio, ma il garante delle decisioni.

## 4. Gli agenti

| Agente | Compito | Dati | Cosa propone all'operatore |
| --- | --- | --- | --- |
| Rischio | Segue eventi sismici e vulcanici (Campi Flegrei, Vesuvio) e meteo; separa i dati confermati da quelli incerti | INGV via FDSN, meteo | Livello di attenzione con grado di certezza dei dati; da definire il formato esatto |
| Mobilità | Stato di linee e strade, sospensioni, percorsi alternativi | Feed GTFS dei gestori locali, API di mappe | Sospensioni o modifiche di servizio e percorsi alternativi con impatto stimato; da definire il formato esatto |
| Folla | Stima presenze e deflussi da stadio e stazioni, organizza il deflusso a ondate | Capienze, ISTAT, presenze aggregate simulate | Piano di deflusso a ondate con tempi stimati; da definire il formato esatto |
| Comunicazione | Messaggi a cittadini e turisti, con provenienza dell'allarme | Decisioni approvate dall'operatore | Bozze di messaggio con provenienza dell'informazione, da approvare prima dell'invio |
| Orchestratore | Integra le proposte, risolve i conflitti, presenta il piano alla control room | Messaggi degli altri agenti | Un piano unico e motivato, con il grado di certezza dei dati e i conflitti risolti |

## 5. Scenario demo

Tutti gli eventi sismici dello scenario sono simulati ed etichettati come tali sullo schermo.

1. **Partita allo stadio Maradona**, città in condizioni normali.
2. **Sciame sismico ai Campi Flegrei, simulato.**
3. **Sospensione di Cumana e Linea 2.**
4. **Deflusso dallo stadio a ondate**, coordinato dagli agenti.
5. **Nuovo imprevisto e adattamento del piano.** Un'allerta meteo e una scossa simulata durante il deflusso dallo stadio.
6. **Bilancio:** indicatori a confronto e registro delle decisioni. *Passo proposto, da confermare o sostituire con il sesto passo del file di progetto del team.*

## 6. Funzioni lato utente

**Per il cittadino (destinatario principale)**

- meteo
- traffico
- emergenze, con messaggi approvati dall'operatore e provenienza dell'informazione

**Per il turista, in più**

- storia di Napoli, con testi da fonti citate
- itinerario suggerito, verificato sulle mappe (tempi e percorribilità, anche rispetto alle sospensioni in corso)

La control room non è un'interfaccia per l'utente finale: è lo strumento con cui l'operatore supervisiona e approva le decisioni degli agenti.

## 7. Dati e fonti

Nessuna delle fonti sotto è stata ancora verificata dal team su Napoli: la disponibilità, la copertura e i formati vanno controllati nella fase dati.

### Verificato

- Da definire. Al momento della stesura non risulta verificata alcuna fonte.

### Da verificare

| Ambito | Fonte indicata | Cosa resta da verificare |
| --- | --- | --- |
| Sismica | INGV via servizio FDSN | Endpoint, formato e uso nella demo (con copia in cache) |
| Meteo | Open-Meteo come candidato, senza chiave | Scelta dell'API e dei limiti d'uso |
| Trasporti | Feed GTFS dei gestori locali | Quali linee coprono, se includono Cumana e Linea 2, se esiste il tempo reale (GTFS-RT) |
| Traffico e mappe | API di mappe con traffico in tempo reale; ripiego su OpenStreetMap senza traffico reale | Quale API, chi crea la chiave e l'account di fatturazione |
| Open data e statistiche | Open data comunali e regionali, ISTAT | Quali dataset servono e sono scaricabili |
| Presenze | Dati aggregati degli operatori di telecomunicazioni | Nel prototipo sono simulati |

### Simulato

Ciò che non si trova nelle fonti è simulato, con le ipotesi dichiarate in `docs/IPOTESI.md` ed etichettato nell'interfaccia. Sono simulati almeno: gli eventi sismici dello scenario, le presenze aggregate e i flussi di persone. Ogni risposta esterna usata nella demo ha una copia in cache, così la demo gira senza rete.

## 8. Benefici misurabili

I benefici si calcolano nella simulazione, sullo stesso scenario, con e senza coordinamento tra agenti. Gli indicatori sono:

- tempo di deflusso dallo stadio
- congestione per zona
- minuti tra evento e avviso
- minuti per decidere in control room

Valori e risultati: da definire. Si ottengono solo eseguendo la simulazione e non vengono stimati in anticipo. Le ipotesi su cui si basano sono dichiarate in `docs/IPOTESI.md`.

## 9. Etica e privacy

- **Simulazione dichiarata:** ogni evento sismico o di emergenza della demo è simulato ed etichettato come simulazione sullo schermo.
- **Fonti ufficiali:** il sistema affianca INGV e Protezione Civile, che restano l'autorità; non li sostituisce e non inventa istruzioni di evacuazione.
- **Supervisione umana:** l'operatore approva ogni decisione; la Comunicazione non invia nulla senza la sua approvazione.
- **Trasparenza sui dati:** dati confermati e incerti sono distinti sempre, anche a schermo; ogni messaggio indica la provenienza.
- **Privacy:** nessun dato personale; le presenze sono dati aggregati, simulati nel prototipo.
- **Tracciabilità:** il registro delle decisioni a catena di hash permette di verificare che le voci passate non siano state modificate.

## 10. Sviluppi futuri

### Blockchain tra enti

Il registro delle decisioni del prototipo è la base di una blockchain permissioned tra Comune, gestori dei trasporti, Protezione Civile e operatori di telecomunicazioni. Sulla catena andrebbero solo gli hash, per restare conformi al GDPR. Le due opzioni da valutare sono Hyperledger Fabric oppure l'ancoraggio degli hash su una blockchain pubblica. Resta fuori dal prototipo.

### Operatori di telecomunicazioni

Gli operatori entrano in due punti:

- dati aggregati sulla presenza di persone, simulati nel prototipo;
- canali di allerta alla popolazione.

È il collegamento naturale con Fastweb + Vodafone.

### Altro

Prenotazioni e acquisti dall'assistente, citati dalla traccia, restano fuori dal prototipo e sono un possibile sviluppo futuro. Altri sviluppi: da definire.

## 11. Punti aperti

- [ ] Nome del team
- [ ] Titolo definitivo del progetto
- [ ] Verifica dei feed GTFS: linee coperte e tempo reale
- [ ] Scelta dello stack
- [ ] Conferma dello scenario e del sesto passo
- [ ] API meteo e API di mappe: quale, e chi ha la chiave
- [ ] Formato delle proposte di ciascun agente
- [ ] Verifica delle fonti dati su Napoli
