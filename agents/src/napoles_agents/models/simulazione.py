"""Serie del simulatore a zone (compiti S0 e B1)."""

from typing import Literal

from pydantic import BaseModel, Field


class StatoZona(BaseModel):
    id: str
    nome: str
    tipo: Literal["stadio", "piazza", "stazione", "fermata", "strada", "quartiere"]
    lat: float
    lon: float
    capienza: int
    persone: int
    in_coda: int
    carico: float = Field(description="persone / capienza")


class PassoSimulazione(BaseModel):
    t_min: int
    ora: str
    zone: list[StatoZona]
    dentro_stadio: int
    arrivati: int = Field(description="Persone che hanno lasciato l'area dello stadio")
    misure_attive: list[str]


class SerieSimulazione(BaseModel):
    scenario: Literal["sessione", "con_coordinamento", "senza_coordinamento"]
    passo_min: int = 5
    passi: list[PassoSimulazione]
    stub: bool = Field(default=False, description="True finché il simulatore a zone non è collegato")
