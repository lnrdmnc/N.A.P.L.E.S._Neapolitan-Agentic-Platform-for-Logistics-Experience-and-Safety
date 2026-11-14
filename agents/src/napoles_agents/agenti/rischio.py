"""Agente Rischio: sismica, allerte meteo, notizie non verificate."""

from typing import Any

from ..models import Affidabilita, Ambito, Caso, Proposta, StatoCitta, TipoEvento


def severita_sisma(magnitudo: float, soglie: dict[str, float]) -> str:
    if magnitudo >= soglie["severo_magnitudo"]:
        return "Severe"
    if magnitudo >= soglie["moderato_magnitudo"]:
        return "Moderate"
    if magnitudo >= soglie["attenzione_magnitudo"]:
        return "Minor"
    return "Unknown"


def proponi(stato: StatoCitta, scenario: dict[str, Any]) -> list[Proposta]:
    soglie = scenario["soglie_sisma"]
    proposte: list[Proposta] = []

    # Caso B: sciame sismico rilevato. Le scosse a meno di `finestra_sciame_min` l'una dall'altra
    # formano un solo sciame, che resta attivo fino a `finestra_sciame_min` dopo l'ultima scossa:
    # così il conteggio non scende quando le prime scosse invecchiano (niente avvisi a raffica).
    finestra = soglie["finestra_sciame_min"]
    rilevanti = [
        e
        for e in stato.eventi
        if e.tipo == TipoEvento.SISMA
        and e.magnitudo is not None
        and e.magnitudo >= soglie["attenzione_magnitudo"]
    ]
    scosse: list = []
    for e in rilevanti:
        if scosse and e.t_min - scosse[-1].t_min > finestra:
            scosse = []
        scosse.append(e)
    if scosse and stato.t_min - scosse[-1].t_min > finestra:
        scosse = []
    if scosse:
        massima = max(e.magnitudo or 0 for e in scosse)
        severita = severita_sisma(massima, soglie)
        proposte.append(
            Proposta(
                id="rischio_sciame_campi_flegrei",
                agente=Ambito.RISCHIO,
                t_min=stato.t_min,
                titolo=(
                    f"Sciame sismico ai Campi Flegrei: {len(scosse)} "
                    f"{'scossa' if len(scosse) == 1 else 'scosse'}, massima Md {massima}"
                ),
                azione="livello_attenzione_sismica",
                dettagli={
                    "numero_scosse": len(scosse),
                    "magnitudo_massima": massima,
                    "severita": severita,
                    "ultima_scossa_t_min": max(e.t_min for e in scosse),
                    "eventi": [e.id for e in scosse],
                    "livello_vulcanico": stato.livello_vulcanico_campi_flegrei,
                },
                risorse=[],
                priorita=5 if severita in ("Moderate", "Severe") else 4,
                affidabilita=Affidabilita.MISURATA,
                caso=Caso.B_RILEVATO,
                motivazione=(
                    "Evento misurato da INGV, nessun allarme ufficiale ricevuto: si informano le persone "
                    "e si attivano solo misure operative, senza istruzioni di evacuazione."
                ),
                fonti=sorted({e.fonte for e in scosse}),
            )
        )

    for e in stato.eventi:
        # Caso A: allerta ufficiale, da inoltrare senza modifiche.
        if e.tipo == TipoEvento.ALLERTA_METEO and e.affidabilita == Affidabilita.UFFICIALE:
            proposte.append(
                Proposta(
                    id=f"rischio_inoltra_{e.id}",
                    agente=Ambito.RISCHIO,
                    t_min=stato.t_min,
                    titolo=f"Inoltrare l'allerta ufficiale: {e.titolo}",
                    azione="inoltra_allerta_ufficiale",
                    dettagli={"evento": e.id, "testo_ufficiale": e.testo_ufficiale, "zona": e.zona},
                    priorita=4,
                    affidabilita=Affidabilita.UFFICIALE,
                    caso=Caso.A_UFFICIALE,
                    motivazione="Allerta emessa da un'autorità: si inoltra il testo originale, senza riscriverlo.",
                    fonti=[e.fonte],
                )
            )
        # Caso C: notizia non verificata, mai rilanciata al pubblico.
        elif e.tipo == TipoEvento.NOTIZIA_NON_VERIFICATA:
            proposte.append(
                Proposta(
                    id=f"rischio_segnala_{e.id}",
                    agente=Ambito.RISCHIO,
                    t_min=stato.t_min,
                    titolo=f"Notizia non verificata: {e.titolo}",
                    azione="segnala_notizia_non_verificata",
                    dettagli={"evento": e.id, "diffondere": False},
                    priorita=2,
                    affidabilita=Affidabilita.NON_VERIFICATA,
                    caso=Caso.C_NON_VERIFICATO,
                    motivazione=(
                        "Nessuna fonte ufficiale o misura conferma la notizia: non si diffonde, "
                        "si segnala all'operatore per una verifica."
                    ),
                    fonti=[e.fonte],
                )
            )
    return proposte
