"""Napoli oggi e nei prossimi giorni: eventi previsti, zone interessate, percorsi alternativi.

Non dipende dalla sessione simulata: guarda il calendario vero di oggi in avanti.
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Query

from ..agenti.calendario import prossimi_giorni
from ..models import NapoliProssimiGiorni

router = APIRouter(tags=["napoli"])


@router.get("/api/napoli/prossimi-giorni", response_model=NapoliProssimiGiorni)
def napoli_prossimi_giorni(giorni: int = Query(10, ge=1, le=30)) -> NapoliProssimiGiorni:
    """Partite reali al Maradona ed eventi dell'elenco curato da oggi a `giorni` giorni, ciascuno
    con zona interessata, fasce orarie critiche, fermate da evitare e alternative."""
    return prossimi_giorni(datetime.now(UTC), giorni)
