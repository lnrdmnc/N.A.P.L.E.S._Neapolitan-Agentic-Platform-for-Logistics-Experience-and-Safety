"""Fonte: ultimi terremoti reali ai Campi Flegrei e al Vesuvio, dal servizio FDSN dell'INGV.

Regole (come le altre fonti):
- solo dati reali e mai mescolati agli eventi simulati dello scenario (`simulato=False`);
- servizio pubblico senza chiave: risposta tenuta in memoria per INGV_TTL_S secondi (predefinito 120);
- se l'INGV non risponde, si mostra l'ultima copia salvata (data/fonti/ingv.json) con la sua data;
  senza copia, `disponibile=False` e nessun evento inventato.
"""

import json
import os
import threading
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path

from pydantic import BaseModel

from ..models.contesto import EventoSismicoReale, StatoFonte
from ..scenario import DATA

URL = "https://webservices.ingv.it/fdsnws/event/1/query"
AREE = {
    "Campi Flegrei": {"lat": 40.827, "lon": 14.139, "maxradiuskm": 15},
    "Vesuvio": {"lat": 40.821, "lon": 14.426, "maxradiuskm": 10},
}
GIORNI = 7
PER_AREA = 5
COPIA = DATA / "fonti" / "ingv.json"

Chiamata = Callable[[str], dict]


class _Copia(BaseModel):
    eventi: list[EventoSismicoReale]
    aggiornato_al: str


def _chiamata_http(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=8) as risposta:
        return json.loads(risposta.read())


def url_area(area: str, oggi: datetime) -> str:
    query = urllib.parse.urlencode(
        {
            **AREE[area],
            "starttime": (oggi - timedelta(days=GIORNI)).strftime("%Y-%m-%dT%H:%M:%S"),
            "format": "geojson",
            "orderby": "time",
            "limit": PER_AREA,
        }
    )
    return f"{URL}?{query}"


def converti(risposta: dict, area: str) -> list[EventoSismicoReale]:
    eventi = []
    for f in risposta.get("features", []):
        p, (lon, lat, profondita) = f["properties"], f["geometry"]["coordinates"][:3]
        eventi.append(
            EventoSismicoReale(
                id=str(p["eventId"]),
                tempo=p["time"],
                magnitudo=float(p["mag"]),
                tipo_magnitudo=p.get("magType", ""),
                luogo=p.get("place") or area,
                lat=float(lat),
                lon=float(lon),
                profondita_km=float(profondita),
            )
        )
    return eventi


class FonteINGV:
    def __init__(
        self,
        chiamata: Chiamata = _chiamata_http,
        ttl_s: int | None = None,
        copia: Path = COPIA,
        adesso: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.chiamata = chiamata
        self.ttl_s = ttl_s if ttl_s is not None else int(os.environ.get("INGV_TTL_S") or "120")
        self.copia = copia
        self.adesso = adesso
        self._ultimo: tuple[list[EventoSismicoReale], StatoFonte] | None = None
        self._ultimo_at: datetime | None = None
        self._lock = threading.Lock()

    def leggi(self) -> tuple[list[EventoSismicoReale], StatoFonte]:
        with self._lock:
            ora = self.adesso()
            if self._ultimo and self._ultimo_at and (ora - self._ultimo_at).total_seconds() < self.ttl_s:
                return self._ultimo
            try:
                eventi = [e for area in AREE for e in converti(self.chiamata(url_area(area, ora)), area)]
            except (urllib.error.URLError, TimeoutError, KeyError, ValueError, OSError) as errore:
                return self._da_copia(f"INGV non ha risposto ({type(errore).__name__})")
            eventi.sort(key=lambda e: e.tempo, reverse=True)
            stato = StatoFonte(nome="INGV FDSN", disponibile=True, aggiornato_al=ora.isoformat())
            self._ultimo, self._ultimo_at = (eventi, stato), ora
            self._salva(_Copia(eventi=eventi, aggiornato_al=ora.isoformat()))
            return self._ultimo

    def _salva(self, dati: _Copia) -> None:
        try:
            self.copia.parent.mkdir(parents=True, exist_ok=True)
            self.copia.write_text(dati.model_dump_json(indent=2) + "\n", encoding="utf-8")
        except OSError:
            pass  # la copia aiuta quando la rete manca, non deve fermare la risposta

    def _da_copia(self, motivo: str) -> tuple[list[EventoSismicoReale], StatoFonte]:
        if self.copia.is_file():
            try:
                salvata = _Copia.model_validate_json(self.copia.read_text(encoding="utf-8"))
            except ValueError:
                salvata = None
            if salvata is not None:
                return salvata.eventi, StatoFonte(
                    nome="INGV FDSN",
                    disponibile=True,
                    copia=True,
                    aggiornato_al=salvata.aggiornato_al,
                    motivo=f"{motivo}: copia salvata del {salvata.aggiornato_al}",
                )
        return [], StatoFonte(nome="INGV FDSN", disponibile=False, motivo=motivo)


_fonte: FonteINGV | None = None


def fonte() -> FonteINGV:
    global _fonte
    if _fonte is None:
        _fonte = FonteINGV()
    return _fonte
