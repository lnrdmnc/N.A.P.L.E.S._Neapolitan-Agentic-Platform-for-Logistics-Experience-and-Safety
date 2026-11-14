"""Fonte: meteo reale a Fuorigrotta (stadio Maradona), da Open-Meteo.

Regole (come le altre fonti):
- solo dati reali, `simulato=False`, mai mescolati all'allerta meteo simulata dello scenario;
- servizio pubblico senza chiave: risposta tenuta in memoria per METEO_TTL_S secondi (predefinito 600);
- se Open-Meteo non risponde, si mostra l'ultima copia salvata (data/fonti/meteo.json) con la sua data;
  senza copia, `disponibile=False` e nessun dato inventato.
"""

import json
import os
import threading
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from ..models.contesto import Meteo, StatoFonte
from ..scenario import DATA

URL = "https://api.open-meteo.com/v1/forecast"
STADIO = {"latitude": 40.8279, "longitude": 14.1930}
COPIA = DATA / "fonti" / "meteo.json"

Chiamata = Callable[[str], dict]


class _Copia(BaseModel):
    meteo: Meteo
    aggiornato_al: str


def _chiamata_http(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=8) as risposta:
        return json.loads(risposta.read())


def url_meteo() -> str:
    query = urllib.parse.urlencode(
        {
            **STADIO,
            "current": "temperature_2m,precipitation,weather_code,wind_speed_10m",
            "timezone": "Europe/Rome",
        }
    )
    return f"{URL}?{query}"


def converti(risposta: dict) -> Meteo:
    c = risposta["current"]
    return Meteo(
        tempo=c["time"],
        temperatura_c=float(c["temperature_2m"]),
        precipitazione_mm=float(c["precipitation"]),
        vento_kmh=float(c["wind_speed_10m"]),
        codice_meteo=int(c["weather_code"]),
    )


class FonteMeteo:
    def __init__(
        self,
        chiamata: Chiamata = _chiamata_http,
        ttl_s: int | None = None,
        copia: Path = COPIA,
        adesso: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.chiamata = chiamata
        self.ttl_s = ttl_s if ttl_s is not None else int(os.environ.get("METEO_TTL_S") or "600")
        self.copia = copia
        self.adesso = adesso
        self._ultimo: tuple[Meteo | None, StatoFonte] | None = None
        self._ultimo_at: datetime | None = None
        self._lock = threading.Lock()

    def leggi(self) -> tuple[Meteo | None, StatoFonte]:
        with self._lock:
            ora = self.adesso()
            if self._ultimo and self._ultimo_at and (ora - self._ultimo_at).total_seconds() < self.ttl_s:
                return self._ultimo
            try:
                meteo = converti(self.chiamata(url_meteo()))
            except (urllib.error.URLError, TimeoutError, KeyError, ValueError, OSError) as errore:
                return self._da_copia(f"Open-Meteo non ha risposto ({type(errore).__name__})")
            stato = StatoFonte(nome="Open-Meteo", disponibile=True, aggiornato_al=ora.isoformat())
            self._ultimo, self._ultimo_at = (meteo, stato), ora
            self._salva(_Copia(meteo=meteo, aggiornato_al=ora.isoformat()))
            return self._ultimo

    def _salva(self, dati: _Copia) -> None:
        try:
            self.copia.parent.mkdir(parents=True, exist_ok=True)
            self.copia.write_text(dati.model_dump_json(indent=2) + "\n", encoding="utf-8")
        except OSError:
            pass

    def _da_copia(self, motivo: str) -> tuple[Meteo | None, StatoFonte]:
        if self.copia.is_file():
            try:
                salvata = _Copia.model_validate_json(self.copia.read_text(encoding="utf-8"))
            except ValueError:
                salvata = None
            if salvata is not None:
                return salvata.meteo, StatoFonte(
                    nome="Open-Meteo",
                    disponibile=True,
                    copia=True,
                    aggiornato_al=salvata.aggiornato_al,
                    motivo=f"{motivo}: copia salvata del {salvata.aggiornato_al}",
                )
        return None, StatoFonte(nome="Open-Meteo", disponibile=False, motivo=motivo)


_fonte: FonteMeteo | None = None


def fonte() -> FonteMeteo:
    global _fonte
    if _fonte is None:
        _fonte = FonteMeteo()
    return _fonte
