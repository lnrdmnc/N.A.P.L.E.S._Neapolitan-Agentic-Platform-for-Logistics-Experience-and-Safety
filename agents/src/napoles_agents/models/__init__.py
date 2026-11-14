"""Contratti del modulo agenti, un file per area.

Sono la fonte di contracts/agenti.openapi.json: chi li cambia esegue `make contracts`
e avvisa in docs/STATO.md. Un modello nuovo va nel file della sua area e qui sotto.
"""

from .alert import Alert, AreaAlert, ConfermaVisto, Pubblico, Ricezione
from .base import Affidabilita, Ambito, Caso
from .calendario import EventoCitta, EventoPrevisto, Finestra, ImpattoEvento, NapoliProssimiGiorni
from .citta import Evento, StatoCitta, StatoLinea, TipoEvento
from .contesto import Contesto, EventoSismicoReale, LivelloVulcanico, Meteo, StatoFonte
from .indicatori import ConfrontoIndicatori, Indicatori, Origine
from .llm import ProvaLLM, StatoLLM
from .messaggi import Messaggio, TipoMessaggio
from .partite import Partita, Partite
from .piano import Conflitto, Impatto, ImpattoZona, ModificaPiano, Piano, Proposta
from .registro import StatoRegistro, VoceRegistro
from .scioperi import Sciopero, ScioperoPrevisto
from .simulazione import PassoSimulazione, SerieSimulazione, StatoZona
from .traffico import LivelloTraffico, PercorsoTraffico, Traffico
from .visite import Accesso, DaVisitare, LuogoConsigliato, Momento

__all__ = [
    "Accesso",
    "Affidabilita",
    "Alert",
    "Ambito",
    "AreaAlert",
    "Caso",
    "ConfermaVisto",
    "Conflitto",
    "ConfrontoIndicatori",
    "Contesto",
    "DaVisitare",
    "Evento",
    "EventoCitta",
    "EventoPrevisto",
    "EventoSismicoReale",
    "Finestra",
    "Impatto",
    "ImpattoEvento",
    "ImpattoZona",
    "Indicatori",
    "LivelloTraffico",
    "LivelloVulcanico",
    "LuogoConsigliato",
    "Messaggio",
    "Meteo",
    "ModificaPiano",
    "Momento",
    "NapoliProssimiGiorni",
    "Origine",
    "Partita",
    "Partite",
    "PassoSimulazione",
    "PercorsoTraffico",
    "Piano",
    "Proposta",
    "ProvaLLM",
    "Pubblico",
    "Ricezione",
    "Sciopero",
    "ScioperoPrevisto",
    "SerieSimulazione",
    "StatoCitta",
    "StatoFonte",
    "StatoLLM",
    "StatoLinea",
    "StatoRegistro",
    "StatoZona",
    "TipoEvento",
    "TipoMessaggio",
    "Traffico",
    "VoceRegistro",
]
