"""Agente Mobilità: linee sospese, navette sostitutive, percorsi alternativi."""

from typing import Any

from ..models import Affidabilita, Ambito, Proposta, StatoCitta, TipoEvento


def proponi(stato: StatoCitta, scenario: dict[str, Any]) -> list[Proposta]:
    sospese = [linea for linea in stato.linee if not linea.attiva]
    if not sospese:
        return []

    navette = scenario["navette"]
    capacita_persa = sum(linea.capacita_persone_min for linea in sospese)
    meteo = any(e.tipo == TipoEvento.ALLERTA_METEO for e in stato.eventi)
    fonti = sorted({e.fonte for e in stato.eventi if e.tipo == TipoEvento.SOSPENSIONE_LINEA})

    proposte = [
        Proposta(
            id="mobilita_navette_sostitutive",
            agente=Ambito.MOBILITA,
            t_min=stato.t_min,
            titolo=f"Navette sostitutive per {', '.join(linea.nome for linea in sospese)}",
            azione="attiva_navette",
            dettagli={
                "linee_sospese": [linea.id for linea in sospese],
                "capacita_persa_persone_min": capacita_persa,
                "capacita_navette_persone_min": navette["capacita_persone_min"],
                "minuti_attivazione": navette["minuti_attivazione"],
                "punto_carico": navette["punto_carico_preferito"],
                "punto_carico_alternativo": navette["punto_carico_alternativo"],
            },
            risorse=[navette["punto_carico_preferito"]],
            priorita=4,
            affidabilita=Affidabilita.UFFICIALE,
            motivazione=(
                f"Le linee sospese tolgono circa {capacita_persa} persone al minuto di capacità: "
                "le navette ne recuperano una parte."
            ),
            fonti=fonti,
        ),
        Proposta(
            id="mobilita_percorsi_pedonali",
            agente=Ambito.MOBILITA,
            t_min=stato.t_min,
            titolo="Percorsi a piedi verso le fermate attive",
            azione="indica_percorsi_alternativi",
            dettagli={
                "evitare": ["stazioni sospese"] + (["sottopassi"] if meteo else []),
                "allerta_meteo_attiva": meteo,
            },
            risorse=["via_terracina"],
            priorita=3,
            affidabilita=Affidabilita.STIMATA,
            motivazione="Distribuisce il deflusso su più direzioni invece che sulle stazioni chiuse."
            + (" Con l'allerta meteo si evitano i sottopassi." if meteo else ""),
            fonti=fonti,
        ),
    ]
    return proposte
