"""Cosa visitare: luoghi reali con le linee per arrivarci, secondo eventi e scioperi veri."""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Query

from ..agenti import calendario, visite
from ..models import DaVisitare

router = APIRouter(tags=["napoli"])


@router.get("/api/napoli/da-visitare", response_model=DaVisitare)
def da_visitare(quando: str | None = Query(None, description="ISO 8601; vuoto per adesso")) -> DaVisitare:
    """Luoghi da visitare in quel momento: prima i consigliati, poi quelli con disagi per sciopero,
    poi quelli in zone affollate da un evento. Dati reali, mai la simulazione dello scenario."""
    adesso = datetime.now(UTC)
    try:
        momento = datetime.fromisoformat(quando) if quando else adesso
    except ValueError as errore:
        raise HTTPException(422, "quando: data non valida") from errore
    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=calendario.ROMA)
    giorni = max(10, min(30, (momento - adesso).days + 2))
    return visite.consigli(momento, calendario.prossimi_giorni(adesso, giorni), adesso)
