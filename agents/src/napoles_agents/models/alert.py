"""Avvisi in formato CAP semplificato e conferma di ricezione."""

from typing import Literal

from pydantic import BaseModel, Field

# Profili a cui si rivolge un avviso. «pendolare»: chi rientra verso l'area flegrea
# (Bagnoli, Pozzuoli) con Cumana o Linea 2, anche se tifoso o residente.
Pubblico = Literal["tutti", "tifoso", "residente", "pendolare", "turista"]


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
    messaggio_modello: str | None = Field(
        default=None,
        description="Messaggio per la persona scritto dal modello linguistico da headline, description e "
        "instruction, senza fatti nuovi; mai per le allerte ufficiali (caso A). None: si mostrano i campi CAP",
    )
    area: AreaAlert
    expires_t_min: int | None = None
    source: str = Field(description="Provenienza dell'informazione, mostrata all'utente")
    ufficiale: bool = Field(description="True se è un'allerta ufficiale inoltrata senza modifiche")
    simulato: bool = True
    pubblico: Pubblico
    lingua: Literal["it", "en"] = "it"
    piano_id: str | None = None


class ConfermaVisto(BaseModel):
    """Corpo di `POST /api/avvisi/{id}/visto`, inviato dalla vista cittadino quando l'avviso è a schermo."""

    dispositivo: str | None = Field(
        default=None,
        description=(
            "Identificativo anonimo generato dal telefono (per esempio un UUID casuale salvato in locale). "
            "Nessun dato personale: serve solo a non contare due volte lo stesso telefono."
        ),
    )


class Ricezione(BaseModel):
    """Quante persone hanno visto un avviso (compito B3).

    `visti_reali` è un conteggio vero delle conferme arrivate in questa sessione.
    `consegnati_stimati` e `visti_stimati` sono stime simulate (docs/IPOTESI.md): `simulato` si
    riferisce a loro.
    """

    avviso: str
    pubblico: Pubblico | None = None
    minuti_dall_invio: int = 0
    visti_reali: int = Field(description="Conferme arrivate dalla vista cittadino in questa sessione")
    visti_stimati: int
    consegnati_stimati: int
    simulato: bool = True
