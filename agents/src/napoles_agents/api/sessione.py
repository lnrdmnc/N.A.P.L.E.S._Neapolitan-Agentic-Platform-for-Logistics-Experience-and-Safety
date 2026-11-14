"""Sessione demo: salute, scenario, reset, avanzamento del tempo, stato della città."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import scenario as sc
from ..models import StatoCitta
from .sessione_corrente import nuova, sessione

router = APIRouter(tags=["sessione"])


class Avanza(BaseModel):
    t_min: int


class Scenario(BaseModel):
    id: str
    titolo: str
    ora_inizio: str
    durata_min: int
    fine_partita_t_min: int
    timeline: list[dict]


@router.get("/api/salute")
def salute() -> dict:
    return {"ok": True, "t_min": sessione().t_min}


@router.get("/api/scenario", response_model=Scenario)
def scenario() -> Scenario:
    s = sessione().scenario
    return Scenario(
        id=s["id"],
        titolo=s["titolo"],
        ora_inizio=s["ora_inizio"],
        durata_min=s["durata_min"],
        fine_partita_t_min=s["fine_partita_t_min"],
        timeline=[
            {"t_min": e.t_min, "ora": sc.ora(s, e.t_min), "titolo": e.titolo, "tipo": e.tipo.value}
            for e in sc.eventi(s)
        ],
    )


@router.post("/api/reset", response_model=StatoCitta)
def reset() -> StatoCitta:
    return nuova().stato


@router.post("/api/avanza", response_model=StatoCitta)
def avanza(richiesta: Avanza) -> StatoCitta:
    s = sessione()
    if not 0 <= richiesta.t_min <= s.scenario["durata_min"]:
        raise HTTPException(422, "t_min fuori dalla durata dello scenario")
    return s.avanza(richiesta.t_min)


@router.get("/api/stato", response_model=StatoCitta)
def stato() -> StatoCitta:
    return sessione().stato
