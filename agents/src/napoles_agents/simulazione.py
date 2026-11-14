"""Indicatori con e senza coordinamento, sullo stesso scenario (compito B4).

I numeri vengono dal simulatore a zone (simulatore.py), lo stesso che disegna la mappa.
Ogni indicatore dichiara la sua origine (docs/PIANO.md, sezione 9):
- «calcolato»: uscita del simulatore, dati gli input;
- «misurato_in_sessione»: tempo letto dalle decisioni vere dell'operatore in questa sessione;
- «ipotesi»: parametro in ingresso, dichiarato in docs/IPOTESI.md.
"""

from copy import deepcopy
from typing import Any

from . import scenario as sc
from .decisioni import misure_da_decisioni
from .models import Alert, ConfrontoIndicatori, Indicatori, Piano, SerieSimulazione, TipoEvento
from .simulatore import Misure, misure_da_scenario, simula


def _primo_evento_critico(scenario: dict[str, Any]) -> int:
    return min(e.t_min for e in sc.eventi(scenario) if e.tipo == TipoEvento.SOSPENSIONE_LINEA)


def _deflusso(scenario: dict[str, Any], serie: SerieSimulazione) -> int | None:
    """Minuti dal fischio finale finché lo stadio è vuoto e fuori restano meno persone della soglia."""
    fine = scenario["fine_partita_t_min"]
    soglia = scenario["simulazione"]["persone_soglia_area_sgombra"]
    for p in serie.passi:
        fuori = sum(z.persone for z in p.zone if z.id != "stadio")
        if p.t_min >= fine and p.dentro_stadio == 0 and fuori <= soglia:
            return p.t_min - fine
    return None


def _indicatori(
    scenario: dict[str, Any],
    misure: Misure,
    nome: str,
    minuti_avviso: int,
    minuti_decisione: int,
    origine_tempi: str,
    note: list[str],
) -> Indicatori:
    serie = simula(scenario, misure, nome, passo_min=1)
    deflusso = _deflusso(scenario, serie)
    if deflusso is None:
        deflusso = scenario["durata_min"] - scenario["fine_partita_t_min"]
        note = [*note, "L'area non si sgombra entro la fine dello scenario: valore minimo."]
    zone = [z.id for z in serie.passi[0].zone if z.id != "stadio"]
    return Indicatori(
        scenario=nome,
        deflusso_min=deflusso,
        picco_attesa_persone=max(sum(z.persone for z in p.zone if z.id != "stadio") for p in serie.passi),
        minuti_evento_avviso=minuti_avviso,
        minuti_decisione=minuti_decisione,
        congestione_zone={
            zona: max(next(z for z in p.zone if z.id == zona).carico for p in serie.passi) for zona in zone
        },
        origine={
            "deflusso_min": "calcolato",
            "picco_attesa_persone": "calcolato",
            "congestione_zone": "calcolato",
            "minuti_evento_avviso": origine_tempi,
            "minuti_decisione": origine_tempi,
        },
        note=note,
    )


def tempi_misurati(
    scenario: dict[str, Any], approvati: list[Piano], avvisi: list[Alert]
) -> tuple[int, int] | None:
    """(minuti evento → avviso, minuti evento → decisione) dalla sessione, se ci sono già."""
    critico = _primo_evento_critico(scenario)
    decisioni = [p.t_decisione for p in approvati if p.t_decisione is not None and p.t_decisione >= critico]
    inviati = [a.sent_t_min for a in avvisi if not a.ufficiale and a.sent_t_min >= critico]
    if not decisioni or not inviati:
        return None
    return min(inviati) - critico, min(decisioni) - critico


def confronta(
    scenario: dict[str, Any],
    approvati: list[Piano] | None = None,
    avvisi: list[Alert] | None = None,
) -> ConfrontoIndicatori:
    """Senza decisioni della sessione, il caso «con coordinamento» usa i tempi ipotizzati.
    Appena l'operatore approva un piano dopo l'evento critico, usa le sue decisioni vere."""
    sim = scenario["simulazione"]
    fine = scenario["fine_partita_t_min"]
    misurati = tempi_misurati(scenario, approvati or [], avvisi or [])
    if misurati:
        avviso, decisione = misurati
        con = _indicatori(
            scenario,
            misure_da_decisioni(scenario, approvati or []),
            "con_coordinamento",
            avviso,
            decisione,
            "misurato_in_sessione",
            ["Decisioni vere dell'operatore in questa sessione."],
        )
    else:
        con = _indicatori(
            scenario,
            misure_da_scenario(scenario, True),
            "con_coordinamento",
            sim["con_coordinamento_minuti_informazione"],
            sim["con_coordinamento_minuti_decisione"],
            "ipotesi",
            ["Nessuna decisione ancora in sessione: tempi ipotizzati."],
        )
    senza = _indicatori(
        scenario,
        misure_da_scenario(scenario, False),
        "senza_coordinamento",
        sim["senza_coordinamento_minuti_informazione"],
        sim["senza_coordinamento_minuti_decisione"],
        "ipotesi",
        ["Uscita simultanea; le persone scoprono le sospensioni da sole dopo il fischio finale."],
    )
    return ConfrontoIndicatori(
        con_coordinamento=con,
        senza_coordinamento=senza,
        ipotesi=[
            "Numeri calcolati dal simulatore a zone, lo stesso della mappa.",
            "Capacità, capienze e quote modali: ordini di grandezza simulati (docs/IPOTESI.md).",
            (
                "Senza coordinamento le persone scoprono le sospensioni "
                f"{sim['senza_coordinamento_minuti_informazione']} minuti dopo il fischio finale "
                f"(minuto {fine}) e la decisione sulle navette arriva dopo "
                f"{sim['senza_coordinamento_minuti_decisione']} minuti: ipotesi."
            ),
            (
                "I percorsi pedonali alternativi aumentano la capacità a piedi di un fattore "
                f"{sim['con_coordinamento_fattore_percorsi_piedi']}: ipotesi."
            ),
            "Tutti gli eventi sismici sono simulati.",
        ],
    )


def sensibilita(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    """Quanto cambia il risultato se cambiano le ipotesi più discutibili.

    Il vantaggio va presentato come intervallo, non come numero unico.
    """
    righe = []
    for fattore in (1.0, 1.3, 1.5):
        for decisione_senza in (10, 20):
            s = deepcopy(scenario)
            s["simulazione"]["con_coordinamento_fattore_percorsi_piedi"] = fattore
            s["simulazione"]["senza_coordinamento_minuti_decisione"] = decisione_senza
            c = confronta(s)
            righe.append(
                {
                    "fattore_percorsi_piedi": fattore,
                    "decisione_senza_min": decisione_senza,
                    "deflusso_con": c.con_coordinamento.deflusso_min,
                    "deflusso_senza": c.senza_coordinamento.deflusso_min,
                    "picco_con": c.con_coordinamento.picco_attesa_persone,
                    "picco_senza": c.senza_coordinamento.picco_attesa_persone,
                }
            )
    return righe
