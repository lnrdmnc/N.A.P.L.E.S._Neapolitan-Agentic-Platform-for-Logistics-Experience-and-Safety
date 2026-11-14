"""Partite allo stadio Maradona, da football-data.org. Dato reale: mai simulato, mai inventato."""

from pydantic import BaseModel, Field


class Partita(BaseModel):
    id: int
    data_ora: str = Field(description="Calcio d'inizio, ISO 8601 in UTC")
    casa: str
    ospite: str
    competizione: str
    stato: str = Field(description="Stato secondo la fonte: SCHEDULED, TIMED, IN_PLAY, FINISHED…")
    stadio: str | None = Field(default=None, description="Stadio indicato dalla fonte, se presente")


class Partite(BaseModel):
    partite: list[Partita] = Field(description="Partite in casa del Napoli, dalla più vicina")
    disponibile: bool = Field(
        description="False se non c'è né una risposta né una copia: nessun dato inventato"
    )
    aggiornato_al: str | None = Field(default=None, description="Quando la fonte ha risposto, ISO 8601")
    copia: bool = Field(
        default=False, description="True se i dati vengono dalla copia salvata, non da una risposta fresca"
    )
    motivo: str | None = Field(default=None, description="Perché i dati mancano o non sono freschi")
    fonte: str = "football-data.org"
    simulato: bool = False
