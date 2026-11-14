"""Agente Comunicazione: dal piano approvato agli avvisi per zona, profilo e lingua.

Regole (docs/PROGETTO.md, 6.2):
- caso A: l'allerta ufficiale si inoltra con il testo originale, mai riscritta;
- caso B: evento rilevato, solo informazioni e misure operative, nessuna istruzione di evacuazione;
- caso C: la notizia non verificata non diventa mai un avviso pubblico.
"""

from typing import Any

from ..models import Alert, AreaAlert, Caso, Piano, StatoCitta
from ..scenario import ora

SENDER = "N.A.P.L.E.S. – control room comunale (simulazione)"
AREA_FUORIGROTTA = AreaAlert(
    descrizione="Fuorigrotta – area stadio Maradona",
    poligono=[(40.8310, 14.1880), (40.8310, 14.2000), (40.8240, 14.2000), (40.8240, 14.1880)],
)
AREA_NAPOLI = AreaAlert(descrizione="Comune di Napoli")
NOMI_PUNTI = {
    "piazzale_tecchio": "Piazzale Tecchio",
    "viale_giochi_del_mediterraneo": "Viale Giochi del Mediterraneo",
}


def _azione(piano: Piano, azione: str) -> Any:
    return next((p for p in piano.proposte if p.azione == azione), None)


def _istruzioni(piano: Piano, scenario: dict[str, Any], pubblico: str) -> tuple[str, str]:
    """Istruzioni operative (italiano, inglese) per un profilo."""
    navette = _azione(piano, "attiva_navette")
    ondate = _azione(piano, "deflusso_a_ondate")
    percorsi = _azione(piano, "indica_percorsi_alternativi")
    it: list[str] = []
    en: list[str] = []
    if navette:
        punto = NOMI_PUNTI.get(navette.dettagli["punto_carico"], navette.dettagli["punto_carico"])
        it.append(f"Cumana e Linea 2 sono sospese: navette sostitutive da {punto}.")
        en.append(f"Cumana and Line 2 are suspended: replacement shuttles from {punto}.")
    if ondate and pubblico in ("tifoso", "turista"):
        turni = "; ".join(
            f"{', '.join(o['settori'])} alle {o['uscita_ora']}" for o in ondate.dettagli["ondate"]
        )
        turni_en = "; ".join(
            f"{', '.join(o['settori'])} at {o['uscita_ora']}" for o in ondate.dettagli["ondate"]
        )
        it.append(f"Uscita dallo stadio a turni: {turni}. Attendi il tuo turno.")
        en.append(f"Stadium exit in turns: {turni_en}. Please wait for your turn.")
    if ondate and pubblico == "residente":
        ultima = ondate.dettagli["ondate"][-1]["uscita_t_min"]
        it.append(f"Evita l'area dello stadio fino alle {ora(scenario, ultima + 20)}.")
    if percorsi and percorsi.dettagli.get("allerta_meteo_attiva"):
        it.append("Per l'allerta meteo evita i sottopassi.")
        en.append("Due to the weather alert, avoid underpasses.")
    return " ".join(it), " ".join(en)


def prepara_avvisi(
    piano: Piano, stato: StatoCitta, scenario: dict[str, Any], precedenti: list[Alert]
) -> list[Alert]:
    avvisi: list[Alert] = []

    def ultimo(chiave: str, pubblico: str) -> Alert | None:
        trovati = [
            a for a in precedenti + avvisi if a.identifier.startswith(chiave) and a.pubblico == pubblico
        ]
        return trovati[-1] if trovati else None

    for p in piano.proposte:
        # Caso A: inoltro senza modifiche.
        if p.caso == Caso.A_UFFICIALE:
            chiave = f"ufficiale_{p.dettagli['evento']}"
            if ultimo(chiave, "tutti"):
                continue
            avvisi.append(
                Alert(
                    identifier=f"{chiave}_{stato.t_min}",
                    sender=p.fonti[0],
                    sent_t_min=stato.t_min,
                    msgType="Alert",
                    severity="Moderate",
                    urgency="Expected",
                    certainty="Likely",
                    event="Allerta meteo",
                    headline=p.titolo.removeprefix("Inoltrare l'allerta ufficiale: "),
                    description=p.dettagli["testo_ufficiale"],
                    area=AREA_NAPOLI,
                    source=p.fonti[0],
                    ufficiale=True,
                    pubblico="tutti",
                    piano_id=piano.id,
                )
            )

        # Caso B: evento rilevato, avvisi per profilo con le misure operative del piano.
        elif p.caso == Caso.B_RILEVATO:
            d = p.dettagli
            for pubblico, lingua in (("tifoso", "it"), ("residente", "it"), ("turista", "en")):
                chiave = f"sisma_campi_flegrei_{pubblico}"
                precedente = ultimo(chiave, pubblico)
                istruzioni_it, istruzioni_en = _istruzioni(piano, scenario, pubblico)
                if lingua == "it":
                    headline = "SIMULAZIONE – Scosse rilevate ai Campi Flegrei"
                    descrizione = (
                        f"INGV ha registrato {d['numero_scosse']} scosse, la più forte di magnitudo "
                        f"Md {d['magnitudo_massima']}. Nessun allarme ufficiale: segui le comunicazioni "
                        "della Protezione Civile."
                    )
                    istruzioni = istruzioni_it
                else:
                    headline = "SIMULATION – Earthquakes detected in Campi Flegrei"
                    descrizione = (
                        f"INGV recorded {d['numero_scosse']} tremors, the strongest Md "
                        f"{d['magnitudo_massima']}. No official alert: follow Civil Protection updates."
                    )
                    istruzioni = istruzioni_en
                if (
                    precedente
                    and precedente.description == descrizione
                    and precedente.instruction == istruzioni
                ):
                    continue
                avvisi.append(
                    Alert(
                        identifier=f"{chiave}_{stato.t_min}",
                        sender=SENDER,
                        sent_t_min=stato.t_min,
                        msgType="Update" if precedente else "Alert",
                        references=precedente.identifier if precedente else None,
                        severity=d["severita"],
                        urgency="Immediate",
                        certainty="Observed",
                        event="Evento sismico",
                        headline=headline,
                        description=descrizione,
                        instruction=istruzioni or None,
                        area=AREA_FUORIGROTTA,
                        expires_t_min=stato.t_min + 60,
                        source=", ".join(p.fonti),
                        ufficiale=False,
                        pubblico=pubblico,
                        lingua=lingua,
                        piano_id=piano.id,
                    )
                )
        # Caso C: nessun avviso pubblico.
    return avvisi
