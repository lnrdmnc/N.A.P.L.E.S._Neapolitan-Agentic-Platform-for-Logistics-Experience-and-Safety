"""La sessione demo condivisa da tutti i router.

Il registro delle decisioni viene scritto su file (`agents/var/registro.jsonl`, oppure il percorso
in `NAPOLES_REGISTRO`; stringa vuota = nessun file). Si verifica con `make verifica-registro`.
"""

import os
from pathlib import Path

from ..motore import Sessione
from ..registro import FILE_PREDEFINITO


def _file() -> Path | None:
    valore = os.environ.get("NAPOLES_REGISTRO")
    if valore is None:
        return FILE_PREDEFINITO
    return Path(valore) if valore else None


_sessione = Sessione(file_registro=_file())


def sessione() -> Sessione:
    return _sessione


def nuova() -> Sessione:
    global _sessione
    _sessione = Sessione(file_registro=_file())
    return _sessione
