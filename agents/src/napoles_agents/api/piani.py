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
    """L'operatore esclude proposte prima di approvare. Il piano passa a «modificato», resta da
    approvare o rifiutare, e la modifica finisce nel registro. Si può rimodificare: conta l'ultimo
    elenco di escluse. Le allerte ufficiali (caso A) non si possono escludere (409)."""
    try:
        return sessione().modifica(piano_id, modifica.proposte_escluse, modifica.motivo, modifica.operatore)
    except KeyError as e:
        raise HTTPException(404, f"Piano o proposta inesistente: {e}") from None
    except ValueError as e:
        raise HTTPException(409, str(e)) from None
