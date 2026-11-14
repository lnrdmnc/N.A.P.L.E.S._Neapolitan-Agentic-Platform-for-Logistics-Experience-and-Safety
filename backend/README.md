# backend

Gateway FastAPI della web app N.A.P.L.E.S., porta 8000, senza logica di dominio: la logica sta negli agenti (`agents/`, porta 8001).

- `GET /api/health`: stato del gateway.
- `GET /api/events`: canale in tempo reale (Server-Sent Events) verso control room e vista cittadino.
- `GET /api/config`: la chiave del browser per Google Maps (`MAPS_JS_API_KEY`), pubblica per natura e limitata ai domini nella console Google. La chiave di Routes resta negli agenti.
- Ogni altro `/api/*` va agli agenti (`AGENTS_URL`, predefinito `http://127.0.0.1:8001`); contratto in `contracts/agenti.openapi.json`. Se gli agenti sono spenti risponde 503.
- `POST /api/piano/{id}/approva` riuscito: gli avvisi restituiti partono anche sul canale in tempo reale, evento `avvisi`.
- Serve la PWA compilata (`frontend/dist`), qualunque altro percorso torna a `index.html`.
- Una rotta nuova sta in un file proprio in `app/routes/` e si registra con una riga in `app/routes/index.py`, prima di `agents_proxy`.
- Avvio: `make backend`. Test: `make test-backend` (gli agenti sono simulati con un trasporto finto).
