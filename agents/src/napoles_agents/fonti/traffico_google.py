"""Fonte: tempi di percorrenza con traffico reale, da Google Routes API (computeRoutes, TRAFFIC_AWARE).

Regole:
- solo dati reali: senza chiave o senza risposta, `disponibile=False` e nessun numero inventato;
- quota gratuita (Compute Routes Pro, 5.000 richieste al mese): risposte tenute in memoria per
  TRAFFICO_TTL_S secondi e al massimo TRAFFICO_MAX_CHIAMATE_GIORNO chiamate al giorno; oltre,
  si mostrano gli ultimi dati reali con l'ora della rilevazione.
"""

import json
import os
import threading
import urllib.error
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime

from ..models.traffico import LivelloTraffico, PercorsoTraffico, Traffico
from ..scenario import DATA

URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
FIELD_MASK = "routes.duration,routes.staticDuration,routes.distanceMeters,routes.polyline.encodedPolyline"

# Soglie sul rapporto durata con traffico / senza traffico (docs/IPOTESI.md)
SOGLIA_RALLENTATO = 1.15
SOGLIA_CONGESTIONATO = 1.5

Chiamata = Callable[[dict, str], dict]  # (corpo della richiesta, chiave) -> risposta JSON


def percorsi() -> list[dict]:
    return json.loads((DATA / "percorsi_traffico.json").read_text(encoding="utf-8"))["percorsi"]


def livello(durata_s: float, statica_s: float) -> LivelloTraffico:
    rapporto = durata_s / statica_s if statica_s > 0 else 1.0
    if rapporto >= SOGLIA_CONGESTIONATO:
        return LivelloTraffico.CONGESTIONATO
    if rapporto >= SOGLIA_RALLENTATO:
        return LivelloTraffico.RALLENTATO
    return LivelloTraffico.SCORREVOLE


def _secondi(valore: str | None) -> float:
    return float(valore.rstrip("s")) if valore else 0.0


def _chiamata_http(corpo: dict, chiave: str) -> dict:
    richiesta = urllib.request.Request(
        URL,
        data=json.dumps(corpo).encode(),
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": chiave,
            "X-Goog-FieldMask": FIELD_MASK,
        },
        method="POST",
    )
    with urllib.request.urlopen(richiesta, timeout=8) as risposta:
        return json.loads(risposta.read())


def _punto(latlon: list[float]) -> dict:
    return {"location": {"latLng": {"latitude": latlon[0], "longitude": latlon[1]}}}


def _vuoto(motivo: str) -> Traffico:
    elenco = [PercorsoTraffico(id=p["id"], nome=p["nome"], da=p["da"], a=p["a"]) for p in percorsi()]
    return Traffico(percorsi=elenco, disponibile=False, motivo=motivo)


class FonteTraffico:
    def __init__(
        self,
        chiave: str | None = None,
        chiamata: Chiamata = _chiamata_http,
        ttl_s: int | None = None,
        max_chiamate_giorno: int | None = None,
        adesso: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.chiave = chiave if chiave is not None else os.environ.get("MAPS_API_KEY", "")
        self.chiamata = chiamata
        self.ttl_s = ttl_s if ttl_s is not None else int(os.environ.get("TRAFFICO_TTL_S") or "600")
        self.max_giorno = (
            max_chiamate_giorno
            if max_chiamate_giorno is not None
            else int(os.environ.get("TRAFFICO_MAX_CHIAMATE_GIORNO") or "150")
        )
        self.adesso = adesso
        self._ultimo: Traffico | None = None
        self._ultimo_at: datetime | None = None
        self._giorno = ""
        self._chiamate_oggi = 0
        self._lock = threading.Lock()

    def leggi(self) -> Traffico:
        if not self.chiave:
            return _vuoto("Chiave MAPS_API_KEY non configurata: traffico reale non disponibile")
        with self._lock:
            ora = self.adesso()
            if self._ultimo_at and (ora - self._ultimo_at).total_seconds() < self.ttl_s:
                return self._ultimo  # type: ignore[return-value]
            giorno = ora.date().isoformat()
            if giorno != self._giorno:
                self._giorno, self._chiamate_oggi = giorno, 0
            elenco = percorsi()
            if self._chiamate_oggi + len(elenco) > self.max_giorno:
                return self._non_fresco("Quota giornaliera di richieste raggiunta")
            try:
                risultati = [self._percorso(p) for p in elenco]
            except (urllib.error.URLError, TimeoutError, KeyError, ValueError, OSError) as errore:
                return self._non_fresco(f"Google Routes API non ha risposto ({type(errore).__name__})")
            finally:
                self._chiamate_oggi += len(elenco)
            self._ultimo = Traffico(percorsi=risultati, disponibile=True, rilevato_alle=ora.isoformat())
            self._ultimo_at = ora
            return self._ultimo

    def _non_fresco(self, motivo: str) -> Traffico:
        if self._ultimo is None:
            return _vuoto(motivo)
        return self._ultimo.model_copy(update={"motivo": f"{motivo}: dati reali dell'ultima rilevazione"})

    def _percorso(self, p: dict) -> PercorsoTraffico:
        corpo = {
            "origin": _punto(p["origine"]),
            "destination": _punto(p["destinazione"]),
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE",
            "languageCode": "it-IT",
            "units": "METRIC",
        }
        route = self.chiamata(corpo, self.chiave)["routes"][0]
        durata = _secondi(route.get("duration"))
        statica = _secondi(route.get("staticDuration")) or durata
        return PercorsoTraffico(
            id=p["id"],
            nome=p["nome"],
            da=p["da"],
            a=p["a"],
            durata_min=round(durata / 60, 1),
            durata_senza_traffico_min=round(statica / 60, 1),
            ritardo_min=round(max(durata - statica, 0) / 60, 1),
            distanza_km=round(route.get("distanceMeters", 0) / 1000, 1),
            livello=livello(durata, statica),
            polilinea=route.get("polyline", {}).get("encodedPolyline"),
        )


_fonte: FonteTraffico | None = None


def fonte() -> FonteTraffico:
    global _fonte
    if _fonte is None:
        _fonte = FonteTraffico()
    return _fonte
