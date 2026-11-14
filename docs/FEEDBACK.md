# Feedback: checkpoint con i mentor e prove a mano

Prevale sulle ipotesi (CLAUDE.md). Una sezione per checkpoint o prova, la più recente in fondo.

## Checkpoint 1 con i mentor — sabato 14/11, ore 14:50

**Osservazioni dei mentor (riportate da Leonardo Monaco alle 18:45):** puntare su **affidabilità** (*trustability*) e **tempo reale** (*real time*).
*Da completare da chi era presente: nomi dei mentor, domande ricevute, frasi esatte.*

**Affidabilità: cosa c'è nel prodotto (verificato sul codice il 14/11 alle 18:45)**

- Ogni evento e ogni proposta dichiara l'affidabilità (ufficiale, misurata, stimata, non verificata), sempre visibile in control room.
- Ogni numero degli indicatori dichiara l'origine (calcolato, ipotesi, misurato in sessione); le ipotesi sono in docs/IPOTESI.md con la sensibilità.
- Allerte ufficiali inoltrate con il testo identico (caso A); notizie non verificate fermate in control room, mai diffuse (caso C); nessuna istruzione di evacuazione.
- L'operatore approva, modifica o rifiuta ogni piano; le allerte ufficiali non si possono escludere.
- Registro delle decisioni a catena di hash, verificabile in control room e con `make verifica-registro`.
- `make prova`: tre esecuzioni con controlli automatici; testi scritti da Claude con controlli e ripiego sul testo a regole (B5).
- Ogni dato simulato è etichettato come tale, in control room e sul telefono.

**Tempo reale: cosa c'è**

- Canale in diretta dal backend ai telefoni (`/api/events`): l'avviso approvato arriva subito; le schermate si aggiornano ogni 1–2 secondi.
- Traffico reale da Google (tempi con traffico, con chiave); partite reali al Maradona da football-data.org.
- Conferme di lettura dei telefoni contate dal vivo in control room.

**Tempo reale: cosa manca (al 14/11 alle 18:45)**

1. ~~Nessuna schermata fa avanzare il tempo dello scenario~~ **Risolto sab 18:51**: regia in control room con orologio che avanza da solo, pausa automatica quando arriva un piano, velocità, salto al prossimo evento, ricomincia.
2. **Contesto reale non collegato**: eventi INGV reali e meteo reale (compiti F1, F2) sono ancora uno stub, eppure le fonti rispondono (INGV ha registrato Md 2.6 ai Campi Flegrei il 13/11).
3. Zone del simulatore sulla mappa (C1) non ancora disegnate.

## Checkpoint 2 con i mentor

*Da fare: obbligatorio per la validità del progetto.*
