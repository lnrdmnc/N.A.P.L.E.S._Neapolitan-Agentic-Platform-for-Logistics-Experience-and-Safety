"""Proposte degli agenti e piano dell'Orchestratore."""

from typing import Any, Literal

from pydantic import BaseModel, Field

from .base import Affidabilita, Ambito, Caso


class Proposta(BaseModel):
    """Quello che un agente propone all'Orchestratore."""

    id: str
    agente: Ambito
    t_min: int
    titolo: str
    azione: str = Field(description="Codice dell'azione, es. attiva_navette")
    dettagli: dict[str, Any] = Field(default_factory=dict)
    risorse: list[str] = Field(
        default_factory=list, description="Luoghi o mezzi usati: servono a trovare i conflitti"
    )
    priorita: int = Field(ge=1, le=5, description="5 = sicurezza delle persone")
    affidabilita: Affidabilita
    caso: Caso | None = None
    motivazione: str
    fonti: list[str] = Field(default_factory=list)


class Conflitto(BaseModel):
    risorsa: str
    proposte: list[str]
    risoluzione: str


class ImpattoZona(BaseModel):
    zona: str
    deflusso_min_con_piano: int
    deflusso_min_senza_piano: int
    picco_carico_con_piano: float = Field(description="Persone / capienza della zona")
    picco_carico_senza_piano: float


class Impatto(BaseModel):
    """Effetto stimato del piano, calcolato dal simulatore a zone (compito B1)."""

    zone: list[ImpattoZona]
    stub: bool = Field(default=False, description="True finché il simulatore a zone non è collegato")


class Piano(BaseModel):
    """Piano unico dell'Orchestratore, da approvare in control room."""

    id: str
    t_min: int
    stato: Literal["proposto", "modificato", "approvato", "rifiutato", "superato"] = "proposto"
    proposte: list[Proposta]
    conflitti: list[Conflitto] = Field(default_factory=list)
    sintesi: str
    t_decisione: int | None = None
    affidabilita_minima: Affidabilita | None = Field(
        default=None, description="L'affidabilità più bassa tra le proposte del piano"
    )
    impatto: Impatto | None = None


class ModificaPiano(BaseModel):
    proposte_escluse: list[str]
    motivo: str = ""
    operatore: str = "operatore"
