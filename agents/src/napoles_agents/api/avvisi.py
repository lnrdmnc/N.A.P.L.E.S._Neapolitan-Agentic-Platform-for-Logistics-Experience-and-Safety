"""Avvisi inviati e conferma di ricezione."""

from typing import Literal

from fastapi import APIRouter, HTTPException

from ..models import Alert, Ricezione
from .sessione_corrente import sessione

router = APIRouter(tags=["avvisi"])


@router.get("/api/avvisi", response_model=list[Alert])
def avvisi(pubblico: Literal["tutti", "tifoso", "residente", "turista"] | None = None) -> list[Alert]:
    """Avvisi inviati. Con `pubblico`, quelli per quel profilo più quelli per tutti."""
    tutti = sessione().avvisi
    if pubblico is None:
        return tutti
    return [a for a in tutti if a.pubblico in (pubblico, "tutti")]


@router.post("/api/avvisi/{avviso_id}/visto", status_code=202)
def visto(avviso_id: str) -> dict:
    """STUB (compito B3): accetta la conferma ma non la conta ancora."""
    if not any(a.identifier == avviso_id for a in sessione().avvisi):
        raise HTTPException(404, "Avviso inesistente")
    return {"ok": True, "stub": True}


@router.get("/api/avvisi/ricezione", response_model=list[Ricezione])
def ricezione() -> list[Ricezione]:
    """STUB (compito B3): numeri finti, sempre marcati come simulati."""
    return [
        Ricezione(avviso=a.identifier, visti_reali=0, visti_stimati=0, consegnati_stimati=0, simulato=True)
        for a in sessione().avvisi
    ]
