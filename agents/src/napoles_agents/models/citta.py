"""Eventi dello scenario e stato della città."""

from enum import StrEnum

from pydantic import BaseModel, Field

from .base import Affidabilita


class TipoEvento(StrEnum):
    PARTITA = "partita"
    SISMA = "sisma"
    SOSPENSIONE_LINEA = "sospensione_linea"
    RIATTIVAZIONE_LINEA = "riattivazione_linea"
    ALLERTA_METEO = "allerta_meteo"
    NOTIZIA_NON_VERIFICATA = "notizia_non_verificata"


class Evento(BaseModel):
    """Un fatto della timeline dello scenario."""

    id: str
    t_min: int = Field(description="Minuti dall'inizio dello scenario")
    tipo: TipoEvento
    titolo: str
    zona: str
    fonte: str
    affidabilita: Affidabilita
    simulato: bool = True
    magnitudo: float | None = None
    linea: str | None = None
    testo_ufficiale: str | None = Field(
        default=None, description="Testo dell'allerta ufficiale, da inoltrare senza modifiche"
    )


class StatoLinea(BaseModel):
    id: str
    nome: str
    attiva: bool
    capacita_persone_min: int
    motivo: str | None = None


class StatoCitta(BaseModel):
    """Fotografia della città al minuto t, vista da tutti gli agenti."""

    t_min: int
    ora: str
    eventi: list[Evento] = Field(description="Eventi già avvenuti fino a t_min")
    linee: list[StatoLinea]
    spettatori: int
    partita_finita: bool
    livello_vulcanico_campi_flegrei: str
