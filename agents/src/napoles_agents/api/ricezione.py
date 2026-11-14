"""Conferma di ricezione degli avvisi (compito B3)."""

from fastapi import APIRouter, HTTPException

from ..models import ConfermaVisto, Ricezione
from ..ricezione import ricezione as calcola
from .sessione_corrente import sessione

router = APIRouter(tags=["ricezione"])


@router.post("/api/avvisi/{avviso_id}/visto", response_model=Ricezione)
def visto(avviso_id: str, conferma: ConfermaVisto | None = None) -> Ricezione:
    """La vista cittadino conferma che l'avviso è stato mostrato. Si contano solo avvisi davvero
    inviati (404 altrimenti) e una sola conferma per `dispositivo`."""
    s = sessione()
    alert = next((a for a in s.avvisi if a.identifier == avviso_id), None)
    if alert is None:
        raise HTTPException(404, "Avviso inesistente o non inviato")
    s.ricezioni.conferma(avviso_id, (conferma or ConfermaVisto()).dispositivo)
    return calcola(alert, s.t_min, s.scenario, s.ricezioni)


@router.get("/api/avvisi/ricezione", response_model=list[Ricezione])
def ricezione() -> list[Ricezione]:
    """Per ogni avviso inviato: conferme reali e stime simulate al minuto attuale della sessione."""
    s = sessione()
    return [calcola(a, s.t_min, s.scenario, s.ricezioni) for a in s.avvisi]
