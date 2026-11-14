"""Partita vera di riferimento per lo scenario: la «prova generale» della prossima partita al Maradona.

Lo scenario simulato (sciame, chiusure, folla) si prova sulla prossima partita vera in casa del
Napoli, letta da football-data.org con le regole di quella fonte (copia salvata se non risponde,
nessuna partita inventata). Si sceglie la prima partita non ancora finita: una partita iniziata da
meno di DURATA_H ore conta ancora.
"""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from .fonti.partite_football import fonte
from .models import Partita, Partite

DURATA_H = 3


def scegli(partite: Partite, adesso: datetime) -> Partita | None:
    soglia = adesso - timedelta(hours=DURATA_H)
    for p in sorted(partite.partite, key=lambda p: p.data_ora):
        if p.stato != "FINISHED" and datetime.fromisoformat(p.data_ora) >= soglia:
            return p
    return None


def partita_reale(adesso: Callable[[], datetime] = lambda: datetime.now(UTC)) -> Partita | None:
    return scegli(fonte().leggi(), adesso())
