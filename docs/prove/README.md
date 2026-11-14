# Prove dello scenario

`make prova` esegue lo scenario tre volte, con tre comportamenti dell'operatore, e scrive qui un rapporto per ognuna:

| File | L'operatore… |
| --- | --- |
| `prova-subito.md` | approva ogni piano appena proposto |
| `prova-tardi.md` | approva un piano solo dopo 10 minuti di attesa |
| `prova-mai.md` | non approva nulla |

Ogni rapporto contiene controlli automatici (niente evacuazioni, notizie non verificate mai diffuse, allerte ufficiali identiche, nessun avviso ripetuto, registro integro), una sintesi con gli indicatori, la linea del tempo dei messaggi tra agenti, i piani con l'impatto stimato e gli avvisi per profilo.

I rapporti sono generati: non si committano (sono esclusi da git) e non si modificano a mano. Ognuno li rigenera con `make prova` in circa un secondo, senza rete. Se un controllo automatico fallisce, `make prova` termina con errore.

**Come leggerli (docs/PIANO.md, P1):** cercare decisioni assurde, messaggi ripetuti o che non aggiungono nulla, testi vaghi o allarmisti, avvisi senza fonte. Quello che si trova va in docs/FEEDBACK.md.

La prova «subito» scrive anche il registro delle decisioni in `agents/var/registro.jsonl`: si verifica con `make verifica-registro`.
