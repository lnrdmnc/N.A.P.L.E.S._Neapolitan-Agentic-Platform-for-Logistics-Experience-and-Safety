"""Registro delle decisioni e verifica della catena."""

from fastapi import APIRouter

from ..models import StatoRegistro
from .sessione_corrente import sessione

router = APIRouter(tags=["registro"])


@router.get("/api/registro", response_model=StatoRegistro)
def registro() -> StatoRegistro:
    r = sessione().registro
    integro, alterata = r.verifica()
    return StatoRegistro(integro=integro, prima_voce_alterata=alterata, voci=r.voci)
