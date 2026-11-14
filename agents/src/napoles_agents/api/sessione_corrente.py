"""La sessione demo condivisa da tutti i router."""

from ..motore import Sessione

_sessione = Sessione()


def sessione() -> Sessione:
    return _sessione


def nuova() -> Sessione:
    global _sessione
    _sessione = Sessione()
    return _sessione
