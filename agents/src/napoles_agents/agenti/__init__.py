"""Indice degli agenti: per aggiungere un agente basta una riga in AGENTI."""

from . import folla, mobilita, rischio

# Ogni agente: proponi(stato, scenario) -> list[Proposta]
AGENTI = [
    rischio.proponi,
    mobilita.proponi,
    folla.proponi,
]
