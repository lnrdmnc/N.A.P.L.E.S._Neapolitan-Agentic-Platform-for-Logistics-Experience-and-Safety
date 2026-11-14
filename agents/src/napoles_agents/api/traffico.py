"""Traffico reale intorno allo stadio, da Google Routes API. Non dipende dalla sessione simulata."""

from fastapi import APIRouter

from ..fonti.traffico_google import fonte
from ..models import Traffico

router = APIRouter(tags=["traffico"])


@router.get("/api/traffico", response_model=Traffico)
def traffico() -> Traffico:
    """Tempi in auto con traffico reale; `disponibile=False` se la fonte non risponde."""
    return fonte().leggi()
