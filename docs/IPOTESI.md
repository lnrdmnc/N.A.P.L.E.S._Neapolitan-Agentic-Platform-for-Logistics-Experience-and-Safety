# Ipotesi e dati simulati

| Dato o ipotesi | Reale o simulato | Fonte o criterio | Dove si vede nella demo |
| --- | --- | --- | --- |
| Scosse ai Campi Flegrei (Md 3.2, 2.6, 2.8 ai minuti 70, 71, 101) | Simulato | Scelte per lo scenario; formato come gli eventi INGV | Control room: eventi e piano; avvisi del caso B |
| Sospensione di Cumana e Linea 2 dopo le scosse | Simulato | Plausibile: verifiche dopo un evento sismico; da confermare con i protocolli dei gestori | Stato delle linee, piano, avvisi |
| Cumana e Linea 2 di nuovo in servizio al minuto 130 (22:55); scenario lungo 170 minuti per mostrare la chiusura dello sciame | Simulato | Scelte per mostrare l'aggiornamento «di nuovo in servizio» e il cessato allarme operativo (minuto 162, 60 minuti dopo l'ultima scossa) | Avvisi: `Update` alle 22:55, `Cancel` alle 23:27 |
| Budget anti-allarme: un aggiornamento parte solo se cambiano gravità o istruzioni per la persona | Regola del sistema | Scelta di progetto contro la stanchezza da allarmi | La scossa delle 22:26 non genera notifiche |
| Allerta meteo gialla e testo ufficiale | Simulato | Testo inventato ed etichettato «SIMULAZIONE» | Avviso ufficiale inoltrato senza modifiche (caso A) |
| Post social «crolli a Bagnoli» | Simulato | Inventato per mostrare il caso C | Piano: segnalazione all'operatore, nessun avviso pubblico |
| Livello di allerta vulcanica dei Campi Flegrei «giallo» | Da verificare | Va controllato sulla fonte ufficiale prima della demo | Contesto in control room |
| 50.000 spettatori e ripartizione per settore (Curve A e B 12.000, Tribune Posillipo e Nisida 8.000, Distinti 10.000) | Simulato | Ordine di grandezza della capienza; ripartizione inventata | Ondate di deflusso |
| Capacità persone al minuto: Linea 2 80, Cumana 30, bus ordinari 60, a piedi e con mezzi propri 700, navette 100 | Simulato | Ordini di grandezza ricalibrati il 14/11 alle 16:30 (prima erano 400, 300, 150, 450, 500: gonfiati). Ferro: un treno ogni 10–20 minuti; navette: circa un bus al minuto da un punto di carico. Da verificare con frequenze GTFS e capienze reali | Indicatori con e senza coordinamento |
| Uscita massima dallo stadio 2.500 persone al minuto | Simulato | Valore di lavoro | Indicatori |
| Ondate: tribune subito, Distinti dopo 8 minuti, curve dopo 16 | Simulato | Scelta dell'agente Folla | Avvisi ai tifosi, indicatori |
| Navette sostitutive con destinazione Bagnoli e Pozzuoli | Simulato | Scelta per il profilo pendolare; percorsi non verificati | Avvisi del profilo «pendolare» |
| Navette operative 12 minuti dopo la decisione | Simulato | Valore di lavoro | Indicatori |
| Punti di carico: Piazzale Tecchio, Viale Giochi del Mediterraneo; percorso pedonale via Terracina | Da verificare | Luoghi reali di Fuorigrotta; idoneità non verificata | Piano, conflitto risolto dall'Orchestratore, avvisi |
| Senza coordinamento: le persone scoprono le sospensioni 15 minuti dopo il fischio finale (davanti alle stazioni chiuse), decisione sulle navette dopo 20; capacità dimezzata finché non sanno | Ipotesi | Scenario di confronto. Fino al 14/11 alle 16:30 il ritardo si contava dalla sospensione (minuto 72) e quindi non aveva mai effetto: corretto | Indicatori «senza coordinamento» |
| Con coordinamento: informazione dopo 3 minuti, decisione dopo 2 | Ipotesi | Tempo per approvare il piano in control room | Indicatori «con coordinamento» |
| Percorsi pedonali alternativi: capacità a piedi × 1,3 | Ipotesi | Effetto della distribuzione su più direzioni | Indicatori «con coordinamento» |
| Soglie sismiche: attenzione Md ≥ 2,5, moderato ≥ 3,0, severo ≥ 4,0; sciame = scosse entro 60 minuti | Ipotesi | Soglie di lavoro, non soglie ufficiali | Gravità degli avvisi del caso B |
| Area dell'avviso: rettangolo intorno allo stadio | Simulato | Coordinate approssimate | Campo `area` degli avvisi |
| Simulatore a zone: capienze di attesa (Piazzale Tecchio 6.000, Viale Giochi del Mediterraneo 4.000, stazione Campi Flegrei 1.500, stazione Mostra 1.000, fermata Marino - Stadio Maradona 800) | Simulato | Ordini di grandezza, da verificare voce per voce | Carico per zona sulla mappa |
| Quote modali all'uscita dallo stadio: a piedi e mezzi propri 55%, Linea 2 20%, Cumana 10%, bus 15% | Ipotesi | Valori di lavoro, non misurati | Simulatore a zone |
| Coordinate delle zone | Reale in parte | Fermate dal GTFS ANM (5001 Piazzale Tecchio, 6277 Campi Flegrei, 2299 Marino - Stadio Maradona); stadio, stazione Mostra e Viale Giochi approssimati | Mappa |
| Chi è informato lascia le stazioni chiuse e le code oltre la capienza e ripiega su navette e piedi in proporzione alla capacità; chi non è informato aspetta | Ipotesi | Regola di comportamento del simulatore a zone | Code alle stazioni nel caso senza coordinamento |
| Nella sessione conta solo ciò che è approvato: ondate solo se approvate entro il fischio finale; navette operative 12 minuti dopo l'approvazione; persone informate dal primo avviso approvato con le sospensioni. Senza approvazioni le persone scoprono le sospensioni da sole, 15 minuti dopo il fischio | Ipotesi | Regole di `decisioni.py` | Mappa della sessione, impatto del piano |
| Ricezione degli avvisi: persone raggiungibili per profilo (tifosi 40.000, residenti 15.000, pendolari 6.000, turisti 4.000, tutti 65.000), quota con l'app 25%, lettura 40% entro 2 minuti, 65% entro 5, 85% entro 15 | Simulato | Valori di lavoro per le stime; le conferme reali dei telefoni in demo sono contate a parte (`visti_reali`) | Control room: ricezione degli avvisi |

## Sensibilità del confronto

Dal 14/11 alle 17:25 gli indicatori vengono dal **simulatore a zone**, lo stesso della mappa (prima da un modello aggregato più semplice). Il beneficio va presentato come **intervallo**, non come numero unico. Calcolato con `make prova` sullo scenario attuale (deflusso: minuti dal fischio finale allo sgombero dell'area; picco: massimo di persone in attesa fuori dallo stadio):

| Percorsi a piedi (fattore) | Decisione senza coordinamento | Deflusso con → senza | Picco con → senza |
| --- | --- | --- | --- |
| 1,0 (nessun effetto) | 10 min | 64 → 59 | 28.361 → 32.800 |
| 1,0 (nessun effetto) | 20 min | 64 → 60 | 28.361 → 33.700 |
| 1,3 (valore usato) | 20 min | 50 → 60 | 23.299 → 33.700 |
| 1,5 | 20 min | 43 → 60 | 19.840 → 33.700 |

Lettura onesta:

- **Robusto, vale con ogni ipotesi:** il coordinamento riduce il picco di persone in attesa (circa −14% anche senza l'ipotesi sui percorsi a piedi, −31% con il valore usato) e **nessuno si ammassa davanti alle stazioni chiuse** (con coordinamento 0; senza, la stazione Campi Flegrei arriva a 5 volte la capienza).
- **Dipende da un'ipotesi:** lo sgombero più rapido (50 contro 60 minuti) esiste solo se i percorsi pedonali alternativi aumentano davvero la capacità a piedi. Senza quell'effetto il coordinamento non accelera lo sgombero, anzi lo allunga di qualche minuto, perché le ondate fanno uscire le curve più tardi. Va detto.
- Il messaggio corretto per il pitch è quindi **meno affollamento e nessuna folla davanti alle stazioni chiuse**, non «sgomberiamo prima».
- Nella sessione, appena l'operatore approva un piano dopo la sospensione, il caso «con coordinamento» usa le sue decisioni vere e i tempi diventano «misurati in sessione»; il caso «senza coordinamento» resta un'ipotesi.
