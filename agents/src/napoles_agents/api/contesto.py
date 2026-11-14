"""Contesto reale (INGV, meteo, livelli vulcanici). STUB fino ai compiti D1, F1, F2."""

from fastapi import APIRouter

from ..models import Contesto, LivelloVulcanico
from .sessione_corrente import sessione

router = APIRouter(tags=["contesto"])


@router.get("/api/contesto", response_model=Contesto)
def contesto() -> Contesto:
    """STUB: nessun dato reale ancora; il livello va verificato sulla fonte ufficiale."""
    livello = sessione().scenario["livello_vulcanico_campi_flegrei"]
    return Contesto(
        livelli_vulcanici=[
            LivelloVulcanico(
                area="Campi Flegrei", livello=livello, fonte="Da verificare (stub)", verificato_il=None
            )
        ],
        eventi_ingv=[],
        meteo=None,
        copia_del=None,
        stub=True,
    )
