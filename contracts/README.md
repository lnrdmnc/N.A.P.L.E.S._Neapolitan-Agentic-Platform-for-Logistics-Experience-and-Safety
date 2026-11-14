# Contratti

I moduli comunicano solo attraverso questi file. Chi cambia un contratto lo fa con un commit dedicato e avvisa in `docs/STATO.md`.

| File | Tra chi | Come si aggiorna |
| --- | --- | --- |
| `agenti.openapi.json` | agenti (Python) → web app | Generato dai modelli in `agents/src/napoles_agents/models.py` e `api.py` con `make contracts`; `make check` fallisce se non è allineato. |

## Oggetti principali (dettaglio nello schema)

- **StatoCitta** — fotografia al minuto `t_min`: eventi avvenuti, linee attive o sospese, livello vulcanico.
- **Proposta** — cosa propone un agente: azione, risorse usate, priorità (5 = sicurezza), `affidabilita` (ufficiale, misurata, stimata, non_verificata), `caso` di gestione alert (A, B, C).
- **Piano** — piano unico dell'Orchestratore: proposte in ordine di priorità, conflitti risolti, sintesi, `stato` (proposto, approvato, rifiutato, superato).
- **Alert** — avviso in formato CAP semplificato: `msgType` (Alert, Update, Cancel), `severity`, `urgency`, `certainty`, `area`, `source`, `ufficiale`, `simulato`, `pubblico`, `lingua`.
- **ConfrontoIndicatori** — stessi indicatori con e senza coordinamento, più le ipotesi usate.
- **VoceRegistro** — voce del registro delle decisioni a catena di hash; `GET /api/registro` dice anche se la catena è integra.

Per la web app: in UI vanno sempre mostrati `simulato`, `affidabilita` o `certainty`, e `source`.
