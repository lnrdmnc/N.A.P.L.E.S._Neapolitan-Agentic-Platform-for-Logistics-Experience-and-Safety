"""Agente Folla: presenze allo stadio e deflusso a ondate."""

from typing import Any

from ..models import Affidabilita, Ambito, Proposta, StatoCitta
from ..scenario import ora

MINUTI_DOPO_FINE = 45  # oltre questo intervallo lo stadio si considera vuoto


def proponi(stato: StatoCitta, scenario: dict[str, Any]) -> list[Proposta]:
    fine = scenario["fine_partita_t_min"]
    linee_sospese = [linea for linea in stato.linee if not linea.attiva]
    if not linee_sospese or stato.t_min > fine + MINUTI_DOPO_FINE:
        return []

    settori = {s["id"]: s for s in scenario["settori"]}
    ondate = []
    for i, o in enumerate(scenario["simulazione"]["ondate"], start=1):
        ondate.append(
            {
                "ondata": i,
                "settori": [settori[s]["nome"] for s in o["settori"]],
                "settori_id": o["settori"],
                "persone": sum(settori[s]["spettatori"] for s in o["settori"]),
                "uscita_t_min": fine + o["ritardo_min"],
                "uscita_ora": ora(scenario, fine + o["ritardo_min"]),
            }
        )
    return [
        Proposta(
            id="folla_deflusso_a_ondate",
            agente=Ambito.FOLLA,
            t_min=stato.t_min,
            titolo=f"Deflusso a ondate di {stato.spettatori} spettatori in {len(ondate)} turni",
            azione="deflusso_a_ondate",
            dettagli={"ondate": ondate, "punto_raccolta": "piazzale_tecchio"},
            risorse=["piazzale_tecchio"],
            priorita=5,
            affidabilita=Affidabilita.STIMATA,
            motivazione=(
                "Con le linee su ferro sospese, l'uscita simultanea concentrerebbe migliaia di persone "
                "davanti alle stazioni chiuse: le ondate tengono l'attesa sotto controllo."
            ),
            fonti=["Capienze dei settori (simulate)"],
        )
    ]
