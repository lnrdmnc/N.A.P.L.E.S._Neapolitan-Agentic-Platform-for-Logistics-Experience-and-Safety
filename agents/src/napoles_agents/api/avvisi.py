"""Avvisi inviati. La conferma di ricezione è in api/ricezione.py."""

from fastapi import APIRouter

from ..models import Alert, Pubblico
from .sessione_corrente import sessione

router = APIRouter(tags=["avvisi"])


@router.get("/api/avvisi", response_model=list[Alert])
def avvisi(pubblico: Pubblico | None = None) -> list[Alert]:
    """Avvisi inviati. Con `pubblico`, quelli per quel profilo più quelli per tutti, tranne gli
    avvisi per tutti che hanno già una versione per quel profilo (es. l'allerta ufficiale con la
    cornice in inglese per il turista, che ha `references` all'originale)."""
    tutti = sessione().avvisi
    if pubblico is None:
        return tutti
    sostituiti = {a.references for a in tutti if a.pubblico == pubblico and a.references}
    return [
        a
        for a in tutti
        if a.pubblico == pubblico or (a.pubblico == "tutti" and a.identifier not in sostituiti)
    ]
