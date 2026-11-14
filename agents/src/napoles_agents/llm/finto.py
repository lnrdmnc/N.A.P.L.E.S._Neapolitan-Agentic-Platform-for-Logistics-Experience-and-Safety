"""Modello finto: deterministico, senza rete. Per i test e per chi non ha la chiave."""

import hashlib

from .base import Richiesta, Risposta


class ModelloFinto:
    nome = "finto"

    def scrivi(self, richiesta: Richiesta) -> Risposta:
        impronta = hashlib.sha256(f"{richiesta.sistema}\n{richiesta.testo}".encode()).hexdigest()[:8]
        return Risposta(testo=f"[testo di prova {impronta}]", modello=self.nome, finto=True)
