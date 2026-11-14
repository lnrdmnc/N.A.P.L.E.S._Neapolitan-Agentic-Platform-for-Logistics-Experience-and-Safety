"""Agente Calendario: Napoli oggi e nei prossimi giorni («la città che Ci pensa»).

Mette insieme gli eventi previsti, capisce quali zone e quali fermate saranno toccate e quando,
e propone alternative prima che il problema si presenti.

Fonti, sempre dichiarate:
- partite in casa del Napoli al Maradona: reali, da football-data.org (fonti/partite_football.py);
- concerti, cortei, manifestazioni: elenco curato dal team (data/eventi_napoli.json); gli eventi
  con `esempio: true` sono dimostrativi e lo dicono a schermo.

Regole d'impatto (ipotesi, docs/IPOTESI.md): affollamento nei 90 minuti prima dell'inizio e nei
60 dopo la fine; livello alto da 20.000 persone attese, medio da 5.000.
"""

import json
import re
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any
from zoneinfo import ZoneInfo

from ..fonti.partite_football import fonte as fonte_partite
from ..models import Affidabilita
from ..models.calendario import EventoCitta, EventoPrevisto, Finestra, ImpattoEvento, NapoliProssimiGiorni
from ..models.contesto import StatoFonte
from ..scenario import DATA

ROMA = ZoneInfo("Europe/Rome")
PRIMA_MIN = 90
DOPO_MIN = 60
DURATA_PARTITA_MIN = 115
PERSONE_PARTITA = 50000  # stima: ordine di grandezza della capienza, non il numero di biglietti
SOGLIA_ALTO = 20000
SOGLIA_MEDIO = 5000


@lru_cache
def _carica(nome: str) -> dict[str, Any]:
    return json.loads((DATA / f"{nome}.json").read_text(encoding="utf-8"))


def luoghi() -> dict[str, dict[str, Any]]:
    return {luogo["id"]: luogo for luogo in _carica("luoghi_napoli")["luoghi"]}


def _senza_codici(fermata: str) -> str:
    """Toglie il codice GTFS tra parentesi: serve al team, non al cittadino."""
    return re.sub(r"\s*\(\d+\)", "", fermata)


def _ora(dt: datetime) -> str:
    return dt.astimezone(ROMA).strftime("%H:%M")


def _evento(
    id_: str,
    titolo: str,
    tipo: str,
    luogo_id: str,
    inizio: datetime,
    durata_min: int,
    persone: int | None,
    fonte: str,
    affidabilita: Affidabilita,
    esempio: bool,
) -> EventoCitta:
    luogo = luoghi()[luogo_id]
    return EventoCitta(
        id=id_,
        titolo=titolo,
        tipo=tipo,
        luogo_id=luogo_id,
        luogo=luogo["nome"],
        quartiere=luogo["quartiere"],
        inizio=inizio.astimezone(ROMA).isoformat(),
        fine=(inizio + timedelta(minutes=durata_min)).astimezone(ROMA).isoformat(),
        persone_attese=persone,
        fonte=fonte,
        affidabilita=affidabilita,
        esempio=esempio,
    )


def impatto(evento: EventoCitta) -> ImpattoEvento:
    luogo = luoghi()[evento.luogo_id]
    inizio = datetime.fromisoformat(evento.inizio)
    fine = datetime.fromisoformat(evento.fine)
    persone = evento.persone_attese or 0
    livello = "alto" if persone >= SOGLIA_ALTO else "medio" if persone >= SOGLIA_MEDIO else "basso"
    arrivo = Finestra(
        da=_ora(inizio - timedelta(minutes=PRIMA_MIN)), a=_ora(inizio), motivo="arrivo del pubblico"
    )
    uscita = Finestra(da=_ora(fine), a=_ora(fine + timedelta(minutes=DOPO_MIN)), motivo="uscita del pubblico")
    da_evitare = [_senza_codici(f) for f in luogo["da_evitare"]]
    alternative_lista = [_senza_codici(f) for f in luogo["alternative"]]
    evitare = ", ".join(da_evitare)
    alternative = ", ".join(alternative_lista)
    return ImpattoEvento(
        livello=livello,
        zona=luogo["zona"],
        lat=luogo["lat"],
        lon=luogo["lon"],
        raggio_m=luogo["raggio_m"],
        finestre=[arrivo, uscita],
        da_evitare=da_evitare,
        alternative=alternative_lista,
        consiglio=(
            f"Tra le {arrivo.da} e le {arrivo.a} e tra le {uscita.da} e le {uscita.a} la zona "
            f"{luogo['zona']} sarà affollata: se non vai all'evento evita {evitare}. "
            f"Usa invece {alternative}."
        ),
    )


def _giorno(inizio: datetime, oggi: datetime) -> str:
    giorni = (inizio.astimezone(ROMA).date() - oggi.astimezone(ROMA).date()).days
    if giorni == 0:
        return "oggi"
    if giorni == 1:
        return "domani"
    return inizio.astimezone(ROMA).strftime("%d/%m")


def prossimi_giorni(oggi: datetime, giorni: int = 10) -> NapoliProssimiGiorni:
    limite = oggi + timedelta(days=giorni)
    eventi: list[EventoCitta] = []

    partite = fonte_partite().leggi()
    for p in partite.partite:
        inizio = datetime.fromisoformat(p.data_ora)
        eventi.append(
            _evento(
                f"partita_{p.id}",
                f"{p.casa}–{p.ospite} · {p.competizione}",
                "partita",
                "maradona",
                inizio,
                DURATA_PARTITA_MIN,
                PERSONE_PARTITA,
                "football-data.org (calendario ufficiale)",
                Affidabilita.UFFICIALE,
                False,
            )
        )
    stato_partite = StatoFonte(
        nome="football-data.org",
        disponibile=partite.disponibile,
        aggiornato_al=partite.aggiornato_al,
        copia=partite.copia,
        motivo=partite.motivo,
    )

    curati = _carica("eventi_napoli")["eventi"]
    for e in curati:
        eventi.append(
            _evento(
                e["id"],
                e["titolo"],
                e["tipo"],
                e["luogo"],
                datetime.fromisoformat(e["inizio"]),
                e["durata_min"],
                e.get("persone_attese"),
                e["fonte"],
                Affidabilita.NON_VERIFICATA if e.get("esempio") else Affidabilita.STIMATA,
                bool(e.get("esempio")),
            )
        )
    esempi = sum(1 for e in curati if e.get("esempio"))
    stato_curati = StatoFonte(
        nome="Elenco curato dal team",
        disponibile=True,
        motivo=f"{esempi} eventi di esempio, da sostituire con eventi verificati" if esempi else None,
    )

    previsti = [
        EventoPrevisto(evento=e, impatto=impatto(e), giorno=_giorno(datetime.fromisoformat(e.inizio), oggi))
        for e in eventi
        if oggi <= datetime.fromisoformat(e.fine) and datetime.fromisoformat(e.inizio) <= limite
    ]
    previsti.sort(key=lambda p: p.evento.inizio)
    return NapoliProssimiGiorni(
        eventi=previsti,
        giorni=giorni,
        generato_al=oggi.astimezone(ROMA).isoformat(),
        fonti=[stato_partite, stato_curati],
    )
