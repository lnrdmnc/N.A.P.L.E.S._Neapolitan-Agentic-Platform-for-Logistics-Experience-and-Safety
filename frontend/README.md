# frontend

Web app PWA di N.A.P.L.E.S. (Vite + React + TypeScript), installabile e funzionante offline.

- `/control-room` (`src/control-room/`): dashboard per il proiettore. Oggi: ora della simulazione, stato della città, linee, eventi con affidabilità. Mappa con traffico reale di Google e tempi dallo stadio (`MappaTraffico.tsx`, etichetta «DATO REALE»). Linea del tempo dei messaggi tra agenti (`MessaggiAgenti.tsx`, C2); indicatori con e senza coordinamento con l'origine di ogni numero (`Indicatori.tsx`, C5); registro delle decisioni con verifica della catena (`Registro.tsx`, C4). Riquadri in costruzione: mappa a zone (C1), piano (C3).
- `/cittadino` (`src/cittadino/`): emergenze e avvisi (`AlertCard.tsx`: caso A o B, certezza, fonte, indicazioni operative), traffico e trasporti, partite al Maradona (`PartiteMaradona.tsx`, dato reale da `/api/partite`), meteo (U2). Scelta del profilo (`SceltaProfilo.tsx`) e avvisi del proprio profilo e lingua, con conferma di lettura anonima (`api/useAvvisiProfilo.ts`): U1.
- `/` (`src/home/`): scelta tra le due viste. Una pagina nuova si registra con una riga in `src/routes.ts`.
- Dati: `src/api/useStato.ts` legge `/api/stato` ogni secondo; `src/api/useLiveEvents.ts` riceve gli eventi da `/api/events`.
- Tipi: `npm run contract` genera `src/api/contratto.ts` da `contracts/agenti.openapi.json` (non si committa; parte da solo prima di dev, lint e build).
- Stile: token ispirati a IBM Carbon in `src/styles/tokens.css`, font IBM Plex in locale. Ogni dato simulato porta l'etichetta viola, ogni dato stimato o non verificato quella gialla.
- Entrambe le viste funzionano da telefono, tablet e computer: punti di rottura a 640 e 1056 px per la control room, 768 e 1200 px per la vista cittadino.
- Sviluppo: `make agents-run`, `make backend`, `make frontend`, poi http://localhost:5173; dal telefono sulla stessa Wi-Fi, `http://<IP del PC>:5173`. Build: `make build`.
