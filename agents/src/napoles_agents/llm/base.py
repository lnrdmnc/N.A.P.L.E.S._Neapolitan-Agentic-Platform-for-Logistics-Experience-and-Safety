"""Tipi comuni dello strato LLM. Il modello scrive solo testi: non decide nulla (agents/README.md)."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Richiesta:
    """Cosa chiedere al modello. `sistema` e `testo` insieme fanno la chiave della cache."""

    sistema: str
    testo: str
    max_token: int = 2000
    effort: str = "medium"  # low per riformulazioni brevi: più veloce


@dataclass(frozen=True)
class Risposta:
    testo: str
    modello: str
    da_cache: bool = False
    finto: bool = False  # True se viene dal modello finto: mai mostrato come testo vero


class ErroreLLM(Exception):
    """Il modello non ha dato un testo utilizzabile: chi chiama usa il testo a regole."""


class Modello(Protocol):
    nome: str

    def scrivi(self, richiesta: Richiesta) -> Risposta: ...
