# Stato del progetto

## Scadenze

| Quando          | Cosa                                                          |
| --------------- | ------------------------------------------------------------- |
| sab 14/11 14:30 | piano approvato, contratti e moduli definiti                  |
| sab 14/11 16:30 | simulatore e scenario con Rischio, Mobilità e Orchestratore   |
| sab 14/11 18:30 | control room, lato utente e indicatori a confronto            |
| sab 14/11 20:30 | stop lavori: stato salvato, esecuzione demo registrata        |
| dom 15/11 08:30 | ripresa                                                       |
| dom 15/11 10:30 | stop alle nuove funzionalità                                  |
| dom 15/11 11:30 | pacchetto di consegna pronto                                  |
| dom 15/11 12:00 | consegna                                                      |

## Chi sta lavorando su cosa

| Compito | Chi | Da quando | Nota |
| --- | --- | --- | --- |
| Piano con moduli, contratti e compiti (docs/PIANO.md) | Leonardo Schiavo | sab 14/11 14:30 | Prompt principale: produce il piano, nessun codice |

## Fatto

- Preparazione del repository: CLAUDE.md, .gitignore, .env.example, README.md, docs/STATO.md, docs/IPOTESI.md, docs/STAND.md, docs/FEEDBACK.md, Makefile con `make check`.
- docs/TEAM.md con i componenti del team e regola dei Co-authored-by in CLAUDE.md.
- docs/PROGETTO.md (concept) e docs/GUIDA.md (guida del team) aggiunti.

## Prossimi compiti liberi

- Piano con moduli, contratti e compiti (Prompt principale, `fable` a `max`, plan mode): produce docs/PIANO.md.
- Stand: fare le domande dello sponsor e degli organizzatori e scrivere le risposte in docs/STAND.md.
- Chiave del modello: procurarla e metterla in .env.

## Problemi aperti

- `make check` è minimo (file base e `.env` non tracciato): va esteso con lint e test quando c'è il codice.
- docs/PIANO.md non esiste ancora.
- Punti aperti del concept: nome del team, titolo definitivo, feed GTFS (linee e tempo reale), stack, API meteo e mappe e chi ha la chiave. L'elenco completo è in docs/PROGETTO.md.
