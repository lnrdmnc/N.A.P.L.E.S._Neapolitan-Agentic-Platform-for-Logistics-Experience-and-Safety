"""Contratti del modulo agenti.

Questi modelli sono la fonte dei contratti in contracts/agenti.schema.json:
chi li cambia rigenera lo schema con `make contracts` e avvisa in docs/STATO.md.
"""

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field


class Affidabilita(StrEnum):
    """Quanto è certa un'informazione: si mostra sempre a schermo."""

    UFFICIALE = "ufficiale"  # emessa da un'autorità (Protezione Civile, gestore)
    MISURATA = "misurata"  # misurata da una fonte affidabile (es. INGV)
    STIMATA = "stimata"  # stimata dal sistema
    NON_VERIFICATA = "non_verificata"  # voci, social


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


class Ambito(StrEnum):
    RISCHIO = "rischio"
    MOBILITA = "mobilita"
    FOLLA = "folla"
    COMUNICAZIONE = "comunicazione"


class Caso(StrEnum):
    """I tre casi di gestione degli alert (docs/PROGETTO.md, 6.2)."""

    A_UFFICIALE = "A_allarme_ufficiale"
    B_RILEVATO = "B_evento_rilevato"
    C_NON_VERIFICATO = "C_notizia_non_verificata"


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


class Piano(BaseModel):
    """Piano unico dell'Orchestratore, da approvare in control room."""

    id: str
    t_min: int
    stato: Literal["proposto", "approvato", "rifiutato", "superato"] = "proposto"
    proposte: list[Proposta]
    conflitti: list[Conflitto] = Field(default_factory=list)
    sintesi: str
    t_decisione: int | None = None


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


class VoceRegistro(BaseModel):
    indice: int
    t_min: int
    tipo: str
    contenuto: dict[str, Any]
    hash_precedente: str
    hash: str


class Indicatori(BaseModel):
    """Stessi indicatori, stesso scenario: con e senza coordinamento."""

    scenario: Literal["con_coordinamento", "senza_coordinamento"]
    deflusso_min: int = Field(description="Minuti dal fischio finale allo sgombero dell'area stadio")
    picco_attesa_persone: int = Field(description="Massimo di persone in attesa fuori dallo stadio")
    minuti_evento_avviso: int
    minuti_decisione: int
    note: list[str] = Field(default_factory=list)


class ConfrontoIndicatori(BaseModel):
    con_coordinamento: Indicatori
    senza_coordinamento: Indicatori
    ipotesi: list[str]
