"""Agente Visite: cosa visitare a Napoli in un certo momento, e come arrivarci.

Parte da luoghi reali (data/luoghi_da_visitare.json: coordinate OpenStreetMap, fermate dal GTFS ANM)
e dal calendario vero dell'agente Calendario (partite, concerti, scioperi ufficiali). Regole:
- un luogo vicino a un evento, durante l'arrivo o l'uscita del pubblico, è «da evitare ora»;
- una linea toccata da uno sciopero in corso è segnata come possibile assente, con il motivo;
- se tutte le linee vicine possono mancare, il luogo è «con disagi»: si arriva a piedi o con altri mezzi.
Nessun orario di apertura inventato: si rimanda al sito ufficiale.
"""

import json
import math
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any

from ..models import Accesso, DaVisitare, LuogoConsigliato, Momento, NapoliProssimiGiorni, ScioperoPrevisto
from ..scenario import DATA
from . import calendario

MARGINE_M = 400  # oltre il raggio della zona dell'evento, chi passa a piedi trova ancora folla
ORDINE = {"consigliato": 0, "con_disagi": 1, "da_evitare_ora": 2}


@lru_cache
def luoghi() -> list[dict[str, Any]]:
    return json.loads((DATA / "luoghi_da_visitare.json").read_text(encoding="utf-8"))["luoghi"]


def _metri(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (
        math.sin((p2 - p1) / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    )
    return 2 * 6371000 * math.asin(math.sqrt(a))


def _fino(fine: str, en: bool) -> str:
    ora = calendario._ora(datetime.fromisoformat(fine))
    if ora == "00:00":
        return "until midnight" if en else "fino a mezzanotte"
    return f"until {ora}" if en else f"fino alle {ora}"


def gestori_coinvolti(p: ScioperoPrevisto) -> set[str]:
    linee = " ".join(p.linee_coinvolte).lower()
    gestori = set()
    if (
        "anm" in linee
        or "linea 1" in linee
        or "trasporto pubblico locale" in linee
        or "tutti i mezzi" in linee
    ):
        gestori.add("ANM")
    if "trenitalia" in linee or "tutti i mezzi" in linee:
        gestori.add("Trenitalia")
    return gestori


def _in_corso(inizio: str, fine: str, quando: datetime) -> bool:
    return datetime.fromisoformat(inizio) <= quando < datetime.fromisoformat(fine)


def consigli(
    quando: datetime, calendario_oggi: NapoliProssimiGiorni, adesso: datetime | None = None
) -> DaVisitare:
    """Consigli per `quando`; i momenti proposti partono sempre da `adesso` (l'ora reale)."""
    scioperi = [p for p in calendario_oggi.scioperi if _in_corso(p.sciopero.inizio, p.sciopero.fine, quando)]
    risultato = []
    for luogo in luoghi():
        motivi, motivi_en = [], []
        for p in calendario_oggi.eventi:
            e, imp = p.evento, p.impatto
            da = datetime.fromisoformat(e.inizio) - timedelta(minutes=calendario.PRIMA_MIN)
            a = datetime.fromisoformat(e.fine) + timedelta(minutes=calendario.DOPO_MIN)
            vicino = _metri(luogo["lat"], luogo["lon"], imp.lat, imp.lon) <= imp.raggio_m + MARGINE_M
            if vicino and da <= quando < a:
                motivi.append(f"Zona affollata: {e.titolo}, fino alle {calendario._ora(a)}")
                motivi_en.append(f"Crowded area: {e.titolo}, until {calendario._ora(a)}")
        accessi = []
        for acc in luogo["accessi"]:
            colpito = next((p for p in scioperi if acc["gestore"] in gestori_coinvolti(p)), None)
            accessi.append(
                Accesso(
                    **{
                        k: acc[k]
                        for k in ("linea", "codice", "gestore", "fermata", "metri", "minuti_a_piedi")
                    },
                    disponibile=colpito is None,
                    motivo=f"Sciopero {_fino(colpito.sciopero.fine, False)}" if colpito else None,
                    motivo_en=f"Strike {_fino(colpito.sciopero.fine, True)}" if colpito else None,
                )
            )
        if motivi:
            stato = "da_evitare_ora"
        elif accessi and not any(a.disponibile for a in accessi):
            stato = "con_disagi"
            motivi.append("Le linee vicine possono mancare per sciopero: a piedi o con altri mezzi")
            motivi_en.append("Nearby lines may not run due to a strike: walk or use other transport")
        else:
            stato = "consigliato"
        risultato.append(
            LuogoConsigliato(
                **{k: luogo[k] for k in ("id", "nome", "name_en", "zona", "descrizione", "description_en")},
                lat=luogo["lat"],
                lon=luogo["lon"],
                fonte_coordinate=luogo["fonte_coordinate"],
                accessi=accessi,
                stato=stato,
                motivi=motivi,
                motivi_en=motivi_en,
            )
        )
    risultato.sort(key=lambda luogo: ORDINE[luogo.stato])
    return DaVisitare(
        quando=quando.astimezone(calendario.ROMA).isoformat(),
        luoghi=risultato,
        momenti=momenti(adesso or quando, calendario_oggi),
        fonti=calendario_oggi.fonti,
    )


def momenti(adesso: datetime, cal: NapoliProssimiGiorni) -> list[Momento]:
    """Adesso, l'inizio di ogni sciopero e la fascia d'arrivo di ogni evento dei prossimi giorni."""
    lista = [
        Momento(quando=adesso.astimezone(calendario.ROMA).isoformat(), etichetta="Adesso", label_en="Now")
    ]
    for p in cal.scioperi:
        t = max(datetime.fromisoformat(p.sciopero.inizio), adesso)
        giorno = t.astimezone(calendario.ROMA).strftime("%d/%m %H:%M")
        lista.append(
            Momento(quando=t.isoformat(), etichetta=f"{giorno} · sciopero", label_en=f"{giorno} · strike")
        )
    for p in cal.eventi:
        t = max(datetime.fromisoformat(p.evento.inizio) - timedelta(minutes=30), adesso)
        giorno = t.astimezone(calendario.ROMA).strftime("%d/%m %H:%M")
        lista.append(
            Momento(
                quando=t.isoformat(),
                etichetta=f"{giorno} · {p.evento.titolo}",
                label_en=f"{giorno} · {p.evento.titolo}",
            )
        )
    visti, unici = set(), []
    for m in sorted(lista, key=lambda m: m.quando):
        if m.quando[:16] not in visti:
            visti.add(m.quando[:16])
            unici.append(m)
    return unici[:8]
