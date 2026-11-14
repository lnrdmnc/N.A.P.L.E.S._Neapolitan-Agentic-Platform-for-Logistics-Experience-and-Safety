"""Contesto reale: livello vulcanico, eventi INGV, meteo (compiti F1, F2). Mai mescolato al simulato."""

from pydantic import BaseModel, Field


class LivelloVulcanico(BaseModel):
    area: str
    livello: str
    fonte: str
    verificato_il: str | None = Field(default=None, description="Data della verifica sulla fonte ufficiale")


class EventoSismicoReale(BaseModel):
    id: str
    tempo: str
    magnitudo: float
    tipo_magnitudo: str
    luogo: str
    lat: float
    lon: float
    profondita_km: float
    simulato: bool = False


class Meteo(BaseModel):
    tempo: str
    temperatura_c: float
    precipitazione_mm: float
    vento_kmh: float
    codice_meteo: int
    simulato: bool = False


class Contesto(BaseModel):
    livelli_vulcanici: list[LivelloVulcanico]
    eventi_ingv: list[EventoSismicoReale]
    meteo: Meteo | None = None
    copia_del: str | None = Field(default=None, description="Data della copia in cache usata")
    stub: bool = Field(default=False, description="True finché le fonti reali non sono collegate")
