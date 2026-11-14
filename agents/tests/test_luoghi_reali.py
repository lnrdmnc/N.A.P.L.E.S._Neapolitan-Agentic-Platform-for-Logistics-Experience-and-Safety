"""Luoghi reali: coordinate delle zone da GTFS e OpenStreetMap, area degli avvisi sul contorno vero."""

import json

from napoles_agents.agenti.comunicazione import AREA_FUORIGROTTA
from napoles_agents.scenario import DATA


def _dentro(lat: float, lon: float, poligono: list[tuple[float, float]]) -> bool:
    """Ray casting su (lat, lon)."""
    dentro = False
    for (y1, x1), (y2, x2) in zip(poligono, poligono[1:] + poligono[:1], strict=True):
        if (y1 > lat) != (y2 > lat) and lon < (x2 - x1) * (lat - y1) / (y2 - y1) + x1:
            dentro = not dentro
    return dentro


def test_nessuna_zona_ha_coordinate_approssimate():
    rete = json.loads((DATA / "rete_fuorigrotta.json").read_text(encoding="utf-8"))
    for z in rete["zone"]:
        fonte = z["fonte_coordinate"]
        assert "approssimat" not in fonte, z["id"]
        assert fonte.startswith(("GTFS", "OpenStreetMap")), z["id"]


def test_area_avvisi_contiene_stadio_e_fermate_vicine():
    rete = {z["id"]: z for z in json.loads((DATA / "rete_fuorigrotta.json").read_text())["zone"]}
    poligono = list(AREA_FUORIGROTTA.poligono)
    assert 3 <= len(poligono) <= 20
    for zona in (
        "stadio",
        "piazzale_tecchio",
        "stazione_campi_flegrei",
        "stazione_mostra",
        "fermata_marino_stadio",
    ):
        assert _dentro(rete[zona]["lat"], rete[zona]["lon"], poligono), zona
    # Viale Giochi del Mediterraneo è a circa 1,1 km: fuori dall'area dello stadio.
    v = rete["viale_giochi_del_mediterraneo"]
    assert not _dentro(v["lat"], v["lon"], poligono)
