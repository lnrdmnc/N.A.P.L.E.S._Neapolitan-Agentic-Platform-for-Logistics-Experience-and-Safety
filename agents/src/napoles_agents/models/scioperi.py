"""Scioperi dei trasporti: dato ufficiale del Ministero delle Infrastrutture e dei Trasporti."""

from pydantic import BaseModel, Field

from .base import Affidabilita


class Sciopero(BaseModel):
    id: str = Field(description="Identificativi MIT degli scioperi uniti (stessa data, orario e categoria)")
    inizio: str = Field(description="ISO 8601, ora di Roma")
    fine: str
    orario: str = Field(
        description="Modalità come pubblicata dal Ministero, es. «4 ORE: DALLE 11.00 ALLE 15.00»"
    )
    settore: str
    rilevanza: str = Field(description="Locale o Nazionale")
    area: str = Field(description="Provincia o «Italia»")
    categoria: str = Field(description="Categoria interessata, come pubblicata")
    sindacati: list[str]
    proclamato_il: str | None = None
    fonte: str = "Ministero delle Infrastrutture e dei Trasporti (scioperi.mit.gov.it)"
    affidabilita: Affidabilita = Affidabilita.UFFICIALE
    simulato: bool = False


class ScioperoPrevisto(BaseModel):
    sciopero: Sciopero
    giorno: str = Field(description="«oggi», «domani» oppure la data")
    linee_coinvolte: list[str]
    linee_non_coinvolte: list[str]
    eventi_coinvolti: list[str] = Field(
        description="Eventi dei prossimi giorni con l'arrivo o l'uscita durante lo sciopero"
    )
    consiglio: str
