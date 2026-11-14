"""Conferma di ricezione degli avvisi (compito B3).

Due numeri diversi, mai mescolati:
- **visti reali**: conferme vere inviate dalla vista cittadino in questa sessione, una per
  telefono (identificativo anonimo casuale, nessun dato personale);
- **consegnati e visti stimati**: quante persone l'avviso raggiungerebbe in produzione, con
  ipotesi dichiarate (persone nell'area per profilo, quota con l'app, ritmo di lettura).

In produzione, con il cell broadcast, la conferma di lettura non esiste: il broadcast è a senso
unico. La conferma esiste solo nell'app (docs/IDEE.md).
"""

import itertools
from collections import Counter
from typing import Any

from .models import Alert, Ricezione


class Ricezioni:
    def __init__(self) -> None:
        self._dispositivi: dict[str, set[str]] = {}
        self._anonime: Counter[str] = Counter()

    def conferma(self, avviso: str, dispositivo: str | None) -> None:
        if dispositivo:
            self._dispositivi.setdefault(avviso, set()).add(dispositivo)
        else:
            self._anonime[avviso] += 1

    def visti(self, avviso: str) -> int:
        return len(self._dispositivi.get(avviso, set())) + self._anonime[avviso]


def _quota_letti(minuti: int, curva: list[list[float]]) -> float:
    """Interpolazione lineare della quota di persone che ha letto l'avviso dopo `minuti`."""
    if minuti <= curva[0][0]:
        return curva[0][1]
    for (m0, q0), (m1, q1) in itertools.pairwise(curva):
        if minuti <= m1:
            return q0 + (q1 - q0) * (minuti - m0) / (m1 - m0)
    return curva[-1][1]


def ricezione(alert: Alert, t_min: int, scenario: dict[str, Any], ricezioni: Ricezioni) -> Ricezione:
    parametri = scenario["ricezione"]
    minuti = max(0, t_min - alert.sent_t_min)
    raggiungibili = parametri["persone_raggiungibili"].get(alert.pubblico, 0)
    consegnati = int(raggiungibili * parametri["quota_con_app"])
    return Ricezione(
        avviso=alert.identifier,
        pubblico=alert.pubblico,
        minuti_dall_invio=minuti,
        visti_reali=ricezioni.visti(alert.identifier),
        visti_stimati=int(consegnati * _quota_letti(minuti, parametri["letti_entro_minuti"])),
        consegnati_stimati=consegnati,
        simulato=True,
    )
