"""Itinerario del turista. STUB fino al compito B6."""

from fastapi import APIRouter

from ..models import Itinerario, Tratta
from .sessione_corrente import sessione

router = APIRouter(tags=["itinerario"])


@router.get("/api/itinerario", response_model=Itinerario)
def itinerario() -> Itinerario:
    """STUB: itinerario fisso; la percorribilità segue solo lo stato delle linee."""
    s = sessione()
    linea2_attiva = next(linea.attiva for linea in s.stato.linee if linea.id == "linea2")
    return Itinerario(
        tappe=["Stadio Maradona", "Piazza del Plebiscito", "Castel dell'Ovo"],
        tratte=[
            Tratta(
                da="Stadio Maradona",
                a="Piazza del Plebiscito",
                mezzo="Linea 2",
                minuti=25,
                percorribile=linea2_attiva,
                motivo=None if linea2_attiva else "Linea 2 sospesa per verifiche tecniche",
                alternativa=None if linea2_attiva else "Navetta sostitutiva, poi Linea 1",
            ),
            Tratta(
                da="Piazza del Plebiscito", a="Castel dell'Ovo", mezzo="a piedi", minuti=12, percorribile=True
            ),
        ],
        fonte="Stub: tempi indicativi",
        verificato_al_t_min=s.t_min,
        stub=True,
    )
