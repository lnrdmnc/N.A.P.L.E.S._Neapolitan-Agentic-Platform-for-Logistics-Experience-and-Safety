"""API HTTP del modulo agenti, per la web app. Avvio: `make agents-run` (porta 8000)."""

from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import scenario as sc
from .models import Alert, ConfrontoIndicatori, Piano, StatoCitta, VoceRegistro
from .motore import Sessione
from .simulazione import confronta

app = FastAPI(title="N.A.P.L.E.S. – agenti", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

sessione = Sessione()


class Avanza(BaseModel):
    t_min: int


class Decisione(BaseModel):
    operatore: str = "operatore"
    motivo: str = ""


class Registro(BaseModel):
    integro: bool
    prima_voce_alterata: int | None
    voci: list[VoceRegistro]


class Scenario(BaseModel):
    id: str
    titolo: str
    ora_inizio: str
    durata_min: int
    fine_partita_t_min: int
    timeline: list[dict]


@app.get("/api/salute")
def salute() -> dict:
    return {"ok": True, "t_min": sessione.t_min}


@app.get("/api/scenario", response_model=Scenario)
def scenario() -> Scenario:
    s = sessione.scenario
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


@app.post("/api/reset", response_model=StatoCitta)
def reset() -> StatoCitta:
    global sessione
    sessione = Sessione()
    return sessione.stato


@app.post("/api/avanza", response_model=StatoCitta)
def avanza(richiesta: Avanza) -> StatoCitta:
    if not 0 <= richiesta.t_min <= sessione.scenario["durata_min"]:
        raise HTTPException(422, "t_min fuori dalla durata dello scenario")
    return sessione.avanza(richiesta.t_min)


@app.get("/api/stato", response_model=StatoCitta)
def stato() -> StatoCitta:
    return sessione.stato


@app.get("/api/piano", response_model=Piano | None)
def piano() -> Piano | None:
    return sessione.piano_corrente


@app.get("/api/piani", response_model=list[Piano])
def piani() -> list[Piano]:
    return sessione.piani


@app.post("/api/piano/{piano_id}/approva", response_model=list[Alert])
def approva(piano_id: str, decisione: Decisione | None = None) -> list[Alert]:
    try:
        return sessione.approva(piano_id, (decisione or Decisione()).operatore)
    except KeyError:
        raise HTTPException(404, "Piano inesistente") from None
    except ValueError as e:
        raise HTTPException(409, str(e)) from None


@app.post("/api/piano/{piano_id}/rifiuta", response_model=Piano)
def rifiuta(piano_id: str, decisione: Decisione | None = None) -> Piano:
    d = decisione or Decisione()
    try:
        return sessione.rifiuta(piano_id, d.operatore, d.motivo)
    except KeyError:
        raise HTTPException(404, "Piano inesistente") from None
    except ValueError as e:
        raise HTTPException(409, str(e)) from None


@app.get("/api/avvisi", response_model=list[Alert])
def avvisi(pubblico: Literal["tutti", "tifoso", "residente", "turista"] | None = None) -> list[Alert]:
    """Avvisi inviati. Con `pubblico`, quelli per quel profilo più quelli per tutti."""
    if pubblico is None:
        return sessione.avvisi
    return [a for a in sessione.avvisi if a.pubblico in (pubblico, "tutti")]


@app.get("/api/indicatori", response_model=ConfrontoIndicatori)
def indicatori() -> ConfrontoIndicatori:
    return confronta(sessione.scenario)


@app.get("/api/registro", response_model=Registro)
def registro() -> Registro:
    integro, alterata = sessione.registro.verifica()
    return Registro(integro=integro, prima_voce_alterata=alterata, voci=sessione.registro.voci)
