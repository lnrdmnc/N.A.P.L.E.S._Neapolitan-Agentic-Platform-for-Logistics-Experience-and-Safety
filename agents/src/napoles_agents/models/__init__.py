"""Contratti del modulo agenti, un file per area.

Sono la fonte di contracts/agenti.openapi.json: chi li cambia esegue `make contracts`
e avvisa in docs/STATO.md. Un modello nuovo va nel file della sua area e qui sotto.
"""

from .alert import Alert, AreaAlert, Ricezione
from .base import Affidabilita, Ambito, Caso
from .citta import Evento, StatoCitta, StatoLinea, TipoEvento
from .contesto import Contesto, EventoSismicoReale, LivelloVulcanico, Meteo
from .indicatori import ConfrontoIndicatori, Indicatori, Origine
from .itinerario import Itinerario, Tratta
from .messaggi import Messaggio, TipoMessaggio
from .piano import Conflitto, Impatto, ImpattoZona, ModificaPiano, Piano, Proposta
from .registro import StatoRegistro, VoceRegistro
from .simulazione import PassoSimulazione, SerieSimulazione, StatoZona

__all__ = [
    "Affidabilita",
    "Alert",
    "Ambito",
    "AreaAlert",
    "Caso",
    "Conflitto",
    "ConfrontoIndicatori",
    "Contesto",
    "Evento",
    "EventoSismicoReale",
    "Impatto",
    "ImpattoZona",
    "Indicatori",
    "Itinerario",
    "LivelloVulcanico",
    "Messaggio",
    "Meteo",
    "ModificaPiano",
    "Origine",
    "PassoSimulazione",
    "Piano",
    "Proposta",
    "Ricezione",
    "SerieSimulazione",
    "StatoCitta",
    "StatoLinea",
    "StatoRegistro",
    "StatoZona",
    "TipoEvento",
    "TipoMessaggio",
    "Tratta",
    "VoceRegistro",
]
