"""Strumento di prova del team (compito P1). Uso: `make prova`.

STUB: oggi esegue il percorso demo approvando ogni piano e stampa i messaggi del bus.
P1 lo completa salvando messaggi, piano e indicatori in docs/prove/.
"""

from .motore import Sessione
from .simulazione import confronta, sensibilita


def main() -> None:
    s = Sessione()
    for t in range(s.scenario["durata_min"] + 1):
        s.avanza(t)
        p = s.piano_corrente
        if p and p.stato == "proposto":
            s.approva(p.id, operatore="prova")
    for m in s.bus.messaggi:
        print(f"{m.seq:3d} {m.ora} [{m.tipo:9s}] {m.da} → {m.a}: {m.titolo}")
    integro, _ = s.registro.verifica()
    c = confronta(s.scenario)
    print(f"\nRegistro integro: {integro}; voci: {len(s.registro.voci)}; avvisi: {len(s.avvisi)}")
    for i in (c.con_coordinamento, c.senza_coordinamento):
        print(f"{i.scenario}: deflusso {i.deflusso_min} min, picco {i.picco_attesa_persone} persone")
    print("\nSensibilità (fattore percorsi a piedi, decisione senza coordinamento):")
    for r in sensibilita(s.scenario):
        print(
            f"  fattore {r['fattore_percorsi_piedi']}, decisione {r['decisione_senza_min']} min: "
            f"deflusso {r['deflusso_con']} → {r['deflusso_senza']} min, "
            f"picco {r['picco_con']} → {r['picco_senza']}"
        )


if __name__ == "__main__":
    main()
