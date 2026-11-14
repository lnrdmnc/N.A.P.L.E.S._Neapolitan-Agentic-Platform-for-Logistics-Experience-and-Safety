"""Cosa visitare: luoghi reali e come raggiungerli, tenendo conto di eventi e scioperi veri."""

from typing import Literal

from pydantic import BaseModel, Field

from .contesto import StatoFonte


class Accesso(BaseModel):
    linea: str
    codice: str
    gestore: str
    fermata: str
    metri: int = Field(description="Distanza in linea d'aria dal luogo")
    minuti_a_piedi: int
    disponibile: bool = True
    motivo: str | None = Field(default=None, description="Perché la linea può mancare (sciopero)")
    motivo_en: str | None = None


class LuogoConsigliato(BaseModel):
    id: str
    nome: str
    name_en: str
    zona: str
    descrizione: str
    description_en: str
    lat: float
    lon: float
    fonte_coordinate: str
    accessi: list[Accesso]
    stato: Literal["consigliato", "con_disagi", "da_evitare_ora"]
    motivi: list[str] = Field(default_factory=list)
    motivi_en: list[str] = Field(default_factory=list)


class Momento(BaseModel):
    quando: str = Field(description="ISO 8601, ora di Roma")
    etichetta: str
    label_en: str


class DaVisitare(BaseModel):
    quando: str
    luoghi: list[LuogoConsigliato] = Field(
        description="Prima i consigliati, poi quelli con disagi, poi da evitare"
    )
    momenti: list[Momento] = Field(description="Momenti dei prossimi giorni in cui i consigli cambiano")
    fonti: list[StatoFonte]
    simulato: bool = False
