"""Indicatori con e senza coordinamento, sullo stesso scenario.

Modello volutamente semplice, a passi di un minuto: le persone escono dallo stadio,
aspettano fuori e se ne vanno alla capacità dei mezzi disponibili. Tutti i parametri
sono nello scenario e dichiarati in docs/IPOTESI.md.
"""

from typing import Any

from .models import ConfrontoIndicatori, Indicatori, TipoEvento
from .scenario import eventi, stato

MAX_MINUTI = 240


def _primo_evento_critico(scenario: dict[str, Any]) -> int:
    return min(e.t_min for e in eventi(scenario) if e.tipo == TipoEvento.SOSPENSIONE_LINEA)


def _simula(scenario: dict[str, Any], coordinato: bool) -> Indicatori:
    sim = scenario["simulazione"]
    navette = scenario["navette"]
    fine = scenario["fine_partita_t_min"]
    critico = _primo_evento_critico(scenario)
    fattore_piedi = sim["con_coordinamento_fattore_percorsi_piedi"] if coordinato else 1.0
    capacita_ordinaria = sum(
        int(linea.capacita_persone_min * (fattore_piedi if linea.id == "piedi" else 1.0))
        for linea in stato(scenario, fine).linee
        if linea.attiva
    )
    if coordinato:
        minuti_avviso = sim["con_coordinamento_minuti_informazione"]
        minuti_decisione = sim["con_coordinamento_minuti_decisione"]
    else:
        minuti_avviso = sim["senza_coordinamento_minuti_informazione"]
        minuti_decisione = sim["senza_coordinamento_minuti_decisione"]
    navette_pronte = critico + minuti_decisione + navette["minuti_attivazione"]
    informati_da = critico + minuti_avviso

    settori = {s["id"]: s["spettatori"] for s in scenario["settori"]}
    if coordinato:
        da_uscire = [(fine + o["ritardo_min"], sum(settori[s] for s in o["settori"])) for o in sim["ondate"]]
    else:
        da_uscire = [(fine, sum(settori.values()))]

    dentro = sum(settori.values())
    fuori = 0
    picco = 0
    in_coda: list[list[int]] = [[t, n] for t, n in da_uscire]
    for minuto in range(fine, fine + MAX_MINUTI):
        # uscita dallo stadio
        uscita = 0
        for gruppo in in_coda:
            if gruppo[0] <= minuto and gruppo[1] > 0:
                n = min(gruppo[1], sim["uscita_massima_persone_min"] - uscita)
                gruppo[1] -= n
                uscita += n
        dentro -= uscita
        fuori += uscita
        # capacità di allontanamento: chi non sa delle sospensioni aspetta alle stazioni chiuse
        capacita = capacita_ordinaria if minuto >= informati_da else capacita_ordinaria // 2
        if minuto >= navette_pronte:
            capacita += navette["capacita_persone_min"]
        fuori = max(0, fuori - capacita)
        picco = max(picco, fuori)
        if dentro == 0 and fuori <= sim["persone_soglia_area_sgombra"]:
            deflusso = minuto - fine + 1
            break
    else:
        deflusso = MAX_MINUTI

    return Indicatori(
        scenario="con_coordinamento" if coordinato else "senza_coordinamento",
        deflusso_min=deflusso,
        picco_attesa_persone=picco,
        minuti_evento_avviso=minuti_avviso,
        minuti_decisione=minuti_decisione,
        # Deflusso e picco li calcola il modello, ma dipendono dai due tempi in ingresso (ipotesi).
        # Il compito B4 misura i tempi «con coordinamento» nella sessione.
        origine={
            "deflusso_min": "calcolato",
            "picco_attesa_persone": "calcolato",
            "minuti_evento_avviso": "ipotesi",
            "minuti_decisione": "ipotesi",
        },
        note=[
            f"Navette operative al minuto {navette_pronte} (fischio finale al minuto {fine}).",
            "Uscita a ondate per settore." if coordinato else "Uscita simultanea di tutti i settori.",
        ],
    )


def confronta(scenario: dict[str, Any]) -> ConfrontoIndicatori:
    sim = scenario["simulazione"]
    return ConfrontoIndicatori(
        con_coordinamento=_simula(scenario, coordinato=True),
        senza_coordinamento=_simula(scenario, coordinato=False),
        ipotesi=[
            "Capacità di linee, bus, navette e deflusso a piedi: valori simulati.",
            (
                "Senza coordinamento le persone scoprono le sospensioni dopo "
                f"{sim['senza_coordinamento_minuti_informazione']} minuti e nel frattempo la capacità di "
                "allontanamento si dimezza."
            ),
            (
                f"Minuti di decisione: {sim['senza_coordinamento_minuti_decisione']} senza coordinamento, "
                f"{sim['con_coordinamento_minuti_decisione']} con il piano dell'Orchestratore (ipotesi)."
            ),
            (
                "I percorsi pedonali alternativi indicati dall'agente Mobilità aumentano la capacità del "
                f"deflusso a piedi di un fattore {sim['con_coordinamento_fattore_percorsi_piedi']} (ipotesi)."
            ),
            "Tutti gli eventi sismici sono simulati.",
        ],
    )
