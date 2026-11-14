"""Contesto reale (INGV, meteo, livelli vulcanici): compiti F1, F2. Mai mescolato al simulato.

Non dipende dalla sessione: sono dati veri di oggi, mostrati accanto allo scenario simulato e
sempre distinti da esso. Il livello di allerta vulcanica ufficiale si legge dal file pubblico della
mappa della Protezione Civile (fonti/vulcani.py); senza rete, la copia salvata o il livello
verificato a mano con la sua data (data/livelli_vulcanici.json).
"""

from fastapi import APIRouter

from ..fonti import ingv, meteo, vulcani
from ..models import Contesto

router = APIRouter(tags=["contesto"])


@router.get("/api/contesto", response_model=Contesto)
def contesto() -> Contesto:
    """Livello di allerta ufficiale (Protezione Civile), ultimi eventi INGV reali (Campi Flegrei,
    Vesuvio, ultimi 7 giorni) e meteo reale allo stadio.
    Ogni fonte dichiara in `fonti` se è disponibile, quando è stata letta e se è una copia salvata."""
    eventi, stato_ingv = ingv.fonte().leggi()
    dati_meteo, stato_meteo = meteo.fonte().leggi()
    livelli, stato_vulcani = vulcani.fonte().leggi()
    stati = (stato_vulcani, stato_ingv, stato_meteo)
    copie = [s.aggiornato_al for s in stati if s.copia and s.aggiornato_al]
    return Contesto(
        livelli_vulcanici=livelli,
        eventi_ingv=eventi,
        meteo=dati_meteo,
        copia_del=min(copie) if copie else None,
        fonti=list(stati),
        stub=False,
    )
