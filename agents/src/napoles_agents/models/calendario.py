"""Napoli oggi e nei prossimi giorni: eventi previsti, zone interessate, percorsi alternativi."""

from typing import Literal

from pydantic import BaseModel, Field

from .base import Affidabilita
from .contesto import StatoFonte
from .scioperi import ScioperoPrevisto

TipoEventoCitta = Literal["partita", "concerto", "manifestazione", "altro"]


class EventoCitta(BaseModel):
    id: str
    titolo: str
    tipo: TipoEventoCitta
    luogo_id: str
    luogo: str
    quartiere: str
    inizio: str = Field(description="ISO 8601 con fuso orario di Roma")
    fine: str
    persone_attese: int | None = None
    fonte: str
    affidabilita: Affidabilita
    esempio: bool = Field(default=False, description="True se è un esempio dimostrativo, da sostituire")
    simulato: bool = False


class Finestra(BaseModel):
    da: str = Field(description="Ora locale HH:MM")
    a: str
    motivo: str


class ImpattoEvento(BaseModel):
    livello: Literal["alto", "medio", "basso"]
    zona: str
    lat: float
    lon: float
    raggio_m: int
    finestre: list[Finestra]
    da_evitare: list[str]
    alternative: list[str]
    consiglio: str


class EventoPrevisto(BaseModel):
    evento: EventoCitta
    impatto: ImpattoEvento
    giorno: str = Field(description="«oggi», «domani» oppure la data, per raggruppare")


class NapoliProssimiGiorni(BaseModel):
    eventi: list[EventoPrevisto] = Field(description="Dal più vicino")
    giorni: int
    generato_al: str
    fonti: list[StatoFonte]
    scioperi: list[ScioperoPrevisto] = Field(
        default_factory=list,
        description="Scioperi dei trasporti ufficiali che toccano Napoli, dal più vicino",
    )
