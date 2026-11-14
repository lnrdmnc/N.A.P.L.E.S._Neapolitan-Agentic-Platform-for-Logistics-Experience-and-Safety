"""Stato dello strato LLM e prova dal browser (compito L0)."""

from pydantic import BaseModel, Field


class StatoLLM(BaseModel):
    provider: str = Field(description="anthropic oppure finto (nessuna chiave: testi a regole)")
    modello: str
    chiave_configurata: bool
    voci_in_cache: int
    ultima_chiamata_ora: str | None = None
    ultima_chiamata_esito: str | None = Field(default=None, description="ok, cache, errore, finto")
    ultima_chiamata_dettaglio: str | None = None


class ProvaLLM(BaseModel):
    richiesta: str
    testo: str | None = Field(description="None se il modello non ha risposto: si userebbe il testo a regole")
    modello: str | None = None
    da_cache: bool = False
    simulato: bool = Field(default=True, description="La situazione descritta è simulata")
