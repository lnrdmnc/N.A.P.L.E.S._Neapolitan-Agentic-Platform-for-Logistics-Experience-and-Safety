"""Fonte: livello di allerta vulcanica ufficiale di Campi Flegrei e Vesuvio.

Lo dichiara il Dipartimento della Protezione Civile. La sua «Mappa livelli di allerta vulcani in
Italia» legge un file GeoJSON pubblico sul repository GitHub del Dipartimento (pcm-dpc/DPC-Mappe):
leggiamo lo stesso file, senza chiave.

Regole (come le altre fonti):
- il livello si mostra così com'è, con la fonte e l'ora della lettura; nessuna interpretazione;
- risposta tenuta in memoria per VULCANI_TTL_S secondi (predefinito 3600: il livello cambia di rado);
- se la fonte non risponde si usa l'ultima copia salvata (data/fonti/vulcani.json) con la sua data;
- senza copia, il livello verificato a mano dal team sulla fonte, con la data della verifica
  (data/livelli_vulcanici.json); se manca anche quello, `disponibile=False` e nessun livello inventato.
"""

import json
import os
import re
import threading
import urllib.error
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from ..models.contesto import LivelloVulcanico, StatoFonte
from ..scenario import DATA

URL = (
    "https://raw.githubusercontent.com/pcm-dpc/DPC-Mappe/refs/heads/master/"
    "rischi/vulcani-livelli-allerte/vulcani_liv_allerta_maplite.geojson"
)
PAGINA = "https://mappe.protezionecivile.gov.it/it/mappe-e-dashboard-rischi/mappa-livelli-di-allerta-vulcani-italia/"
NOME = "Protezione Civile (livelli di allerta vulcanica)"
AREE = ("Campi Flegrei", "Vesuvio")
COPIA = DATA / "fonti" / "vulcani.json"
VERIFICATI_A_MANO = DATA / "livelli_vulcanici.json"

Chiamata = Callable[[str], dict]


class _Copia(BaseModel):
    livelli: list[LivelloVulcanico]
    aggiornato_al: str


def _chiamata_http(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=8) as risposta:
        return json.loads(risposta.read())


def _testo(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html).strip()


def converti(risposta: dict, letto_il: str) -> list[LivelloVulcanico]:
    """Solo le aree che ci servono, nell'ordine di AREE. Un'area assente non viene inventata."""
    trovati: dict[str, LivelloVulcanico] = {}
    for f in risposta["features"]:
        p = f["properties"]
        area = _testo(p["Vulcano"])
        if area in AREE:
            trovati[area] = LivelloVulcanico(
                area=area,
                livello=str(p["livello_allerta"]).strip().lower(),
                fonte="Dipartimento della Protezione Civile, mappa dei livelli di allerta",
                url=PAGINA,
                verificato_il=letto_il,
            )
    if not trovati:
        raise ValueError("nessuna delle aree attese nella risposta")
    return [trovati[a] for a in AREE if a in trovati]


class FonteVulcani:
    def __init__(
        self,
        chiamata: Chiamata = _chiamata_http,
        ttl_s: int | None = None,
        copia: Path = COPIA,
        a_mano: Path = VERIFICATI_A_MANO,
        adesso: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.chiamata = chiamata
        self.ttl_s = ttl_s if ttl_s is not None else int(os.environ.get("VULCANI_TTL_S") or "3600")
        self.copia = copia
        self.a_mano = a_mano
        self.adesso = adesso
        self._ultimo: tuple[list[LivelloVulcanico], StatoFonte] | None = None
        self._ultimo_at: datetime | None = None
        self._lock = threading.Lock()

    def leggi(self) -> tuple[list[LivelloVulcanico], StatoFonte]:
        with self._lock:
            ora = self.adesso()
            if self._ultimo and self._ultimo_at and (ora - self._ultimo_at).total_seconds() < self.ttl_s:
                return self._ultimo
            try:
                livelli = converti(self.chiamata(URL), ora.isoformat())
            except (urllib.error.URLError, TimeoutError, KeyError, ValueError, TypeError, OSError) as errore:
                return self._da_copia(f"Protezione Civile non ha risposto ({type(errore).__name__})")
            stato = StatoFonte(nome=NOME, disponibile=True, aggiornato_al=ora.isoformat())
            self._ultimo, self._ultimo_at = (livelli, stato), ora
            self._salva(_Copia(livelli=livelli, aggiornato_al=ora.isoformat()))
            return self._ultimo

    def _salva(self, dati: _Copia) -> None:
        try:
            self.copia.parent.mkdir(parents=True, exist_ok=True)
            self.copia.write_text(dati.model_dump_json(indent=2) + "\n", encoding="utf-8")
        except OSError:
            pass  # la copia aiuta quando la rete manca, non deve fermare la risposta

    def _da_copia(self, motivo: str) -> tuple[list[LivelloVulcanico], StatoFonte]:
        if self.copia.is_file():
            try:
                salvata = _Copia.model_validate_json(self.copia.read_text(encoding="utf-8"))
            except ValueError:
                salvata = None
            if salvata is not None:
                return salvata.livelli, StatoFonte(
                    nome=NOME,
                    disponibile=True,
                    copia=True,
                    aggiornato_al=salvata.aggiornato_al,
                    motivo=f"{motivo}: copia salvata del {salvata.aggiornato_al}",
                )
        if self.a_mano.is_file():
            try:
                verificati = json.loads(self.a_mano.read_text(encoding="utf-8"))["livelli"]
                livelli = [LivelloVulcanico(**v) for v in verificati]
            except (ValueError, KeyError, TypeError):
                livelli = []
            if livelli:
                data = livelli[0].verificato_il
                return livelli, StatoFonte(
                    nome=NOME,
                    disponibile=True,
                    copia=True,
                    aggiornato_al=data,
                    motivo=f"{motivo}: livello verificato a mano il {data}",
                )
        return [], StatoFonte(nome=NOME, disponibile=False, motivo=motivo)


_fonte: FonteVulcani | None = None


def fonte() -> FonteVulcani:
    global _fonte
    if _fonte is None:
        _fonte = FonteVulcani()
    return _fonte
