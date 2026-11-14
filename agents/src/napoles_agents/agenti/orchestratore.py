"""Orchestratore: integra le proposte, risolve i conflitti, produce un piano unico."""

from collections import defaultdict

from .. import llm
from ..llm.controlli import motivo_scarto, pulisci
from ..luoghi import agente, luogo
from ..models import Affidabilita, Conflitto, Piano, Proposta

# Dalla più alla meno certa: serve a calcolare l'affidabilità minima del piano.
ORDINE_AFFIDABILITA = [
    Affidabilita.UFFICIALE,
    Affidabilita.MISURATA,
    Affidabilita.STIMATA,
    Affidabilita.NON_VERIFICATA,
]


def pianifica(proposte: list[Proposta], t_min: int, numero: int) -> Piano:
    ordinate = sorted(proposte, key=lambda p: (-p.priorita, p.id))
    finali: list[Proposta] = []
    conflitti: list[Conflitto] = []
    occupate: dict[str, Proposta] = {}

    for p in ordinate:
        p = p.model_copy(deep=True)
        for risorsa in list(p.risorse):
            if risorsa not in occupate:
                continue
            alternativa = p.dettagli.get("punto_carico_alternativo")
            chi = occupate[risorsa]
            if alternativa and alternativa not in occupate:
                p.risorse = [alternativa if r == risorsa else r for r in p.risorse]
                p.dettagli["punto_carico"] = alternativa
                risoluzione = (
                    f"{luogo(risorsa)} resta a «{chi.titolo}» ({agente(chi.agente.value)}, priorità più "
                    f"alta); «{p.titolo}» ({agente(p.agente.value)}) si sposta su {luogo(alternativa)}."
                )
            else:
                risoluzione = (
                    f"{luogo(risorsa)} resta a «{chi.titolo}» ({agente(chi.agente.value)}); "
                    f"«{p.titolo}» ({agente(p.agente.value)}) la usa in un secondo momento."
                )
            conflitti.append(Conflitto(risorsa=risorsa, proposte=[chi.id, p.id], risoluzione=risoluzione))
        for risorsa in p.risorse:
            occupate.setdefault(risorsa, p)
        finali.append(p)

    testo_regole = sintesi(finali, conflitti)
    return Piano(
        id=f"piano_{numero:03d}",
        t_min=t_min,
        proposte=finali,
        conflitti=conflitti,
        sintesi=testo_regole,
        sintesi_modello=sintesi_modello(finali, conflitti, testo_regole),
        affidabilita_minima=max(
            (p.affidabilita for p in finali), key=ORDINE_AFFIDABILITA.index, default=None
        ),
    )


def sintesi(proposte: list[Proposta], conflitti: list[Conflitto]) -> str:
    if not proposte:
        return "Nessuna azione necessaria."
    agenti = defaultdict(int)
    for p in proposte:
        agenti[p.agente.value] += 1
    righe = [
        f"{len(proposte)} azioni da {len(agenti)} agenti, in ordine di priorità.",
        "Prima azione: " + proposte[0].titolo + ".",
    ]
    if conflitti:
        righe.append(f"{len(conflitti)} conflitti risolti: " + " ".join(c.risoluzione for c in conflitti))
    return " ".join(righe)


SISTEMA_SINTESI = (
    "Sei l'Orchestratore di N.A.P.L.E.S., sistema di agenti per la control room del Comune di Napoli. "
    "Spieghi all'operatore, in italiano, il piano che deve approvare o rifiutare. Regole: "
    "usa solo i fatti forniti; non aggiungere numeri, orari, luoghi o azioni; "
    "massimo quattro frasi brevi, senza elenchi e senza saluti; "
    "di' cosa fare per primo e perché, come sono stati risolti i conflitti, "
    "e qual è il dato meno certo su cui si basa il piano; "
    "niente istruzioni di evacuazione; la prima parola è SIMULAZIONE perché lo scenario è simulato."
)


def _fatti(proposte: list[Proposta], conflitti: list[Conflitto], testo_regole: str) -> str:
    righe = ["Azioni proposte, in ordine di priorità:"]
    for p in proposte:
        righe.append(
            f"- {p.titolo} (agente {agente(p.agente.value)}, dato {p.affidabilita.value}, "
            f"fonti: {', '.join(p.fonti)}). {p.motivazione}"
        )
    for c in conflitti:
        righe.append(f"Conflitto risolto: {c.risoluzione}")
    righe.append(f"Sintesi a regole: {testo_regole}")
    return "\n".join(righe)


def sintesi_modello(proposte: list[Proposta], conflitti: list[Conflitto], testo_regole: str) -> str | None:
    """Spiegazione scritta dal modello; None senza modello o se il testo non passa i controlli."""
    servizio = llm.servizio()
    if not proposte or not servizio.attivo:
        return None
    fatti = _fatti(proposte, conflitti, testo_regole)
    risposta = servizio.scrivi(
        llm.Richiesta(sistema=SISTEMA_SINTESI, testo=fatti, max_token=3000, effort="low")
    )
    if risposta is None:
        return None
    testo = pulisci(risposta.testo)
    motivo = motivo_scarto(testo, fatti, prefissi=("SIMULAZIONE",))
    if motivo:
        servizio.scarta(f"sintesi: {motivo}")
        return None
    return testo
