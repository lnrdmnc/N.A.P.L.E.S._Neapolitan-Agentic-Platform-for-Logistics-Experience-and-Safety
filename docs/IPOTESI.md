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
| Navette operative 12 minuti dopo la decisione | Simulato | Valore di lavoro | Indicatori |
| Punti di carico: Piazzale Tecchio, Viale Giochi del Mediterraneo; percorso pedonale via Terracina | Da verificare | Luoghi reali di Fuorigrotta; idoneità non verificata | Piano, conflitto risolto dall'Orchestratore, avvisi |
| Senza coordinamento: le persone scoprono le sospensioni 15 minuti dopo il fischio finale (davanti alle stazioni chiuse), decisione sulle navette dopo 20; capacità dimezzata finché non sanno | Ipotesi | Scenario di confronto. Fino al 14/11 alle 16:30 il ritardo si contava dalla sospensione (minuto 72) e quindi non aveva mai effetto: corretto | Indicatori «senza coordinamento» |
| Con coordinamento: informazione dopo 3 minuti, decisione dopo 2 | Ipotesi | Tempo per approvare il piano in control room | Indicatori «con coordinamento» |
| Percorsi pedonali alternativi: capacità a piedi × 1,3 | Ipotesi | Effetto della distribuzione su più direzioni | Indicatori «con coordinamento» |
| Soglie sismiche: attenzione Md ≥ 2,5, moderato ≥ 3,0, severo ≥ 4,0; sciame = scosse entro 60 minuti | Ipotesi | Soglie di lavoro, non soglie ufficiali | Gravità degli avvisi del caso B |
| Area dell'avviso: rettangolo intorno allo stadio | Simulato | Coordinate approssimate | Campo `area` degli avvisi |

## Sensibilità del confronto

Il beneficio va presentato come **intervallo**, non come numero unico. Calcolato con `make prova` sullo scenario attuale (deflusso in minuti dal fischio finale; picco di persone in attesa fuori dallo stadio):

| Percorsi a piedi (fattore) | Decisione senza coordinamento | Deflusso con → senza | Picco con → senza |
| --- | --- | --- | --- |
| 1,0 (nessun effetto) | 10 min | 58 → 65 | 27.640 → 38.500 |
| 1,0 (nessun effetto) | 20 min | 58 → 66 | 27.640 → 39.400 |
| 1,3 (valore usato) | 20 min | 47 → 66 | 22.180 → 39.400 |
| 1,5 | 20 min | 41 → 66 | 18.540 → 39.400 |

Lettura onesta: anche senza alcun effetto dei percorsi a piedi il coordinamento riduce il deflusso di circa 7 minuti e il picco di circa il 28%, perché le persone sanno prima dell'uscita che le stazioni sono chiuse. Il tempo di decisione senza coordinamento pesa poco. Il dato più incerto resta il ritardo d'informazione senza coordinamento (15 minuti): è un'ipotesi e va detto.
