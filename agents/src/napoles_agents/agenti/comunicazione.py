"""Agente Comunicazione: dal piano approvato agli avvisi per zona, profilo e lingua.

Regole (docs/PROGETTO.md, 6.2):
- caso A: l'allerta ufficiale si inoltra con il testo originale, mai riscritta;
- caso B: evento rilevato, solo informazioni e misure operative, nessuna istruzione di evacuazione;
- caso C: la notizia non verificata non diventa mai un avviso pubblico.

Budget anti-allarme: un aggiornamento parte solo se cambia qualcosa per la persona
(gravità o istruzioni operative). Una scossa in più della stessa gravità non genera notifiche.
Cessato allarme operativo: quando lo sciame si chiude, un `Cancel` chiude gli avvisi del caso B.
Riguarda solo gli aspetti operativi: il rischio vulcanico resta della Protezione Civile.
"""

import json
from concurrent.futures import ThreadPoolExecutor, wait
from typing import Any

from .. import llm
from ..llm.controlli import motivo_scarto, pulisci
from ..luoghi import luogo
from ..models import Alert, AreaAlert, Caso, Piano, StatoCitta, TipoEvento
from ..scenario import DATA, ora

PUBBLICI = (("tifoso", "it"), ("residente", "it"), ("pendolare", "it"), ("turista", "en"))

SENDER = "N.A.P.L.E.S. – control room comunale (simulazione)"
# Area degli avvisi del caso B: contorno reale dello stadio e fermate vere vicine (data/area_avvisi.json).
_AREA = json.loads((DATA / "area_avvisi.json").read_text(encoding="utf-8"))
AREA_FUORIGROTTA = AreaAlert(descrizione=_AREA["descrizione"], poligono=[tuple(p) for p in _AREA["poligono"]])
AREA_NAPOLI = AreaAlert(descrizione="Comune di Napoli")


def _azione(piano: Piano, azione: str) -> Any:
    return next((p for p in piano.proposte if p.azione == azione), None)


def _linee_riattivate(stato: StatoCitta, scenario: dict[str, Any]) -> list[str]:
    nomi = {linea["id"]: linea["nome"].split("–")[0].strip() for linea in scenario["linee"]}
    attive = {linea.id for linea in stato.linee if linea.attiva}
    return [
        nomi.get(e.linea, e.linea)
        for e in stato.eventi
        if e.tipo == TipoEvento.RIATTIVAZIONE_LINEA and e.linea in attive
    ]


def _istruzioni(piano: Piano, stato: StatoCitta, scenario: dict[str, Any], pubblico: str) -> tuple[str, str]:
    """Istruzioni operative (italiano, inglese) per un profilo."""
    navette = _azione(piano, "attiva_navette")
    ondate = _azione(piano, "deflusso_a_ondate")
    percorsi = _azione(piano, "indica_percorsi_alternativi")
    it: list[str] = []
    en: list[str] = []
    riattivate = _linee_riattivate(stato, scenario)
    if riattivate and not navette:
        it.append(f"Di nuovo in servizio: {', '.join(riattivate)}.")
        en.append(f"Back in service: {', '.join(riattivate)}.")
    if navette:
        punto = luogo(navette.dettagli["punto_carico"])
        destinazioni = navette.dettagli.get("destinazioni") or []
        if pubblico == "pendolare" and destinazioni:
            it.append(
                f"Cumana e Linea 2 sono sospese: per {' e '.join(destinazioni)} navette sostitutive "
                f"da {punto}."
            )
        else:
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
    if pubblico == "pendolare":
        # Chi rientra verso l'area delle scosse: nessuna indicazione sul rischio, si rimanda a chi decide.
        it.append(
            "Prima di rientrare verso l'area flegrea segui le comunicazioni della Protezione Civile "
            "e del tuo Comune."
        )
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
            originale = Alert(
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
            avvisi.append(originale)
            # Cornice in inglese per il turista: solo il titolo è nostro e lo dice; il testo
            # ufficiale resta identico, in italiano, non tradotto né riassunto.
            avvisi.append(
                originale.model_copy(
                    update={
                        "identifier": f"{chiave}_turista_{stato.t_min}",
                        "references": originale.identifier,
                        "headline": (
                            ("SIMULATION – " if p.dettagli.get("simulato", True) else "")
                            + f"Official alert from {p.fonti[0].replace(' (simulato)', '')}"
                            + " – original Italian text below, not translated"
                        ),
                        "pubblico": "turista",
                        "lingua": "en",
                    }
                )
            )

        # Caso B: evento rilevato, avvisi per profilo con le misure operative del piano.
        elif p.caso == Caso.B_RILEVATO:
            d = p.dettagli
            for pubblico, lingua in PUBBLICI:
                chiave = f"sisma_campi_flegrei_{pubblico}"
                precedente = ultimo(chiave, pubblico)
                if precedente and precedente.msgType == "Cancel":
                    precedente = None  # sciame nuovo dopo un cessato allarme: si riparte da «Alert»
                istruzioni_it, istruzioni_en = _istruzioni(piano, stato, scenario, pubblico)
                if lingua == "it":
                    headline = "SIMULAZIONE – Scosse rilevate ai Campi Flegrei"
                    descrizione = (
                        f"INGV ha registrato una scossa di magnitudo Md {d['magnitudo_massima']}."
                        if d["numero_scosse"] == 1
                        else f"INGV ha registrato {d['numero_scosse']} scosse, la più forte di "
                        f"magnitudo Md {d['magnitudo_massima']}."
                    ) + " Nessun allarme ufficiale: segui le comunicazioni della Protezione Civile."
                    istruzioni = istruzioni_it
                else:
                    headline = "SIMULATION – Earthquakes detected in Campi Flegrei"
                    descrizione = (
                        f"INGV recorded one tremor of magnitude Md {d['magnitudo_massima']}."
                        if d["numero_scosse"] == 1
                        else f"INGV recorded {d['numero_scosse']} tremors, the strongest Md "
                        f"{d['magnitudo_massima']}."
                    ) + " No official alert: follow Civil Protection updates."
                    istruzioni = istruzioni_en
                # Budget anti-allarme: niente notifica se per la persona non cambia nulla.
                if (
                    precedente
                    and precedente.severity == d["severita"]
                    and (precedente.instruction or "") == istruzioni
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

    # Cessato allarme operativo: lo sciame non è più nel piano, si chiudono gli avvisi del caso B.
    # Se l'operatore ha solo escluso la proposta con «Modifica», lo sciame è ancora in corso: niente Cancel.
    if not any(p.caso == Caso.B_RILEVATO for p in piano.proposte + piano.proposte_escluse):
        finestra = scenario["soglie_sisma"]["finestra_sciame_min"]
        servizi_regolari = all(linea.attiva for linea in stato.linee)
        for pubblico, lingua in PUBBLICI:
            precedente = ultimo(f"sisma_campi_flegrei_{pubblico}", pubblico)
            if not precedente or precedente.msgType == "Cancel":
                continue
            if lingua == "it":
                headline = "SIMULAZIONE – Fine degli aggiornamenti operativi sulle scosse"
                descrizione = (
                    f"Nessuna nuova scossa rilevata da {finestra} minuti"
                    + (" e servizi di nuovo regolari." if servizi_regolari else ".")
                    + " Per il rischio vulcanico fanno fede le comunicazioni della Protezione Civile."
                )
            else:
                headline = "SIMULATION – Operational updates on the tremors have ended"
                descrizione = (
                    f"No new tremors detected for {finestra} minutes"
                    + (" and services are back to normal." if servizi_regolari else ".")
                    + " For volcanic risk, follow Civil Protection communications."
                )
            avvisi.append(
                Alert(
                    identifier=f"sisma_campi_flegrei_{pubblico}_{stato.t_min}",
                    sender=SENDER,
                    sent_t_min=stato.t_min,
                    msgType="Cancel",
                    references=precedente.identifier,
                    severity="Minor",
                    urgency="Past",
                    certainty="Observed",
                    event="Evento sismico",
                    headline=headline,
                    description=descrizione,
                    area=AREA_FUORIGROTTA,
                    source=precedente.source,
                    ufficiale=False,
                    pubblico=pubblico,
                    lingua=lingua,
                    piano_id=piano.id,
                )
            )
    return con_messaggi_del_modello(avvisi)


# --- Testi scritti dal modello (compito B5) -------------------------------------------------
# Il modello riformula per la persona i campi già decisi a regole; non decide nulla e non tocca
# mai le allerte ufficiali. I campi CAP restano identici: budget anti-allarme e test non cambiano.

ATTESA_MASSIMA_S = 25

SISTEMA_MESSAGGIO = (
    "Scrivi il messaggio che compare sul telefono di una persona a Napoli, a partire da un avviso "
    "operativo del Comune. Regole: usa solo i fatti dell'avviso; non aggiungere numeri, orari, luoghi, "
    "linee o consigli; niente istruzioni di evacuazione; tono calmo e diretto, frasi brevi, al massimo "
    "quattro; scrivi nella lingua indicata; la prima parola è SIMULAZIONE (in inglese SIMULATION) "
    "perché la situazione è simulata; chiudi con la fonte."
)

PROFILI = {
    "tifoso": "tifoso allo stadio Maradona, in italiano",
    "residente": "residente di Fuorigrotta, in italiano",
    "pendolare": "pendolare che rientra verso l'area flegrea, in italiano",
    "turista": "turista straniero allo stadio, in inglese semplice",
}


def _fonte_avviso(a: Alert) -> str:
    return "\n".join(
        x
        for x in (
            f"Per: {PROFILI.get(a.pubblico, a.pubblico)}",
            f"Tipo: {a.msgType}",
            f"Titolo: {a.headline}",
            f"Descrizione: {a.description}",
            f"Istruzioni: {a.instruction}" if a.instruction else "",
            f"Fonte: {a.source}",
        )
        if x
    )


def _messaggio(servizio: llm.Servizio, a: Alert) -> str | None:
    fonte = _fonte_avviso(a)
    risposta = servizio.scrivi(
        llm.Richiesta(sistema=SISTEMA_MESSAGGIO, testo=fonte, max_token=3000, effort="low")
    )
    if risposta is None:
        return None
    testo = pulisci(risposta.testo)
    motivo = motivo_scarto(testo, fonte, prefissi=("SIMULATION",) if a.lingua == "en" else ("SIMULAZIONE",))
    if motivo:
        servizio.scarta(f"{a.identifier}: {motivo}")
        return None
    return testo


def con_messaggi_del_modello(avvisi: list[Alert]) -> list[Alert]:
    servizio = llm.servizio()
    da_scrivere = [a for a in avvisi if not a.ufficiale]
    if not servizio.attivo or not da_scrivere:
        return avvisi
    with ThreadPoolExecutor(max_workers=8) as pool:
        futuri = {a.identifier: pool.submit(_messaggio, servizio, a) for a in da_scrivere}
        wait(futuri.values(), timeout=ATTESA_MASSIMA_S)
    testi = {k: f.result() for k, f in futuri.items() if f.done() and not f.exception()}
    return [
        a.model_copy(update={"messaggio_modello": testi[a.identifier]}) if testi.get(a.identifier) else a
        for a in avvisi
    ]
