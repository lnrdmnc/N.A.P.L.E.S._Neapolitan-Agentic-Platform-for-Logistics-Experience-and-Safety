# Script del video pitch

Durata massima **3 minuti**: oltre si viene esclusi (docs/STATO.md). La voce fuori campo conta circa 390 parole: a un ritmo calmo di 2,5 parole al secondo dura 2:40, e il video si chiude a 2:57 con i titoli. Se in prova si sfora, si taglia dalla scena 6, mai dalla 4.

Regole che valgono per ogni inquadratura:

- ogni evento sismico o di emergenza mostrato porta l'etichetta **SIMULAZIONE** ben leggibile;
- nessuna istruzione di evacuazione, né a voce né a schermo;
- si vede sempre che è l'operatore ad approvare;
- i numeri degli indicatori vengono dalla simulazione: si inseriscono dopo l'esecuzione finale, mai a stima;
- nessun volto, targa o dato personale nelle riprese.

## Scene

| # | Tempo | Cosa si vede | Voce fuori campo |
| --- | --- | --- | --- |
| 1 | 0:00–0:12 | Napoli di sera, lo stadio Maradona dall'alto (immagini libere da diritti o mappa animata). Sovrimpressione: «SIMULAZIONE». | Napoli, sera di partita. Cinquantamila persone al Maradona. E se, a dieci minuti dalla fine, ai Campi Flegrei arrivasse uno sciame sismico? |
| 2 | 0:12–0:30 | Quattro riquadri separati che non si parlano: trasporti, protezione civile, folla, comunicazione. Poi un telefono con la notifica «Cumana sospesa» e nient'altro. | Oggi trasporti, protezione civile, gestione della folla e comunicazione lavorano su informazioni separate, proprio quando servirebbe una regia comune. E chi esce dallo stadio sa che la Cumana è ferma, ma non sa quale alternativa prendere, né quanto fidarsi di ciò che legge. |
| 3 | 0:30–0:55 | Logo N.A.P.L.E.S. Schema dei cinque agenti che convergono sull'Orchestratore, e dall'Orchestratore all'operatore. | Questo è N.A.P.L.E.S.: cinque agenti AI che lavorano insieme. Rischio legge i dati sismici e meteo e separa ciò che è confermato da ciò che è incerto. Mobilità valuta linee e percorsi, Folla stima i deflussi, Comunicazione prepara i messaggi. L'Orchestratore unisce le proposte, risolve i conflitti e presenta un solo piano. E a decidere è sempre una persona: l'operatore della control room comunale. |
| 4 | 0:55–1:50 | Registrazione dello schermo, control room e vista cittadino affiancate. Minuto 70: scossa simulata Md 3.1, ricalcata su una scossa vera del 1° agosto; la linea del tempo dei messaggi tra agenti si riempie; il piano con il grado di certezza di ogni dato; clic su **Approva**; l'avviso compare sul telefono. Poi il post «crolli a Bagnoli» con l'etichetta «non verificata» solo in control room, e l'allerta meteo ufficiale inoltrata tale e quale. | Guardiamolo all'opera. Minuto settanta: scossa simulata di magnitudo 3.1, ricalcata su una scossa vera di quest'estate. Rischio la segnala come evento rilevato, in attesa delle comunicazioni ufficiali. Mobilità propone di sospendere Cumana e Linea 2, Folla un deflusso a ondate, settore per settore. Dove le proposte si contraddicono, l'Orchestratore sceglie e spiega perché. L'operatore legge il piano e approva. In quel momento il telefono del tifoso riceve l'avviso: quale linea è ferma, dove prendere la navetta, quando uscire. Sempre con la fonte. Un post parla di crolli a Bagnoli: N.A.P.L.E.S. non lo rilancia, lo segnala all'operatore come non verificato. E l'allerta meteo ufficiale arriva ai cittadini senza cambiare una parola. |
| 5 | 1:50–2:15 | Indicatori affiancati, con e senza coordinamento, con l'origine accanto a ogni numero (calcolato, misurato, ipotesi). Poi il registro delle decisioni con la verifica della catena che passa. | Il beneficio non lo dichiariamo: lo misuriamo. Stesso scenario, stesso simulatore, con e senza coordinamento. Deflusso dallo stadio: [X] minuti invece di [Y]. Congestione nella zona più carica: [X] invece di [Y]. Le ipotesi sono dichiarate, una per una. E ogni proposta, approvazione e messaggio finisce in un registro a catena di hash, che nessuno può modificare di nascosto. |
| 6 | 2:15–2:27 | Pagina «Perché Napoli», oppure il golfo con il Vesuvio e i Campi Flegrei sulla mappa. | Perché Napoli? Perché pochi posti convivono con un'area vulcanica attiva, grandi eventi e tanti visitatori. N.A.P.L.E.S. non sostituisce INGV e Protezione Civile: li affianca, e porta alle persone ciò che serve per muoversi. |
| 7 | 2:27–2:52 | Mockup di un'app per smartphone con l'avviso in notifica. Poi la mappa a zone che si colora da sola, con due icone: rete mobile e telecamera, con la scritta «dati aggregati e anonimi». | E questo è solo l'inizio. Quando Napoli adotterà N.A.P.L.E.S., il passo successivo sarà un'app per smartphone, che porta gli avvisi in tasca a cittadini e turisti. E il controllo in tempo reale diventerà ancora più preciso: con le presenze lette dalle SIM sulla rete mobile e con le telecamere di sicurezza della città. Sempre in forma aggregata e anonima, contando le persone senza identificarle. |
| 8 | 2:52–2:57 | Logo e titolo, link al repository. | N.A.P.L.E.S.: la città che ci pensa. |

## Prima di registrare

- [ ] Schermate necessarie alla scena 4: linea del tempo (C2), piano con Approva (C3), avviso nella vista cittadino (U1). Se una manca all'ora della registrazione, si riprende ciò che c'è e si accorcia la voce della scena 4, senza mostrare funzioni che non esistono.
- [ ] Numeri della scena 5 presi dall'esecuzione finale di `make prova` o dalla schermata indicatori; se un numero è un'ipotesi, a schermo deve risultare tale.
- [ ] Livello di allerta vulcanica: se compare a schermo, verificato sulla fonte ufficiale (docs/IPOTESI.md).
- [ ] Il mockup dell'app della scena 7 è etichettato «sviluppo futuro».
- [ ] Lettura ad alta voce con cronometro: entro 2:57, titoli compresi.
- [ ] Musica e immagini libere da diritti; nessun marchio nel nome del team.

## Note per la scena 7

L'app nativa è già indicata come sviluppo futuro in docs/PROGETTO.md (6.1). I dati di presenza dalla rete mobile sono il collegamento con gli operatori di telecomunicazioni (PROGETTO.md, sezione 10): nel prototipo sono simulati. Per SIM e telecamere la voce dice sempre «aggregata e anonima»: il progetto non tratta dati personali, e la giuria lo nota.
