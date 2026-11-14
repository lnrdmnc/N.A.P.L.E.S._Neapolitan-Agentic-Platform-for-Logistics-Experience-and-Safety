"""Traffico reale sulle strade, da Google Routes API. Mai simulato: se manca, si dice che manca."""

from enum import StrEnum

from pydantic import BaseModel, Field


class LivelloTraffico(StrEnum):
    """Soglie sul rapporto tra durata con traffico e senza traffico (docs/IPOTESI.md)."""

    SCORREVOLE = "scorrevole"
    RALLENTATO = "rallentato"
    CONGESTIONATO = "congestionato"


class PercorsoTraffico(BaseModel):
    id: str
    nome: str
    da: str
    a: str
    durata_min: float | None = Field(default=None, description="Tempo in auto con il traffico attuale")
    durata_senza_traffico_min: float | None = None
    ritardo_min: float | None = None
    distanza_km: float | None = None
    livello: LivelloTraffico | None = None
    polilinea: str | None = Field(default=None, description="Tracciato codificato (Google encoded polyline)")


class Traffico(BaseModel):
    percorsi: list[PercorsoTraffico]
    disponibile: bool = Field(
        description="False se la fonte non ha risposto: nessun dato inventato al suo posto"
    )
    rilevato_alle: str | None = Field(default=None, description="Ora della rilevazione, ISO 8601")
    motivo: str | None = Field(default=None, description="Perché i dati mancano o non sono freschi")
    fonte: str = "Google Maps Platform, Routes API (traffico in tempo reale)"
    simulato: bool = False
