"""Fonte: scioperi dei trasporti dal Ministero delle Infrastrutture e dei Trasporti (feed RSS ufficiale).

Regole (come le altre fonti):
- dato ufficiale, mostrato com'è: orario e categoria come pubblicati, nessuna fascia garantita inventata;
- si tengono solo gli scioperi che toccano Napoli: locali in provincia di Napoli e nazionali,
  esclusi aereo, merci e gli scioperi generali che escludono i trasporti;
- scioperi identici proclamati da più sindacati (stessa data, orario e categoria) diventano uno solo;
- risposta in memoria per SCIOPERI_TTL_S secondi (predefinito 3600); se il Ministero non risponde,
  l'ultima copia salvata (data/fonti/scioperi.json) con la sua data; senza copia, nessuno sciopero.
"""

import os
import re
import threading
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import BaseModel

from ..models.contesto import StatoFonte
from ..models.scioperi import Sciopero
from ..scenario import DATA

URL = "https://scioperi.mit.gov.it/mit2/public/scioperi/rss"
NOME = "Ministero dei Trasporti (scioperi)"
COPIA = DATA / "fonti" / "scioperi.json"
ROMA = ZoneInfo("Europe/Rome")
SETTORI_ESCLUSI = {"Aereo", "Trasporto merci"}
ORARIO = re.compile(
    r"DALLE\s+(\d{1,2})[.:](\d{2})(?:\s+DEL\s+(\d{1,2})/(\d{1,2}))?\s+ALLE\s+(\d{1,2})[.:](\d{2})(?:\s+DEL\s+(\d{1,2})/(\d{1,2}))?"
)
INTERA_DEL = re.compile(r"INTERA\s+(?:PRESTAZIONE|GIORNATA)\s+DEL\s+(\d{1,2})/(\d{1,2})")

Chiamata = Callable[[str], bytes]


class _Copia(BaseModel):
    scioperi: list[Sciopero]
    aggiornato_al: str


def _chiamata_http(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=8) as risposta:
        return risposta.read()


def _campi(descrizione: str) -> dict[str, str]:
    campi = {}
    for parte in re.split(r"<br\s*/?>", descrizione):
        if ":" in parte:
            nome, valore = parte.split(":", 1)
            campi[nome.strip().lower()] = valore.strip()
    return campi


def _data(testo: str) -> datetime:
    return datetime.strptime(testo.strip(), "%d/%m/%Y").replace(tzinfo=ROMA)


def _momento(giorno: datetime, ora: str, minuti: str, gg: str | None, mm: str | None) -> datetime:
    if gg and mm:
        giorno = giorno.replace(day=int(gg), month=int(mm))
    return giorno.replace(hour=0, minute=0) + timedelta(hours=int(ora), minutes=int(minuti))


def intervallo(orario: str, inizio: datetime, fine: datetime) -> tuple[datetime, datetime]:
    """Dalle/alle come pubblicato; senza orario leggibile, le giornate intere da inizio a fine."""
    testo = orario.upper()
    m = ORARIO.search(testo)
    if not m:
        return inizio, fine + timedelta(days=1)
    da = _momento(inizio, m[1], m[2], m[3], m[4])
    a = _momento(inizio if not m[7] else fine, m[5], m[6], m[7], m[8])
    if a <= da:
        a += timedelta(days=1)
    # «…; TPL: intera prestazione del 21/11»: una parte dello sciopero dura tutto quel giorno
    for gg, mm in INTERA_DEL.findall(testo):
        a = max(a, inizio.replace(day=int(gg), month=int(mm), hour=0, minute=0) + timedelta(days=1))
    return da, a


def tocca_napoli(campi: dict[str, str]) -> bool:
    if campi.get("settore") in SETTORI_ESCLUSI:
        return False
    if "ESCLUSIONE SETTORE TRASPORTI" in campi.get("categoria interessata", "").upper():
        return False
    if campi.get("rilevanza") == "Nazionale":
        return True
    return campi.get("regione") == "Campania" and campi.get("provincia") in {"Napoli", "Tutte"}


def converti(xml: bytes) -> list[Sciopero]:
    uniti: dict[tuple[str, str, str], Sciopero] = {}
    for item in ET.fromstring(xml).iter("item"):
        titolo = item.findtext("title") or ""
        campi = _campi(item.findtext("description") or "")
        m = re.search(r"Data inizio:\s*(\d{2}/\d{2}/\d{4})", titolo)
        if not m or not tocca_napoli(campi):
            continue
        inizio_g = _data(m[1])
        fine_g = _data(campi.get("data fine", m[1]))
        orario = campi.get("modalità", campi.get("modalita", ""))
        da, a = intervallo(orario, inizio_g, fine_g)
        categoria = campi.get("categoria interessata", "")
        chiave = (da.isoformat(), a.isoformat(), categoria)
        guid = (item.findtext("guid") or "").rsplit("/", 1)[-1]
        sindacati = [campi["sindacati"]] if campi.get("sindacati") else []
        if chiave in uniti:
            s = uniti[chiave]
            s.id += f",{guid}"
            s.sindacati += [x for x in sindacati if x not in s.sindacati]
            continue
        uniti[chiave] = Sciopero(
            id=guid,
            inizio=da.isoformat(),
            fine=a.isoformat(),
            orario=orario,
            settore=campi.get("settore", ""),
            rilevanza=campi.get("rilevanza", ""),
            area=campi.get("provincia", "") if campi.get("rilevanza") == "Locale" else "Italia",
            categoria=categoria,
            sindacati=sindacati,
            proclamato_il=campi.get("data proclamazione"),
        )
    return sorted(uniti.values(), key=lambda s: s.inizio)


class FonteScioperi:
    def __init__(
        self,
        chiamata: Chiamata = _chiamata_http,
        ttl_s: int | None = None,
        copia: Path = COPIA,
        adesso: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.chiamata = chiamata
        self.ttl_s = ttl_s if ttl_s is not None else int(os.environ.get("SCIOPERI_TTL_S") or "3600")
        self.copia = copia
        self.adesso = adesso
        self._ultimo: tuple[list[Sciopero], StatoFonte] | None = None
        self._ultimo_at: datetime | None = None
        self._lock = threading.Lock()

    def leggi(self) -> tuple[list[Sciopero], StatoFonte]:
        with self._lock:
            ora = self.adesso()
            if self._ultimo and self._ultimo_at and (ora - self._ultimo_at).total_seconds() < self.ttl_s:
                return self._ultimo
            try:
                scioperi = converti(self.chiamata(URL))
            except (urllib.error.URLError, TimeoutError, ET.ParseError, ValueError, OSError) as errore:
                return self._da_copia(f"Il Ministero non ha risposto ({type(errore).__name__})")
            stato = StatoFonte(nome=NOME, disponibile=True, aggiornato_al=ora.isoformat())
            self._ultimo, self._ultimo_at = (scioperi, stato), ora
            self._salva(_Copia(scioperi=scioperi, aggiornato_al=ora.isoformat()))
            return self._ultimo

    def _salva(self, dati: _Copia) -> None:
        try:
            self.copia.parent.mkdir(parents=True, exist_ok=True)
            self.copia.write_text(dati.model_dump_json(indent=2) + "\n", encoding="utf-8")
        except OSError:
            pass  # la copia aiuta quando la rete manca, non deve fermare la risposta

    def _da_copia(self, motivo: str) -> tuple[list[Sciopero], StatoFonte]:
        if self.copia.is_file():
            try:
                salvata = _Copia.model_validate_json(self.copia.read_text(encoding="utf-8"))
            except ValueError:
                salvata = None
            if salvata is not None:
                return salvata.scioperi, StatoFonte(
                    nome=NOME,
                    disponibile=True,
                    copia=True,
                    aggiornato_al=salvata.aggiornato_al,
                    motivo=f"{motivo}: copia salvata del {salvata.aggiornato_al}",
                )
        return [], StatoFonte(nome=NOME, disponibile=False, motivo=motivo)


_fonte: FonteScioperi | None = None


def fonte() -> FonteScioperi:
    global _fonte
    if _fonte is None:
        _fonte = FonteScioperi()
    return _fonte
