"""Partite reali allo stadio Maradona, da football-data.org. Non dipende dalla sessione simulata."""

from fastapi import APIRouter

from ..fonti.partite_football import fonte
from ..models import Partite

router = APIRouter(tags=["partite"])


@router.get("/api/partite", response_model=Partite)
def partite() -> Partite:
    """Prossime partite in casa del Napoli al Maradona; `disponibile=False` se mancano anche le copie."""
    return fonte().leggi()
