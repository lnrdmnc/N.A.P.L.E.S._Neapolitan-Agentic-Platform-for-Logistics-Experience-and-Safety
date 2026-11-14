"""Indicatori con e senza coordinamento."""

from typing import Literal

from pydantic import BaseModel, Field

Origine = Literal["calcolato", "misurato_in_sessione", "ipotesi"]


class Indicatori(BaseModel):
    """Stessi indicatori, stesso scenario: con e senza coordinamento."""

    scenario: Literal["con_coordinamento", "senza_coordinamento"]
    deflusso_min: int = Field(description="Minuti dal fischio finale allo sgombero dell'area stadio")
    picco_attesa_persone: int = Field(description="Massimo di persone in attesa fuori dallo stadio")
    minuti_evento_avviso: int
    minuti_decisione: int
    congestione_zone: dict[str, float] = Field(
        default_factory=dict, description="Picco di carico per zona (persone / capienza); compito B4"
    )
    origine: dict[str, Origine] = Field(
        default_factory=dict, description="Da dove viene ogni numero: va mostrato accanto al valore"
    )
    note: list[str] = Field(default_factory=list)


class ConfrontoIndicatori(BaseModel):
    con_coordinamento: Indicatori
    senza_coordinamento: Indicatori
    ipotesi: list[str]
