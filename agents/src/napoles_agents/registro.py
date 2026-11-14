"""Registro delle decisioni a catena di hash: ogni voce contiene l'hash della precedente."""

import hashlib
import json
from typing import Any

from .models import VoceRegistro

GENESI = "0" * 64


def _hash(indice: int, t_min: int, tipo: str, contenuto: dict[str, Any], precedente: str) -> str:
    corpo = json.dumps(
        {"indice": indice, "t_min": t_min, "tipo": tipo, "contenuto": contenuto, "prec": precedente},
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(corpo.encode("utf-8")).hexdigest()


class Registro:
    def __init__(self) -> None:
        self.voci: list[VoceRegistro] = []

    def aggiungi(self, t_min: int, tipo: str, contenuto: dict[str, Any]) -> VoceRegistro:
        precedente = self.voci[-1].hash if self.voci else GENESI
        indice = len(self.voci)
        voce = VoceRegistro(
            indice=indice,
            t_min=t_min,
            tipo=tipo,
            contenuto=contenuto,
            hash_precedente=precedente,
            hash=_hash(indice, t_min, tipo, contenuto, precedente),
        )
        self.voci.append(voce)
        return voce

    def verifica(self) -> tuple[bool, int | None]:
        """Ritorna (integro, indice della prima voce alterata)."""
        precedente = GENESI
        for v in self.voci:
            atteso = _hash(v.indice, v.t_min, v.tipo, v.contenuto, precedente)
            if v.hash_precedente != precedente or v.hash != atteso:
                return False, v.indice
            precedente = v.hash
        return True, None
