# Contratti

I moduli comunicano solo attraverso questi file. Chi cambia un contratto lo fa con un commit dedicato e avvisa in `docs/STATO.md`.

| File | Tra chi | Come si aggiorna |
| --- | --- | --- |
| `agenti.openapi.json` | agenti (Python, porta **8001**) → web app | Generato da `agents/src/napoles_agents/models/` e `api/` con `make contracts`; `make check` fallisce se non è allineato. |

## Oggetti (dettaglio nello schema)

- **StatoCitta** — fotografia al minuto `t_min`: eventi avvenuti, linee attive o sospese, livello vulcanico.
- **Messaggio** — linea del tempo tra agenti: `seq`, `da`, `a`, `tipo` (evento, proposta, conflitto, piano, decisione, avviso), `titolo`, `testo`, `affidabilita`, `simulato`, `rif`. `GET /api/messaggi?da_seq=N` restituisce solo quelli dopo N.
- **Proposta** — cosa propone un agente: azione, risorse, priorità (5 = sicurezza), `affidabilita` (ufficiale, misurata, stimata, non_verificata), `caso` di gestione alert (A, B, C).
- **Piano** — piano unico dell'Orchestratore: proposte in ordine di priorità, conflitti risolti, sintesi, `affidabilita_minima`, `impatto` (vuoto finché non c'è B1), `stato` (proposto, modificato, approvato, rifiutato, superato).
- **Alert** — avviso in formato CAP semplificato: `msgType` (Alert, Update, Cancel), `severity`, `urgency`, `certainty`, `area`, `source`, `ufficiale`, `simulato`, `pubblico`, `lingua`, `piano_id`.
- **Ricezione** — conferme di lettura di un avviso (stub fino a B3).
- **ConfrontoIndicatori** — stessi indicatori con e senza coordinamento, con `origine` di ogni numero (calcolato, misurato_in_sessione, ipotesi) e le ipotesi usate.
- **SerieSimulazione** — passi da 5 minuti con lo stato di ogni zona, per la mappa (stub fino a S0 e B1).
- **Contesto** — dati reali: livelli vulcanici con fonte e data, eventi INGV, meteo; sempre `simulato: false` (stub fino a F1 e F2).
- **Itinerario** — tratte del turista con percorribilità e alternativa (stub fino a B6).
- **StatoRegistro** — voci del registro a catena di hash e verifica di integrità.

Gli oggetti con `stub: true` hanno già la forma definitiva ma dati finti: la web app può costruirci sopra.

Per la web app: in UI vanno sempre mostrati `simulato`, `affidabilita` o `certainty`, `source` e, per gli indicatori, `origine`.
