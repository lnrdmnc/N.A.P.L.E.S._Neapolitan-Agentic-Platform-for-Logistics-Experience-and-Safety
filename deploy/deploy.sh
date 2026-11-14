#!/bin/bash
# Messa online su Google Cloud Run in un solo comando: `make deploy` (guida in docs/DEPLOY.md).
# Idempotente: si rilancia uguale per ogni aggiornamento.
#
# Fa, nell'ordine: abilita le API, crea un account di servizio dedicato, copia le chiavi di .env
# in Secret Manager (solo se cambiate), costruisce l'immagine con Cloud Build, pubblica il servizio
# pubblica l'indirizzo leggibile su Firebase Hosting (https://<SITO>.web.app, che inoltra a Cloud Run)
# e aggiunge gli indirizzi ai siti autorizzati della chiave Maps del browser.
#
# Variabili: GCP_PROJECT (predefinito: progetto di `gcloud config`), GCP_REGION (europe-west8, Milano),
# SERVIZIO (naples), SITO (naples-coscienze: l'indirizzo sarà https://naples-coscienze.web.app).
set -euo pipefail
cd "$(dirname "$0")/.."

GCLOUD=${GCLOUD:-$(command -v gcloud || echo "$HOME/google-cloud-sdk/bin/gcloud")}
[ -x "$GCLOUD" ] || { echo "deploy: gcloud non trovato (docs/DEPLOY.md, passo 1)"; exit 1; }
[ -f .env ] || { echo "deploy: manca .env con le chiavi"; exit 1; }
set -a; . ./.env; set +a

PROGETTO=${GCP_PROJECT:-$("$GCLOUD" config get-value project 2>/dev/null)}
REGIONE=${GCP_REGION:-europe-west8}
SERVIZIO=${SERVIZIO:-naples}
SITO=${SITO:-naples-coscienze}
SA="naples-run@${PROGETTO}.iam.gserviceaccount.com"
[ -n "$PROGETTO" ] || { echo "deploy: nessun progetto: gcloud config set project <ID>"; exit 1; }
"$GCLOUD" auth list --filter=status:ACTIVE --format="value(account)" | grep -q . \
  || { echo "deploy: prima esegui gcloud auth login"; exit 1; }
g() { "$GCLOUD" --project "$PROGETTO" --quiet "$@"; }

echo "→ Progetto $PROGETTO, regione $REGIONE, servizio $SERVIZIO"

echo "→ API"
g services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com apikeys.googleapis.com firebase.googleapis.com firebasehosting.googleapis.com

echo "→ Account di servizio dedicato (legge solo i propri segreti)"
g iam service-accounts describe "$SA" >/dev/null 2>&1 \
  || g iam service-accounts create naples-run --display-name "N.A.P.L.E.S. Cloud Run"

echo "→ Chiavi in Secret Manager"
SEGRETI=()
for VAR in MAPS_API_KEY LLM_API_KEY FOOTBALL_DATA_API_KEY; do
  VALORE=${!VAR:-}
  [ -n "$VALORE" ] || { echo "   $VAR vuota in .env: salto"; continue; }
  NOME="naples-$(echo "$VAR" | tr '[:upper:]_' '[:lower:]-')"
  if ! g secrets describe "$NOME" >/dev/null 2>&1; then
    g secrets create "$NOME" --replication-policy=automatic >/dev/null
  fi
  ATTUALE=$(g secrets versions access latest --secret "$NOME" 2>/dev/null || true)
  if [ "$ATTUALE" != "$VALORE" ]; then
    printf '%s' "$VALORE" | g secrets versions add "$NOME" --data-file=- >/dev/null
    echo "   $VAR: nuova versione"
  else
    echo "   $VAR: invariata"
  fi
  g secrets add-iam-policy-binding "$NOME" --member "serviceAccount:$SA" \
    --role roles/secretmanager.secretAccessor >/dev/null
  SEGRETI+=("$VAR=$NOME:latest")
done

# Firebase Hosting trattiene le risposte in streaming: il canale in tempo reale va diretto a Cloud Run,
# che accetta le pagine servite da web.app (CORS_ORIGINS). L'indirizzo diretto è prevedibile.
NUMERO=$(g projects describe "$PROGETTO" --format 'value(projectNumber)')
DIRETTO="https://${SERVIZIO}-${NUMERO}.${REGIONE}.run.app"
PUBBLICI="https://${SITO}.web.app,https://${SITO}.firebaseapp.com"

echo "→ Build (Cloud Build) e pubblicazione: qualche minuto"
# max-instances 1: sessione demo e canale in tempo reale stanno nella memoria di un solo processo.
# timeout 3600: il canale in tempo reale verso i telefoni resta aperto fino a un'ora.
g run deploy "$SERVIZIO" --source . --region "$REGIONE" \
  --service-account "$SA" --allow-unauthenticated \
  --min-instances 0 --max-instances 1 --timeout 3600 --memory 1Gi --cpu 1 \
  --set-env-vars "^;^MAPS_JS_API_KEY=${MAPS_JS_API_KEY:-};LLM_PROVIDER=${LLM_PROVIDER:-};LLM_MODEL=${LLM_MODEL:-};EVENTS_URL=$DIRETTO/api/events;CORS_ORIGINS=$PUBBLICI" \
  ${SEGRETI:+--set-secrets "$(IFS=,; echo "${SEGRETI[*]}")"}

URL=$(g run services describe "$SERVIZIO" --region "$REGIONE" --format 'value(status.url)')

echo "→ Indirizzo leggibile su Firebase Hosting"
TOKEN=$("$GCLOUD" auth print-access-token)
api() { curl -sS -X "$1" -H "Authorization: Bearer $TOKEN" -H "x-goog-user-project: $PROGETTO" \
  -H "Content-Type: application/json" "$2" ${3:+-d "$3"}; }
FB=https://firebasehosting.googleapis.com/v1beta1
if ! api GET "https://firebase.googleapis.com/v1beta1/projects/$PROGETTO" | grep -q '"projectId"'; then
  api POST "https://firebase.googleapis.com/v1beta1/projects/$PROGETTO:addFirebase" '{}' >/dev/null
  sleep 20
fi
if ! api GET "$FB/projects/$PROGETTO/sites/$SITO" | grep -q '"defaultUrl"'; then
  api POST "$FB/projects/$PROGETTO/sites?siteId=$SITO" '{}' | grep -q '"defaultUrl"' \
    || { echo "   sito $SITO non creato (nome già usato da altri? prova SITO=altro-nome)"; exit 1; }
fi
REGOLA="{\"glob\":\"**\",\"run\":{\"serviceId\":\"$SERVIZIO\",\"region\":\"$REGIONE\"}}"
if api GET "$FB/sites/$SITO/releases?pageSize=1" | tr -d ' \n' | grep -qF "\"rewrites\":[$REGOLA]"; then
  echo "   https://$SITO.web.app già collegato a $SERVIZIO"
else
  VERSIONE=$(api POST "$FB/sites/$SITO/versions" "{\"config\":{\"rewrites\":[$REGOLA]}}" \
    | python3 -c 'import json,sys; print(json.load(sys.stdin)["name"])')
  api PATCH "$FB/$VERSIONE?update_mask=status" '{"status":"FINALIZED"}' >/dev/null
  api POST "$FB/sites/$SITO/releases?versionName=$VERSIONE" '{}' >/dev/null
  echo "   https://$SITO.web.app → $SERVIZIO"
fi

# Siti autorizzati della chiave Maps del browser: quelli già presenti, più lo sviluppo in locale,
# più ogni indirizzo del servizio (Cloud Run ne dà due). Le restrizioni sulle API restano.
LOCALI=(http://localhost:5173/* http://127.0.0.1:5173/* http://localhost:8000/* http://127.0.0.1:8000/*)
if [ -n "${MAPS_JS_API_KEY:-}" ]; then
  echo "→ Siti autorizzati sulla chiave Maps del browser"
  CHIAVE=$(g services api-keys lookup "$MAPS_JS_API_KEY" --format 'value(name)' 2>/dev/null || true)
  if [ -z "$CHIAVE" ]; then
    echo "   chiave non trovata in questo progetto: aggiungi a mano $URL/* nei siti autorizzati"
  else
    ATTUALI=$(g services api-keys describe "$CHIAVE" \
      --format 'value(restrictions.browserKeyRestrictions.allowedReferrers.list(separator=","))')
    INDIRIZZI=$(g run services describe "$SERVIZIO" --region "$REGIONE" \
      --format 'value(metadata.annotations."run.googleapis.com/urls")' | tr -d '[]" ' | tr ',' '\n')
    VOLUTI=$( { tr ',' '\n' <<<"$ATTUALI"; printf '%s\n' "${LOCALI[@]}"; sed 's|$|/*|' <<<"$INDIRIZZI"; echo "$URL/*"; tr ',' '\n' <<<"$PUBBLICI" | sed 's|$|/*|'; } \
      | grep . | sort -u | paste -sd, -)
    if [ "$(tr ',' '\n' <<<"$ATTUALI" | grep . | sort -u | paste -sd, -)" == "$VOLUTI" ]; then
      echo "   già a posto"
    else
      ARGOMENTI=(--allowed-referrers "$VOLUTI")
      while read -r SERVIZIO_API; do
        [ -n "$SERVIZIO_API" ] && ARGOMENTI+=(--api-target "service=$SERVIZIO_API")
      done < <(g services api-keys describe "$CHIAVE" --format 'value(restrictions.apiTargets[].service)' | tr ';' '\n')
      g services api-keys update "$CHIAVE" "${ARGOMENTI[@]}" >/dev/null 2>&1
      echo "   aggiornati: $VOLUTI (attivi entro qualche minuto)"
    fi
  fi
fi

echo
echo "Online: https://$SITO.web.app"
echo "  Control room: https://$SITO.web.app/control-room"
echo "  Cittadino:    https://$SITO.web.app/cittadino"
echo "  Diretto (Cloud Run): $URL"
