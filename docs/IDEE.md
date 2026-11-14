# Idee e punti di forza — check di sabato 14/11, 16:00

Quattro agenti esperti di smart city hanno letto il repository in sola lettura, ciascuno da un punto di vista: **cittadini**, **turisti**, **telco e mobilità** (lo sguardo di Fastweb + Vodafone), **giuria**. Qui c'è la sintesi. Le idee rispettano i vincoli del progetto: operatore sempre nel ciclo, allerte ufficiali mai riscritte, nessuna evacuazione inventata, nessun dato personale, simulato sempre etichettato.

## Punti di forza

- **Cittadini.** I tre casi di allerta sono nel codice: l'ufficiale si inoltra intatta, l'evento rilevato dice «nessun allarme ufficiale, segui la Protezione Civile», la notizia non verificata non diventa mai un avviso. Avvisi per profilo con istruzioni concrete (turni di uscita, punto navette, «evita i sottopassi»). Fonte sempre citata.
- **Turisti.** Avvisi già in inglese; l'endpoint dell'itinerario ha la forma definitiva (percorribile, motivo, alternativa).
- **Sponsor.** Il CAP è il linguaggio del cell broadcast; registro tracciabile; ogni numero dichiara l'origine; dati reali verificati (GTFS ANM con L2, GTFS EAV con Cumana, INGV).
- **Giuria, voto atteso oggi:** attinenza 5, utilità 3, chiarezza 3, creatività 3, design/UX 2 (sale a 3–4 solo con control room e telefono affiancati entro le 20:30).

## Problemi trovati (verificati sul codice)

1. **Numeri poco credibili.** Il ritardo d'informazione «senza coordinamento» non aveva effetto (scattava al minuto 87, il deflusso parte al 95); capacità di navette, Linea 2 e Cumana gonfiate; il vantaggio veniva quasi tutto da due ipotesi. *In correzione: vedi docs/IPOTESI.md.*
2. **Troppi avvisi.** 19 avvisi in 70 minuti di simulazione; il conflitto su Piazzale Tecchio ricompare in ogni piano. Sembra allarmista.
3. **Manca il cessato allarme.** `Cancel` è nel contratto ma non viene mai generato.
4. **Allerta ufficiale solo in italiano** per il turista, senza spiegazione.
5. **Concetto da correggere.** Il cell broadcast è unidirezionale e non distingue i profili: la conferma di ricezione esiste solo nella PWA. IT-Alert è della Protezione Civile: le informazioni operative passano da un canale separato (PWA o SMS su adesione).

## Da fare stasera, in ordine

| # | Idea | Da chi | Tempo | Dove |
|---|---|---|---|---|
| 1 | ✅ Numeri credibili: bug del ritardo, capacità realistiche, sensibilità delle ipotesi | Telco, giuria | fatto | agenti |
| 2 | ✅ Budget anti-allarme: aggiornamento solo se cambiano gravità o istruzioni; conflitto mostrato una volta sulla linea del tempo | Giuria | fatto | agenti |
| 3 | ✅ Cessato allarme operativo (`Cancel`) quando lo sciame si chiude, `Update` quando le linee ripartono; rimanda sempre alla Protezione Civile per il rischio | Cittadini | fatto | agenti |
| 4 | ✅ Allerta ufficiale con cornice in inglese: «Official alert – original Italian text below, not translated», testo intatto | Turisti | fatto | agenti |
| 5 | Veto dell'operatore che cambia la città: Approva, Modifica, Rifiuta cambiano mappa e coda | Giuria | B1 + B2 + C3 | backend + web app |
| 6 | La notizia falsa fermata: control room e telefono nella stessa inquadratura | Giuria | solo UI | web app |
| 7 | Presenze aggregate per cella (simulate, soglia di anonimato) come input dell'agente Folla: l'aggancio diretto con Fastweb + Vodafone | Telco | 1–3h | con S0 |
| 8 | ✅ Profilo «pendolare flegreo»: chi torna verso Pozzuoli e Bagnoli con la Cumana sospesa | Cittadini, giuria | fatto | agenti |

## Nel pitch, come visione

- Due canali: IT-Alert ufficiale, inoltrato, e un canale operativo su adesione.
- Area dell'avviso come insieme di celle, non come rettangolo.
- La rete come sensore: un picco anomalo di traffico dopo una scossa diventa un segnale «stimato».
- Modello di business: licenza per il Comune, servizio a evento, insight aggregati dall'operatore.
- 5G ed edge vicino allo stadio.
- Crocieristi con «rientro al porto garantito»; fasce orarie consigliate quando arrivano più navi.
- Modalità «Facile» per anziani e persone fragili, con lettura ad alta voce.
- «Il mio appuntamento all'ufficio»: arrivo garantito o richiesta di rinvio.
- Più lingue per gli avvisi del caso B, con frasi fisse ricontrollate.
- Botteghe vicine durante l'attesa, **spente automaticamente durante un'allerta**.

## Cosa togliamo dalla demo e perché

- **Storia di Napoli e itinerario del turista (U4, B6, U3).** Non sono idee sbagliate: escono dalla *demo* perché in 3 minuti la giuria deve capire una sola storia, cioè agenti che si coordinano in un'emergenza e un beneficio misurabile. Un itinerario turistico apre un secondo racconto che compete con il primo, costa circa 1,5 ore (B6 + U3) proprio mentre manca ancora il percorso demo, e mostrare un itinerario di visita mentre l'avviso sismico è attivo stona con il tono. Il piano li mette già in fondo alla lista dei tagli. Il turista resta presente dove conta: avvisi in inglese, cornice dell'allerta ufficiale e, nel pitch, il «rientro al porto garantito». Se domenica mattina il percorso demo è stabile, B6 si recupera.
- **Il quantistico nel video.** Resta in PROGETTO.md come sviluppo futuro, ma esce dal video: oggi non migliora nessun indicatore, e in 3 minuti la giuria lo leggerebbe come una moda, togliendo credibilità al resto. Se un giurato chiede del futuro, la risposta è pronta (ottimizzazione QUBO e firme post-quantum per il registro).
