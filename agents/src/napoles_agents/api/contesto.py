"""Contesto reale (INGV, meteo, livelli vulcanici): compiti F1, F2. Mai mescolato al simulato.

Non dipende dalla sessione: sono dati veri di oggi, mostrati accanto allo scenario simulato e
sempre distinti da esso. Il livello di allerta vulcanica ufficiale non ha un servizio da leggere:
si verifica a mano sulla fonte e si registra con la data in data/livelli_vulcanici.json.
"""

import json

from fastapi import APIRouter

from ..fonti import ingv, meteo
from ..models import Contesto, LivelloVulcanico
from ..scenario import DATA

router = APIRouter(tags=["contesto"])


@router.get("/api/contesto", response_model=Contesto)
def contesto() -> Contesto:
    """Ultimi eventi INGV reali (Campi Flegrei, Vesuvio, ultimi 7 giorni) e meteo reale allo stadio.
    Ogni fonte dichiara in `fonti` se è disponibile, quando è stata letta e se è una copia salvata."""
    eventi, stato_ingv = ingv.fonte().leggi()
    dati_meteo, stato_meteo = meteo.fonte().leggi()
    verificati = json.loads((DATA / "livelli_vulcanici.json").read_text(encoding="utf-8"))["livelli"]
    copie = [s.aggiornato_al for s in (stato_ingv, stato_meteo) if s.copia and s.aggiornato_al]
    return Contesto(
        livelli_vulcanici=[LivelloVulcanico(**v) for v in verificati],
        eventi_ingv=eventi,
        meteo=dati_meteo,
        copia_del=min(copie) if copie else None,
        fonti=[stato_ingv, stato_meteo],
        stub=False,
    )
