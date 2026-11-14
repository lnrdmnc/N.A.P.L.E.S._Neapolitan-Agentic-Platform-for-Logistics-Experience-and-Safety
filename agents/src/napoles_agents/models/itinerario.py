"""Itinerario del turista verificato rispetto alle linee sospese (compito B6)."""

from pydantic import BaseModel, Field


class Tratta(BaseModel):
    da: str
    a: str
    mezzo: str
    minuti: int
    percorribile: bool
    motivo: str | None = Field(default=None, description="Perché non è percorribile: cita il servizio")
    alternativa: str | None = None


class Itinerario(BaseModel):
    tappe: list[str]
    tratte: list[Tratta]
    fonte: str
    verificato_al_t_min: int
    stub: bool = Field(default=False, description="True finché l'itinerario non è calcolato davvero")
