"""Fonte: partite in casa del Napoli allo stadio Maradona, da football-data.org (API v4).

Regole:
- solo dati reali: senza chiave e senza copia salvata, `disponibile=False` e nessuna partita inventata;
- piano gratuito con limite di richieste al minuto: risposta tenuta in memoria per PARTITE_TTL_S
  secondi (predefinito 6 ore, il calendario cambia di rado);
- demo offline: ogni risposta riuscita si salva in data/fonti/partite_maradona.json e, se la fonte
  non risponde, si mostra quella copia con la sua data.
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

from ..models.partite import Partita, Partite
from ..scenario import DATA

URL = "https://api.football-data.org/v4/teams/{squadra}/matches"
SQUADRA_NAPOLI = 113  # id dell'SSC Napoli su football-data.org
GIORNI_AVANTI = 60
COPIA = DATA / "fonti" / "partite_maradona.json"

Chiamata = Callable[[str, str], dict]  # (url, chiave) -> risposta JSON


def _chiamata_http(url: str, chiave: str) -> dict:
    richiesta = urllib.request.Request(url, headers={"X-Auth-Token": chiave})
    with urllib.request.urlopen(richiesta, timeout=8) as risposta:
        return json.loads(risposta.read())


def url_partite(oggi: datetime, squadra: int = SQUADRA_NAPOLI) -> str:
    query = urllib.parse.urlencode(
        {
            "venue": "HOME",
            "dateFrom": oggi.date().isoformat(),
            "dateTo": (oggi + timedelta(days=GIORNI_AVANTI)).date().isoformat(),
        }
    )
    return f"{URL.format(squadra=squadra)}?{query}"


def al_maradona(partita: dict) -> bool:
    """In casa del Napoli; se la fonte indica lo stadio, deve essere il Maradona."""
    stadio = partita.get("venue")
    return not stadio or "maradona" in stadio.lower()


def converti(risposta: dict) -> list[Partita]:
    partite = [
        Partita(
            id=m["id"],
            data_ora=m["utcDate"],
            casa=m["homeTeam"].get("shortName") or m["homeTeam"]["name"],
            ospite=m["awayTeam"].get("shortName") or m["awayTeam"]["name"],
            competizione=m.get("competition", {}).get("name", ""),
            stato=m.get("status", ""),
            stadio=m.get("venue"),
        )
        for m in risposta.get("matches", [])
        if al_maradona(m)
    ]
    return sorted(partite, key=lambda p: p.data_ora)


class FontePartite:
    def __init__(
        self,
        chiave: str | None = None,
        chiamata: Chiamata = _chiamata_http,
        ttl_s: int | None = None,
        copia: Path = COPIA,
        adesso: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.chiave = chiave if chiave is not None else os.environ.get("FOOTBALL_DATA_API_KEY", "")
        self.chiamata = chiamata
        self.ttl_s = ttl_s if ttl_s is not None else int(os.environ.get("PARTITE_TTL_S") or "21600")
        self.copia = copia
        self.adesso = adesso
        self._ultimo: Partite | None = None
        self._ultimo_at: datetime | None = None
        self._lock = threading.Lock()

    def leggi(self) -> Partite:
        with self._lock:
            ora = self.adesso()
            if self._ultimo_at and (ora - self._ultimo_at).total_seconds() < self.ttl_s:
                return self._ultimo  # type: ignore[return-value]
            if not self.chiave:
                return self._da_copia("Chiave FOOTBALL_DATA_API_KEY non configurata")
            try:
                partite = converti(self.chiamata(url_partite(ora), self.chiave))
            except (urllib.error.URLError, TimeoutError, KeyError, ValueError, OSError) as errore:
                return self._da_copia(f"football-data.org non ha risposto ({type(errore).__name__})")
            self._ultimo = Partite(partite=partite, disponibile=True, aggiornato_al=ora.isoformat())
            self._ultimo_at = ora
            self._salva(self._ultimo)
            return self._ultimo

    def _salva(self, dati: Partite) -> None:
        try:
            self.copia.parent.mkdir(parents=True, exist_ok=True)
            self.copia.write_text(dati.model_dump_json(indent=2) + "\n", encoding="utf-8")
        except OSError:
            pass  # la copia è un aiuto per l'offline, non deve fermare la risposta

    def _da_copia(self, motivo: str) -> Partite:
        if self.copia.is_file():
            try:
                salvata = Partite.model_validate_json(self.copia.read_text(encoding="utf-8"))
            except ValueError:
                salvata = None
            if salvata is not None:
                return salvata.model_copy(
                    update={"copia": True, "motivo": f"{motivo}: copia salvata del {salvata.aggiornato_al}"}
                )
        return Partite(partite=[], disponibile=False, motivo=motivo)


_fonte: FontePartite | None = None


def fonte() -> FontePartite:
    global _fonte
    if _fonte is None:
        _fonte = FontePartite()
    return _fonte
