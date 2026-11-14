"""Indicatori con e senza coordinamento."""

from fastapi import APIRouter

from ..models import ConfrontoIndicatori
from ..simulazione import confronta
from .sessione_corrente import sessione

router = APIRouter(tags=["indicatori"])


@router.get("/api/indicatori", response_model=ConfrontoIndicatori)
def indicatori() -> ConfrontoIndicatori:
    return confronta(sessione().scenario)
