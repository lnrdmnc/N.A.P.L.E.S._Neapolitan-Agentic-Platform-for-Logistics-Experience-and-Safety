"""Caricamento dello scenario e stato della città al minuto t."""

import json
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

from .models import Evento, StatoCitta, StatoLinea, TipoEvento

DATA = Path(__file__).parent / "data"


@lru_cache
def carica(nome: str = "scenario_maradona") -> dict[str, Any]:
    return json.loads((DATA / f"{nome}.json").read_text(encoding="utf-8"))


def eventi(scenario: dict[str, Any]) -> list[Evento]:
    return sorted((Evento(**e) for e in scenario["eventi"]), key=lambda e: e.t_min)


def ora(scenario: dict[str, Any], t_min: int) -> str:
    inizio = datetime.strptime(scenario["ora_inizio"], "%H:%M")
    return (inizio + timedelta(minutes=t_min)).strftime("%H:%M")


def stato(scenario: dict[str, Any], t_min: int) -> StatoCitta:
    passati = [e for e in eventi(scenario) if e.t_min <= t_min]
    sospese: dict[str, str] = {}
    for e in passati:
        if e.tipo == TipoEvento.SOSPENSIONE_LINEA and e.linea:
            sospese[e.linea] = e.titolo
        elif e.tipo == TipoEvento.RIATTIVAZIONE_LINEA and e.linea:
            sospese.pop(e.linea, None)
    linee = [
        StatoLinea(
            id=linea["id"],
            nome=linea["nome"],
            attiva=linea["id"] not in sospese,
            capacita_persone_min=linea["capacita_persone_min"],
            motivo=sospese.get(linea["id"]),
        )
        for linea in scenario["linee"]
    ]
    return StatoCitta(
        t_min=t_min,
        ora=ora(scenario, t_min),
        eventi=passati,
        linee=linee,
        spettatori=scenario["spettatori"],
        partita_finita=t_min >= scenario["fine_partita_t_min"],
        livello_vulcanico_campi_flegrei=scenario["livello_vulcanico_campi_flegrei"],
    )
