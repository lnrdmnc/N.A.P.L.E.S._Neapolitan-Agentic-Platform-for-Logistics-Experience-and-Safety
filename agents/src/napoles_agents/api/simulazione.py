"""Serie del simulatore a zone per la mappa (compiti S0 e B1)."""

from typing import Literal

from fastapi import APIRouter

from ..models import SerieSimulazione
from ..simulatore import misure_da_scenario, simula
from .sessione_corrente import sessione

router = APIRouter(tags=["simulazione"])


@router.get("/api/simulazione", response_model=SerieSimulazione)
def simulazione(
    scenario: Literal["sessione", "con_coordinamento", "senza_coordinamento"] = "sessione",
) -> SerieSimulazione:
    """Passi da 5 minuti con lo stato di ogni zona.

    - `sessione`: la città secondo le decisioni approvate fin qui dall'operatore, proiettata
      fino a fine scenario (la web app mostra i passi fino a `t_min` di `/api/stato`);
    - `con_coordinamento` e `senza_coordinamento`: i due casi del confronto, per lo schermo diviso.
    """
    s = sessione()
    if scenario == "sessione":
        return s.simulazione()
    return simula(s.scenario, misure_da_scenario(s.scenario, scenario == "con_coordinamento"), scenario)
