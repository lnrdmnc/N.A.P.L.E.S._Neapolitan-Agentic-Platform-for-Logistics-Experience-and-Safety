"""Strato LLM (compito L0): il modello scrive testi, non prende decisioni.

Uso: `scrivi(Richiesta(sistema, testo))` restituisce una Risposta oppure None. Con None chi
chiama usa il testo a regole: la demo funziona anche senza chiave, senza rete o se il modello
rifiuta. Ordine: cache su file, poi il modello scelto in `.env`; il modello finto non finisce mai
in cache né davanti ai cittadini.

Configurazione (.env): LLM_PROVIDER = anthropic | finto (vuoto: anthropic se c'è LLM_API_KEY),
LLM_MODEL (predefinito claude-opus-5-5), LLM_API_KEY.
"""

import os
import threading
from dataclasses import dataclass
from datetime import UTC, datetime

from .base import ErroreLLM, Modello, Richiesta, Risposta
from .cache import Cache
from .finto import ModelloFinto

__all__ = ["ErroreLLM", "Richiesta", "Risposta", "Servizio", "scrivi", "servizio"]


@dataclass
class UltimaChiamata:
    ora: str
    esito: str  # "ok", "cache", "errore", "finto"
    dettaglio: str | None = None


def modello_da_ambiente() -> Modello:
    provider = (os.environ.get("LLM_PROVIDER") or "").strip().lower()
    chiave = os.environ.get("LLM_API_KEY") or ""
    if provider == "finto" or not chiave:
        return ModelloFinto()
    from .anthropic_claude import ModelloClaude

    return ModelloClaude(chiave=chiave, modello=os.environ.get("LLM_MODEL") or None)


class Servizio:
    def __init__(self, modello: Modello | None = None, cache: Cache | None = None) -> None:
        self.modello = modello or modello_da_ambiente()
        self.cache = cache or Cache()
        self.ultima: UltimaChiamata | None = None
        self._lock = threading.Lock()

    def _segna(self, esito: str, dettaglio: str | None = None) -> None:
        self.ultima = UltimaChiamata(datetime.now(UTC).isoformat(), esito, dettaglio)

    def scrivi(self, richiesta: Richiesta) -> Risposta | None:
        if isinstance(self.modello, ModelloFinto):
            self._segna("finto", "Nessuna chiave: si usano i testi a regole")
            return None
        with self._lock:
            in_cache = self.cache.leggi(self.modello.nome, richiesta)
        if in_cache:
            self._segna("cache")
            return in_cache
        try:
            risposta = self.modello.scrivi(richiesta)
        except ErroreLLM as e:
            self._segna("errore", str(e))
            return None
        with self._lock:
            self.cache.scrivi(self.modello.nome, richiesta, risposta)
        self._segna("ok")
        return risposta

    def scarta(self, motivo: str) -> None:
        """Chi chiama ha scartato il testo nei controlli (llm/controlli.py)."""
        self._segna("scartato", motivo)

    @property
    def attivo(self) -> bool:
        return not isinstance(self.modello, ModelloFinto)


_servizio: Servizio | None = None


def servizio() -> Servizio:
    global _servizio
    if _servizio is None:
        _servizio = Servizio()
    return _servizio


def scrivi(richiesta: Richiesta) -> Risposta | None:
    return servizio().scrivi(richiesta)
