"""Messaggi sul bus: la linea del tempo che la control room osserva."""

from typing import Literal

from pydantic import BaseModel, Field

from .base import Affidabilita

TipoMessaggio = Literal["evento", "proposta", "conflitto", "piano", "decisione", "avviso"]


class Messaggio(BaseModel):
    seq: int = Field(description="Numero progressivo nella sessione: usarlo con ?da_seq=")
    t_min: int
    ora: str
    da: str = Field(description="Chi parla: fonte, agente, orchestratore, operatore")
    a: str = Field(description="A chi: agente, orchestratore, operatore, pubblico")
    tipo: TipoMessaggio
    titolo: str
    testo: str
    affidabilita: Affidabilita | None = None
    simulato: bool = True
    rif: str | None = Field(
        default=None, description="Id dell'oggetto collegato: evento, proposta, piano, avviso"
    )
