"""Serie del simulatore a zone per la mappa. STUB fino ai compiti S0 e B1."""

from typing import Literal

from fastapi import APIRouter

from .. import scenario as sc
from ..models import PassoSimulazione, SerieSimulazione, StatoZona
from .sessione_corrente import sessione

router = APIRouter(tags=["simulazione"])

# Zone finte ma con coordinate vere di Fuorigrotta, per disegnare la mappa da subito.
ZONE_STUB = [
    ("stadio", "Stadio Maradona", "stadio", 40.8279, 14.1930, 54000),
    ("piazzale_tecchio", "Piazzale Tecchio", "piazza", 40.8236, 14.1955, 8000),
    ("campi_flegrei_l2", "Stazione L2 Campi Flegrei", "stazione", 40.8244, 14.1969, 2000),
    ("viale_giochi", "Viale Giochi del Mediterraneo", "strada", 40.8296, 14.1902, 5000),
]


@router.get("/api/simulazione", response_model=SerieSimulazione)
def simulazione(
    scenario: Literal["sessione", "con_coordinamento", "senza_coordinamento"] = "sessione",
) -> SerieSimulazione:
    """STUB: valori finti che crescono e calano dopo il fischio finale."""
    s = sessione().scenario
    fine = s["fine_partita_t_min"]
    passi = []
    for t in range(0, s["durata_min"] + 1, 5):
        uscita = max(0.0, min(1.0, (t - fine) / 40))
        zone = []
        for i, (zid, nome, tipo, lat, lon, cap) in enumerate(ZONE_STUB):
            persone = int(s["spettatori"] * (1 - uscita)) if i == 0 else int(cap * uscita * (1 - uscita) * 3)
            zone.append(
                StatoZona(
                    id=zid,
                    nome=nome,
                    tipo=tipo,
                    lat=lat,
                    lon=lon,
                    capienza=cap,
                    persone=persone,
                    in_coda=max(0, persone - cap),
                    carico=round(persone / cap, 2),
                )
            )
        passi.append(
            PassoSimulazione(
                t_min=t,
                ora=sc.ora(s, t),
                zone=zone,
                dentro_stadio=zone[0].persone,
                arrivati=int(s["spettatori"] * uscita),
                misure_attive=[],
            )
        )
    return SerieSimulazione(scenario=scenario, passi=passi, stub=True)
