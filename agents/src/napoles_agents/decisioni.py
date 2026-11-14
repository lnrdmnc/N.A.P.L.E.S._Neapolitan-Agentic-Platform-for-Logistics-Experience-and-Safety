"""Dalle decisioni dell'operatore alle misure attive nel simulatore a zone (compito B1).

Conta solo ciò che è stato approvato, e da quando: un piano proposto o rifiutato non
cambia la città. Senza nessuna approvazione le persone scoprono comunque le sospensioni,
ma tardi (lo stesso ritardo dichiarato per il caso «senza coordinamento»).
"""

from typing import Any

from . import scenario as sc
from .models import Impatto, ImpattoZona, Piano, SerieSimulazione, TipoEvento
from .simulatore import Misure, simula


def _azione(piano: Piano, azione: str):
    return next((p for p in piano.proposte if p.azione == azione), None)


def misure_da_decisioni(scenario: dict[str, Any], approvati: list[Piano]) -> Misure:
    """`approvati`: piani con stato «approvato» e `t_decisione`, in qualunque ordine."""
    sim = scenario["simulazione"]
    fine = scenario["fine_partita_t_min"]
    sospensioni = [e.t_min for e in sc.eventi(scenario) if e.tipo == TipoEvento.SOSPENSIONE_LINEA]
    critico = min(sospensioni) if sospensioni else None

    ondate = False
    navette_dal_t = None
    navette_zona = scenario["navette"]["punto_carico_preferito"]
    informati_dal_t = None
    da_avvisi = False
    fattore_piedi = 1.0
    etichette: list[str] = []

    for piano in sorted(approvati, key=lambda p: p.t_decisione or 0):
        t = piano.t_decisione if piano.t_decisione is not None else piano.t_min
        if _azione(piano, "deflusso_a_ondate") and t <= fine and not ondate:
            ondate = True
            etichette.append(f"ondate (approvate alle {sc.ora(scenario, t)})")
        navette = _azione(piano, "attiva_navette")
        if navette and navette_dal_t is None:
            navette_dal_t = t + navette.dettagli.get("minuti_attivazione", 0)
            navette_zona = navette.dettagli.get("punto_carico", navette_zona)
            etichette.append(f"navette (approvate alle {sc.ora(scenario, t)})")
        # Le persone sanno delle sospensioni dal primo avviso approvato che le contiene.
        if (navette or _azione(piano, "indica_percorsi_alternativi")) and informati_dal_t is None:
            informati_dal_t = t
            da_avvisi = True
        if _azione(piano, "indica_percorsi_alternativi") and fattore_piedi == 1.0:
            fattore_piedi = sim["con_coordinamento_fattore_percorsi_piedi"]

    if informati_dal_t is None and critico is not None:
        informati_dal_t = max(critico, fine) + sim["senza_coordinamento_minuti_informazione"]
        etichette.append("informazione tardiva, senza avvisi")

    return Misure(
        ondate=ondate,
        navette_dal_t=navette_dal_t,
        navette_zona=navette_zona,
        informati_dal_t=informati_dal_t,
        fattore_piedi=fattore_piedi,
        informati_da_avvisi=da_avvisi,
        etichette=tuple(etichette),
    )


def _minuti_alla_normalita(serie: SerieSimulazione, zona: str, fine: int) -> int:
    """Minuti dal fischio finale finché la zona torna sotto la capienza e ci resta."""
    ultimo_in_coda = None
    for p in serie.passi:
        z = next(z for z in p.zone if z.id == zona)
        if z.in_coda > 0:
            ultimo_in_coda = p.t_min
    if ultimo_in_coda is None:
        return 0
    return max(0, ultimo_in_coda + serie.passo_min - fine)


def impatto(scenario: dict[str, Any], approvati: list[Piano], piano: Piano, t: int) -> Impatto:
    """Effetto stimato di approvare `piano` adesso, rispetto a non approvarlo."""
    con_piano = piano.model_copy(update={"t_decisione": t, "stato": "approvato"})
    con = simula(scenario, misure_da_decisioni(scenario, [*approvati, con_piano]))
    senza = simula(scenario, misure_da_decisioni(scenario, approvati))
    fine = scenario["fine_partita_t_min"]
    zone = [z.id for z in con.passi[0].zone if z.id != "stadio"]

    def picco(serie: SerieSimulazione, zona: str) -> float:
        return max(next(z for z in p.zone if z.id == zona).carico for p in serie.passi)

    return Impatto(
        zone=[
            ImpattoZona(
                zona=zona,
                deflusso_min_con_piano=_minuti_alla_normalita(con, zona, fine),
                deflusso_min_senza_piano=_minuti_alla_normalita(senza, zona, fine),
                picco_carico_con_piano=picco(con, zona),
                picco_carico_senza_piano=picco(senza, zona),
            )
            for zona in zone
        ],
        stub=False,
    )
