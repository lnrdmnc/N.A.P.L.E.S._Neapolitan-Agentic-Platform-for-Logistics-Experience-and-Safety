"""Indice degli agenti: per aggiungere un agente basta una riga in AGENTI.

L'agente Calendario (calendario.py) non segue lo scenario minuto per minuto: guarda i prossimi
giorni ed è esposto da GET /api/napoli/prossimi-giorni."""

from . import folla, mobilita, rischio

# Ogni agente: proponi(stato, scenario) -> list[Proposta]
AGENTI = [
    rischio.proponi,
    mobilita.proponi,
    folla.proponi,
]
