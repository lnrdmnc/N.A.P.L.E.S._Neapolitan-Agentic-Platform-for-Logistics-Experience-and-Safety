"""Avvisi in formato CAP semplificato e conferma di ricezione."""

from typing import Literal

from pydantic import BaseModel, Field


class AreaAlert(BaseModel):
    descrizione: str
    poligono: list[tuple[float, float]] = Field(default_factory=list, description="Coppie (lat, lon)")


class Alert(BaseModel):
    """Messaggio di allerta: versione semplificata del Common Alerting Protocol (OASIS CAP)."""

    identifier: str
    sender: str
    sent_t_min: int
    msgType: Literal["Alert", "Update", "Cancel"]
    references: str | None = None
    severity: Literal["Extreme", "Severe", "Moderate", "Minor", "Unknown"]
    urgency: Literal["Immediate", "Expected", "Future", "Past", "Unknown"]
    certainty: Literal["Observed", "Likely", "Possible", "Unlikely", "Unknown"]
    event: str
    headline: str
    description: str
    instruction: str | None = None
    area: AreaAlert
    expires_t_min: int | None = None
    source: str = Field(description="Provenienza dell'informazione, mostrata all'utente")
    ufficiale: bool = Field(description="True se è un'allerta ufficiale inoltrata senza modifiche")
    simulato: bool = True
    pubblico: Literal["tutti", "tifoso", "residente", "turista"]
    lingua: Literal["it", "en"] = "it"
    piano_id: str | None = None


class Ricezione(BaseModel):
    """Quante persone hanno visto un avviso (compito B3)."""

    avviso: str
    visti_reali: int = Field(description="Conferme arrivate dalla vista cittadino in questa sessione")
    visti_stimati: int
    consegnati_stimati: int
    simulato: bool = True
