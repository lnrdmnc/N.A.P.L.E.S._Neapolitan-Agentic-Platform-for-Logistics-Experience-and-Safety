"""API HTTP del modulo agenti, per la web app. Avvio: `make agents-run` (porta 8001).

Un router per area. Per aggiungerne uno: un file in questa cartella e una riga in ROUTER.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import (
    avvisi,
    contesto,
    indicatori,
    itinerario,
    messaggi,
    partite,
    piani,
    registro,
    ricezione,
    sessione,
    simulazione,
    traffico,
)

PORTA = 8001  # concordata con la web app (Francesco Sannella)

ROUTER = [
    sessione.router,
    piani.router,
    avvisi.router,
    ricezione.router,
    messaggi.router,
    indicatori.router,
    registro.router,
    simulazione.router,
    contesto.router,
    itinerario.router,
    traffico.router,
    partite.router,
]

app = FastAPI(title="N.A.P.L.E.S. – agenti", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
for r in ROUTER:
    app.include_router(r)
