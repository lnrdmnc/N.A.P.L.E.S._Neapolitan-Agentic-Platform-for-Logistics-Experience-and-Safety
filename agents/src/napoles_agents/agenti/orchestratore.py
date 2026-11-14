"""Orchestratore: integra le proposte, risolve i conflitti, produce un piano unico."""

from collections import defaultdict

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

    return Piano(
        id=f"piano_{numero:03d}",
        t_min=t_min,
        proposte=finali,
        conflitti=conflitti,
        sintesi=sintesi(finali, conflitti),
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
