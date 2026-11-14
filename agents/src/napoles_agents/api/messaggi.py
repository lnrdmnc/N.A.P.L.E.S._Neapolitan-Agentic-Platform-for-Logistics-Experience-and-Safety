"""Linea del tempo dei messaggi tra agenti."""

from fastapi import APIRouter

from ..models import Messaggio
from .sessione_corrente import sessione

router = APIRouter(tags=["messaggi"])


@router.get("/api/messaggi", response_model=list[Messaggio])
def messaggi(da_seq: int = 0) -> list[Messaggio]:
    """Messaggi successivi a `da_seq`: la web app passa l'ultimo `seq` che ha già."""
    return sessione().bus.da(da_seq)
