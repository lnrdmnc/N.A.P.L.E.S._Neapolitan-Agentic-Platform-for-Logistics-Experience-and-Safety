"""Cache su file dei testi del modello: stessa richiesta, stesso testo, nessuna spesa in più.

Un file JSON per richiesta in `data/llm_cache/`, nominato con l'hash di modello, sistema e testo.
I file si committano (compito K1): la demo rilegge testi già controllati dal team.
"""

import hashlib
import json
from pathlib import Path

from ..scenario import DATA
from .base import Richiesta, Risposta

CARTELLA = DATA / "llm_cache"


def chiave(modello: str, richiesta: Richiesta) -> str:
    grezzo = json.dumps([modello, richiesta.sistema, richiesta.testo], ensure_ascii=False)
    return hashlib.sha256(grezzo.encode()).hexdigest()[:24]


class Cache:
    def __init__(self, cartella: Path = CARTELLA) -> None:
        self.cartella = cartella

    def leggi(self, modello: str, richiesta: Richiesta) -> Risposta | None:
        file = self.cartella / f"{chiave(modello, richiesta)}.json"
        if not file.is_file():
            return None
        dati = json.loads(file.read_text(encoding="utf-8"))
        return Risposta(testo=dati["risposta"], modello=dati["modello_risposta"], da_cache=True)

    def scrivi(self, modello: str, richiesta: Richiesta, risposta: Risposta) -> None:
        self.cartella.mkdir(parents=True, exist_ok=True)
        dati = {
            "modello": modello,
            "modello_risposta": risposta.modello,
            "sistema": richiesta.sistema,
            "richiesta": richiesta.testo,
            "risposta": risposta.testo,
        }
        file = self.cartella / f"{chiave(modello, richiesta)}.json"
        file.write_text(json.dumps(dati, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def voci(self) -> int:
        return len(list(self.cartella.glob("*.json"))) if self.cartella.is_dir() else 0
