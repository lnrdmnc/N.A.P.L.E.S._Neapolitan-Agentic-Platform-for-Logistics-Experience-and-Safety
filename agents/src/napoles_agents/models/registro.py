"""Registro delle decisioni a catena di hash."""

from typing import Any

from pydantic import BaseModel


class VoceRegistro(BaseModel):
    indice: int
    t_min: int
    tipo: str
    contenuto: dict[str, Any]
    hash_precedente: str
    hash: str


class StatoRegistro(BaseModel):
    integro: bool
    prima_voce_alterata: int | None
    voci: list[VoceRegistro]
