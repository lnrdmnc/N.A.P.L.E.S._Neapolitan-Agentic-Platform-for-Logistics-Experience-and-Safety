# Messa online su Google Cloud Run

Un solo container (`Dockerfile`): agenti su 127.0.0.1:8001, interni; gateway con la PWA compilata sulla porta che assegna Cloud Run. Avvio in `deploy/start.sh`.

## Chiavi

Le chiavi stanno in `.env`, che non si committa: si passa ai PC del team solo in privato. Su Cloud Run si passano come variabili d'ambiente al momento del deploy, mai nell'immagine (`.dockerignore` esclude `.env`).

| Variabile | API | Restrizioni nella console Google |
| --- | --- | --- |
| `MAPS_API_KEY` | Routes API | Solo Routes API; nessuna restrizione di IP (Cloud Run esce da indirizzi variabili) |
| `MAPS_JS_API_KEY` | Maps JavaScript API | Solo Maps JavaScript API; siti web `http://localhost:5173/*`, `http://localhost:8000/*`, `http://127.0.0.1:8000/*` e l'indirizzo `https://…run.app/*` dopo il primo deploy |

Quote gratuite al mese: 5.000 richieste Compute Routes Pro, 10.000 caricamenti Dynamic Maps. Il codice limita Routes a 150 chiamate al giorno; consigliati anche un budget con avviso in Fatturazione e un tetto giornaliero nelle quote di Routes API.

## Primo deploy

Serve [gcloud](https://cloud.google.com/sdk/docs/install) e un progetto con fatturazione, con abilitate Cloud Run Admin API, Cloud Build API e Artifact Registry API.

```sh
gcloud auth login
gcloud config set project <ID_PROGETTO>
set -a; . ./.env; set +a
gcloud run deploy naples --source . --region europe-west1 \
  --allow-unauthenticated --max-instances 1 --min-instances 0 \
  --set-env-vars "MAPS_API_KEY=$MAPS_API_KEY,MAPS_JS_API_KEY=$MAPS_JS_API_KEY"
```

`--max-instances 1` è necessario: la sessione della demo e il canale in tempo reale stanno nella memoria di un solo processo. Con `--min-instances 0` il servizio si spegne quando nessuno lo usa e non costa; la prima apertura dopo una pausa impiega qualche secondo.

Alla fine il comando stampa l'indirizzo `https://naples-….run.app`: va aggiunto alle restrizioni della chiave del browser. Viste: `/control-room` e `/cittadino`.

## Aggiornare

Dopo un pull di main, lo stesso comando `gcloud run deploy` dalla cartella del progetto.
