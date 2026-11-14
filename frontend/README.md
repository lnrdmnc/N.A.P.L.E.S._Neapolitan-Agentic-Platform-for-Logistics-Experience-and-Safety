# frontend

Web app PWA di N.A.P.L.E.S. (Vite + React + TypeScript), installabile e funzionante offline.

- `/control-room` (`src/control-room/`): dashboard per il proiettore. Oggi: ora della simulazione, stato della città, linee, eventi con affidabilità, canale in tempo reale. Da fare: mappa (C1), piano (C3), indicatori (C5).
- `/cittadino` (`src/cittadino/`): vista mobile con linee e avvisi approvati in diretta. Filtro per profilo e lingua: U1.
- `/` (`src/home/`): scelta tra le due viste. Una pagina nuova si registra con una riga in `src/routes.ts`.
- Dati: `src/api/useStato.ts` legge `/api/stato` ogni secondo; `src/api/useLiveEvents.ts` riceve gli eventi da `/api/events`.
- Tipi: `npm run contract` genera `src/api/contratto.ts` da `contracts/agenti.openapi.json` (non si committa; parte da solo prima di dev, lint e build).
- Stile: token ispirati a IBM Carbon in `src/styles/tokens.css`, font IBM Plex in locale. Ogni dato simulato porta l'etichetta viola, ogni dato stimato o non verificato quella gialla.
- Sviluppo: `make agents-run`, `make backend`, `make frontend`, poi http://localhost:5173. Build: `make build`.
