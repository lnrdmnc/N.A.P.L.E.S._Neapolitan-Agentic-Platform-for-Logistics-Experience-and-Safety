"""Indicatori con e senza coordinamento."""

from fastapi import APIRouter

from ..models import ConfrontoIndicatori
from ..simulazione import confronta
from .sessione_corrente import sessione

router = APIRouter(tags=["indicatori"])


@router.get("/api/indicatori", response_model=ConfrontoIndicatori)
def indicatori() -> ConfrontoIndicatori:
    """Stessi indicatori, stesso simulatore a zone della mappa. Ogni numero ha la sua `origine`:
    il caso «con coordinamento» usa le decisioni vere dell'operatore appena ce n'è una dopo
    l'evento critico (`misurato_in_sessione`), prima usa i tempi ipotizzati (`ipotesi`)."""
    s = sessione()
    return confronta(s.scenario, s.approvati, s.avvisi)
