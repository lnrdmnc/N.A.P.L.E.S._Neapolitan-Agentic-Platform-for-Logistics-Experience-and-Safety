"""Piano dell'Orchestratore e decisioni dell'operatore."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..models import Alert, ModificaPiano, Piano
from .sessione_corrente import sessione

router = APIRouter(tags=["piani"])


class Decisione(BaseModel):
    operatore: str = "operatore"
    motivo: str = ""


@router.get("/api/piano", response_model=Piano | None)
def piano() -> Piano | None:
    return sessione().piano_corrente


@router.get("/api/piani", response_model=list[Piano])
def piani() -> list[Piano]:
    return sessione().piani


@router.post("/api/piano/{piano_id}/approva", response_model=list[Alert])
def approva(piano_id: str, decisione: Decisione | None = None) -> list[Alert]:
    try:
        return sessione().approva(piano_id, (decisione or Decisione()).operatore)
    except KeyError:
        raise HTTPException(404, "Piano inesistente") from None
    except ValueError as e:
        raise HTTPException(409, str(e)) from None


@router.post("/api/piano/{piano_id}/rifiuta", response_model=Piano)
def rifiuta(piano_id: str, decisione: Decisione | None = None) -> Piano:
    d = decisione or Decisione()
    try:
        return sessione().rifiuta(piano_id, d.operatore, d.motivo)
    except KeyError:
        raise HTTPException(404, "Piano inesistente") from None
    except ValueError as e:
        raise HTTPException(409, str(e)) from None


@router.post("/api/piano/{piano_id}/modifica", response_model=Piano)
def modifica(piano_id: str, modifica: ModificaPiano) -> Piano:
    """STUB (compito B2): restituisce il piano senza le proposte escluse, ma non lo salva
    e non lo scrive nel registro. La forma della risposta è quella definitiva."""
    s = sessione()
    try:
        originale = next(p for p in s.piani if p.id == piano_id)
    except StopIteration:
        raise HTTPException(404, "Piano inesistente") from None
    escluse = set(modifica.proposte_escluse)
    return originale.model_copy(
        update={
            "stato": "modificato",
            "proposte": [p for p in originale.proposte if p.id not in escluse],
        }
    )
