# Messa online su Google Cloud Run

Un comando: **`make deploy`**. Lo script (`deploy/deploy.sh`) si rilancia uguale per ogni aggiornamento.

## Cosa serve, una volta per PC

1. **Google Cloud CLI.** Linux, senza sudo:
   ```sh
   curl -sSLO https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz
   tar -xzf google-cloud-cli-linux-x86_64.tar.gz -C ~ && ~/google-cloud-sdk/install.sh --quiet
   ```
   macOS e Windows: [guida ufficiale](https://cloud.google.com/sdk/docs/install). Lo script trova `gcloud` anche in `~/google-cloud-sdk/bin` se non è nel PATH.
2. **Accesso e progetto** (lo stesso progetto delle chiavi Maps, con fatturazione attiva):
   ```sh
   gcloud auth login
   gcloud config set project <ID_PROGETTO>
   ```
3. **`.env`** nella cartella del progetto, ricevuto in privato.

## Cosa fa `make deploy`

1. Abilita le API: Cloud Run, Cloud Build, Artifact Registry, Secret Manager, API Keys, Firebase e Firebase Hosting.
2. Crea l'account di servizio `naples-run`, che può solo leggere i propri segreti (non l'account predefinito, che ha permessi da Editor su tutto il progetto).
3. Copia `MAPS_API_KEY`, `LLM_API_KEY` e `FOOTBALL_DATA_API_KEY` da `.env` in **Secret Manager**, con una versione nuova solo se il valore è cambiato. Nessuna chiave finisce nell'immagine o nelle variabili in chiaro. `MAPS_JS_API_KEY` resta una variabile: è pubblica per natura e limitata ai siti autorizzati.
4. Costruisce l'immagine con **Cloud Build** (non serve Docker sul PC). `.gcloudignore` esclude `.env` dal caricamento.
5. Pubblica il servizio `naples` a **Milano** (`europe-west8`), pubblico, con:
   - `--max-instances 1`: la sessione della demo e il canale in tempo reale stanno nella memoria di un solo processo;
   - `--min-instances 0`: senza visite si spegne e non costa; la prima apertura dopo una pausa impiega qualche secondo;
   - `--timeout 3600`: il canale in tempo reale verso i telefoni resta aperto fino a un'ora (il predefinito è 5 minuti).
6. Pubblica l'indirizzo leggibile **https://naples-coscienze.web.app** su Firebase Hosting (gratuito, stesso progetto): un sito senza file propri che inoltra ogni richiesta al servizio Cloud Run. Nome del sito con `SITO=<nome>`.
7. Aggiunge ai siti autorizzati della chiave Maps del browser gli indirizzi locali, i due di Cloud Run e i due di Firebase, conservando gli altri e le restrizioni sulle API.
8. Stampa gli indirizzi di control room e vista cittadino.

**Canale in tempo reale.** Firebase Hosting trattiene le risposte in streaming fino alla fine, quindi il canale `/api/events` non può passare da lì. Il servizio riceve `EVENTS_URL` (l'indirizzo diretto di Cloud Run, prevedibile dal numero di progetto) e `CORS_ORIGINS` (gli indirizzi Firebase): la web app legge `events_url` da `/api/config` e apre il canale direttamente su Cloud Run. Tutte le altre richieste passano da web.app. In locale `events_url` è vuoto e il canale resta sulla stessa origine.

## Il container

`Dockerfile`: compila la PWA con Node, poi un'immagine Python con agenti e gateway, eseguita da un utente senza privilegi. `deploy/start.sh` avvia gli agenti su 127.0.0.1:8001, aspetta che rispondano, poi il gateway sulla porta di Cloud Run. Se uno dei due processi si ferma il container esce e Cloud Run lo riavvia.

## Costi

Con l'uso di una demo si resta nelle quote gratuite: Cloud Run (2 milioni di richieste al mese), Cloud Build (120 minuti di build al giorno), Artifact Registry (0,5 GB), Secret Manager (6 versioni attive). Le chiamate a Google Maps e al modello si pagano come in locale; la cache dei testi del modello è nell'immagine.

## Variabili facoltative

`GCP_PROJECT=<id> GCP_REGION=<regione> SERVIZIO=<nome> SITO=<nome> make deploy` per usare un altro progetto, regione o nome del servizio.

## Se qualcosa va storto

- **Build negata per permessi:** nei progetti nuovi Cloud Build usa l'account di servizio predefinito di Compute Engine; dagli il ruolo «Cloud Build Service Account» o segui il messaggio di `gcloud`.
- **Mappa grigia online:** la chiave del browser non autorizza ancora l'indirizzo; lo script lo aggiunge, ma serve qualche minuto.
- **Log:** `gcloud run services logs read naples --region europe-west8`.
