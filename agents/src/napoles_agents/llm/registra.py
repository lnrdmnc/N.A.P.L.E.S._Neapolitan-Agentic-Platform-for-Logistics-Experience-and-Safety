"""Prepara la cache dei testi del modello (compito K1). Uso: `make llm-cache` (serve LLM_API_KEY).

Esegue lo scenario approvando ogni piano, come `make prova`: ogni testo del percorso demo viene
scritto una volta e salvato in data/llm_cache/. Da rileggere prima del commit.
"""

import time

from .. import llm
from ..motore import Sessione


def main() -> None:
    servizio = llm.servizio()
    if not servizio.attivo:
        raise SystemExit("llm-cache: manca LLM_API_KEY in .env, nessun testo da registrare")
    prima = servizio.cache.voci()
    inizio = time.monotonic()
    s = Sessione()
    for t in range(s.scenario["durata_min"] + 1):
        s.avanza(t)
        p = s.piano_corrente
        if p and p.stato == "proposto":
            s.approva(p.id, operatore="registrazione")
    con_testo = [a for a in s.avvisi if a.messaggio_modello]
    print(f"Piani: {len(s.piani)}, con sintesi del modello: {sum(1 for p in s.piani if p.sintesi_modello)}")
    print(f"Avvisi: {len(s.avvisi)}, con messaggio del modello: {len(con_testo)}")
    print(f"Voci in cache: {prima} → {servizio.cache.voci()}, in {time.monotonic() - inizio:.0f} s")
    if servizio.ultima and servizio.ultima.esito in ("errore", "scartato"):
        print(f"Ultimo problema: {servizio.ultima.esito} – {servizio.ultima.dettaglio}")


if __name__ == "__main__":
    main()
