# scripts

Comandi di servizio del progetto, solo libreria standard di Python.

- `demo.py` — `make demo` (compito X1): compila la PWA, avvia gli agenti sulla 8001 e il gateway
  sulla 8000, riporta lo scenario al minuto 0 e stampa gli indirizzi da aprire.
  Legge `.env` se c'è e dice quali chiavi sono configurate, senza mostrarne i valori.
  Opzioni: `--apri` apre la control room, `--senza-build` usa `frontend/dist` già compilato.

Si esegue con il Python di `backend/.venv` (lo fa il Makefile). Non importa codice di altri moduli:
parla con agenti e gateway solo via HTTP.
