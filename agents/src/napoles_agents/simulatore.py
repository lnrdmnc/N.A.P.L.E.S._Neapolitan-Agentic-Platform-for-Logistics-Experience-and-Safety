"""Simulatore a zone di Fuorigrotta (compito S0). Funzione pura e deterministica.

A passi di un minuto le persone escono dallo stadio, scelgono un modo per allontanarsi
(a piedi, Linea 2, Cumana, bus, navette) e si spostano nella zona di quel modo, che le
smaltisce alla capacità del mezzo. Chi non sa che una linea è sospesa va comunque alla
stazione e aspetta lì finché non viene informato; poi ripiega su navette o a piedi.

- Le persone si conservano: dentro lo stadio + nelle zone + arrivate = totale, a ogni minuto.
- Una zona oltre la propria capienza ha una coda (`in_coda`).
- Stessa entrata, stessa uscita: niente numeri casuali.

Parametri: scenario (linee, capacità, ondate, eventi) e rete (zone, quote modali), tutti
dichiarati in docs/IPOTESI.md. Le misure (ondate, navette, informazione) arrivano da fuori:
il compito B1 le ricava dai piani approvati nella sessione.
"""

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Literal

from . import scenario as sc
from .models import PassoSimulazione, SerieSimulazione, StatoZona, TipoEvento
from .scenario import DATA

NomeScenario = Literal["sessione", "con_coordinamento", "senza_coordinamento"]


@dataclass(frozen=True)
class Misure:
    """Cosa è attivo nella città. Ogni campo è una decisione o un'informazione."""

    ondate: bool = False
    navette_dal_t: int | None = None
    navette_zona: str = "piazzale_tecchio"
    informati_dal_t: int | None = None
    fattore_piedi: float = 1.0
    etichette: tuple[str, ...] = field(default_factory=tuple)


@lru_cache
def carica_rete(nome: str = "rete_fuorigrotta") -> dict[str, Any]:
    import json

    return json.loads((DATA / f"{nome}.json").read_text(encoding="utf-8"))


def ripartisci(n: int, pesi: dict[str, float]) -> dict[str, int]:
    """Divide n persone secondo i pesi, con interi che sommano esattamente a n."""
    totale = sum(pesi.values())
    if n <= 0 or totale <= 0:
        return dict.fromkeys(pesi, 0)
    esatti = {k: n * p / totale for k, p in pesi.items()}
    interi = {k: int(v) for k, v in esatti.items()}
    resto = n - sum(interi.values())
    for k in sorted(esatti, key=lambda k: (-(esatti[k] - interi[k]), k))[:resto]:
        interi[k] += 1
    return interi


def misure_da_scenario(scenario: dict[str, Any], coordinato: bool) -> Misure:
    """Le misure dei due casi del confronto, dagli stessi parametri di simulazione.py."""
    sim = scenario["simulazione"]
    navette = scenario["navette"]
    fine = scenario["fine_partita_t_min"]
    critico = min(e.t_min for e in sc.eventi(scenario) if e.tipo == TipoEvento.SOSPENSIONE_LINEA)
    if coordinato:
        return Misure(
            ondate=True,
            navette_dal_t=critico + sim["con_coordinamento_minuti_decisione"] + navette["minuti_attivazione"],
            navette_zona=navette["punto_carico_alternativo"],
            informati_dal_t=critico + sim["con_coordinamento_minuti_informazione"],
            fattore_piedi=sim["con_coordinamento_fattore_percorsi_piedi"],
            etichette=("ondate", "navette", "avvisi", "percorsi_alternativi"),
        )
    return Misure(
        ondate=False,
        navette_dal_t=critico + sim["senza_coordinamento_minuti_decisione"] + navette["minuti_attivazione"],
        navette_zona=navette["punto_carico_preferito"],
        informati_dal_t=max(critico, fine) + sim["senza_coordinamento_minuti_informazione"],
        fattore_piedi=1.0,
        etichette=("navette_tardive",),
    )


def _destinazioni_ripiego(
    misure: Misure, ripiego: str, navette_ok: bool, capacita_navette: int, capacita_piedi: int
) -> dict[str, float]:
    """Chi rinuncia a una linea sospesa sceglie tra navette e piedi in base alla capacità."""
    if not navette_ok:
        return {ripiego: 1.0}
    if misure.navette_zona == ripiego:
        return {ripiego: 1.0}
    return {misure.navette_zona: capacita_navette, ripiego: capacita_piedi}


def _ripiega(persone: dict[str, int], n: int, verso: dict[str, float]) -> None:
    for zid, k in ripartisci(n, verso).items():
        persone[zid] += k


def simula(
    scenario: dict[str, Any],
    misure: Misure,
    nome: NomeScenario = "sessione",
    rete: dict[str, Any] | None = None,
    passo_min: int = 5,
    fino_a_t: int | None = None,
) -> SerieSimulazione:
    rete = rete or carica_rete()
    sim = scenario["simulazione"]
    fine = scenario["fine_partita_t_min"]
    durata = scenario["durata_min"] if fino_a_t is None else fino_a_t
    zone = {z["id"]: z for z in rete["zone"]}
    modi = rete["modi"]
    ripiego = rete["ripiego_senza_linea"]
    settori = {s["id"]: s["spettatori"] for s in scenario["settori"]}
    totale = sum(settori.values())

    if misure.ondate:
        gruppi = [[fine + o["ritardo_min"], sum(settori[s] for s in o["settori"])] for o in sim["ondate"]]
    else:
        gruppi = [[fine, totale]]

    dentro = totale
    arrivati = 0
    persone = {zid: 0 for zid in zone if zid != "stadio"}
    passi: list[PassoSimulazione] = []

    for t in range(durata + 1):
        linee = {linea.id: linea for linea in sc.stato(scenario, t).linee}
        attiva = {m["id"]: linee[m["linea"]].attiva for m in modi}
        informati = misure.informati_dal_t is not None and t >= misure.informati_dal_t
        navette_ok = misure.navette_dal_t is not None and t >= misure.navette_dal_t

        # 1. uscita dallo stadio
        uscita = 0
        for g in gruppi:
            if g[0] <= t and g[1] > 0:
                n = min(g[1], sim["uscita_massima_persone_min"] - uscita)
                g[1] -= n
                uscita += n
        dentro -= uscita

        # 2. scelta del modo: chi è informato evita le linee sospese
        quote = {m["id"]: m["quota"] for m in modi}
        if informati:
            sospese = sum(q for mid, q in quote.items() if not attiva[mid])
            quote = {mid: q for mid, q in quote.items() if attiva[mid]}
            quote["_ripiego"] = sospese

        piedi = next(m for m in modi if m["id"] == "piedi")
        capacita_piedi = int(linee[piedi["linea"]].capacita_persone_min * misure.fattore_piedi)
        verso = _destinazioni_ripiego(
            misure, ripiego, navette_ok, scenario["navette"]["capacita_persone_min"], capacita_piedi
        )
        for mid, n in ripartisci(uscita, quote).items():
            if mid == "_ripiego":
                _ripiega(persone, n, verso)
            else:
                zona = next(m["zona"] for m in modi if m["id"] == mid)
                persone[zona] += n

        # 3. chi è informato non resta ad aspettare: lascia le stazioni chiuse e le code oltre
        #    la capienza della zona e ripiega. Chi non sa nulla, invece, aspetta.
        if informati:
            for m in modi:
                if not attiva[m["id"]] and persone[m["zona"]] > 0:
                    n, persone[m["zona"]] = persone[m["zona"]], 0
                    _ripiega(persone, n, verso)
            for zid, z in zone.items():
                if zid in ("stadio", ripiego):
                    continue
                eccesso = persone[zid] - z["capienza"]
                if eccesso > 0:
                    persone[zid] -= eccesso
                    persone[ripiego] += eccesso

        # 4. ogni zona smaltisce alla capacità dei mezzi attivi
        capacita = dict.fromkeys(persone, 0)
        for m in modi:
            if attiva[m["id"]]:
                c = linee[m["linea"]].capacita_persone_min
                if m["id"] == "piedi":
                    c = int(c * misure.fattore_piedi)
                capacita[m["zona"]] += c
        if navette_ok:
            capacita[misure.navette_zona] += scenario["navette"]["capacita_persone_min"]
        for zid, c in capacita.items():
            via = min(persone[zid], c)
            persone[zid] -= via
            arrivati += via

        assert dentro + sum(persone.values()) + arrivati == totale, "persone non conservate"

        if t % passo_min == 0 or t == durata:
            passi.append(_passo(t, scenario, zone, dentro, persone, arrivati, misure, navette_ok, informati))

    return SerieSimulazione(scenario=nome, passo_min=passo_min, passi=passi, stub=False)


def _passo(
    t: int,
    scenario: dict[str, Any],
    zone: dict[str, dict[str, Any]],
    dentro: int,
    persone: dict[str, int],
    arrivati: int,
    misure: Misure,
    navette_ok: bool,
    informati: bool,
) -> PassoSimulazione:
    stati = []
    for zid, z in zone.items():
        n = dentro if zid == "stadio" else persone[zid]
        stati.append(
            StatoZona(
                id=zid,
                nome=z["nome"],
                tipo=z["tipo"],
                lat=z["lat"],
                lon=z["lon"],
                capienza=z["capienza"],
                persone=n,
                in_coda=max(0, n - z["capienza"]),
                carico=round(n / z["capienza"], 2),
            )
        )
    attive = []
    if misure.ondate and t >= scenario["fine_partita_t_min"]:
        attive.append("ondate")
    if navette_ok:
        attive.append(f"navette da {zone[misure.navette_zona]['nome']}")
    if informati:
        attive.append("persone informate delle sospensioni")
    if misure.fattore_piedi > 1:
        attive.append("percorsi pedonali alternativi")
    return PassoSimulazione(
        t_min=t,
        ora=sc.ora(scenario, t),
        zone=stati,
        dentro_stadio=dentro,
        arrivati=arrivati,
        misure_attive=attive,
    )
