"""Orchestratore: integra le proposte, risolve i conflitti, produce un piano unico."""

from collections import defaultdict

from ..models import Conflitto, Piano, Proposta


def pianifica(proposte: list[Proposta], t_min: int, numero: int) -> Piano:
    ordinate = sorted(proposte, key=lambda p: (-p.priorita, p.id))
    finali: list[Proposta] = []
    conflitti: list[Conflitto] = []
    occupate: dict[str, str] = {}

    for p in ordinate:
        p = p.model_copy(deep=True)
        for risorsa in list(p.risorse):
            if risorsa not in occupate:
                continue
            alternativa = p.dettagli.get("punto_carico_alternativo")
            if alternativa and alternativa not in occupate:
                p.risorse = [alternativa if r == risorsa else r for r in p.risorse]
                p.dettagli["punto_carico"] = alternativa
                risoluzione = (
                    f"«{risorsa}» resta a «{occupate[risorsa]}» (priorità più alta); "
                    f"«{p.id}» si sposta su «{alternativa}»."
                )
            else:
                risoluzione = (
                    f"«{risorsa}» resta a «{occupate[risorsa]}»; «{p.id}» la usa in un secondo momento."
                )
            conflitti.append(
                Conflitto(risorsa=risorsa, proposte=[occupate[risorsa], p.id], risoluzione=risoluzione)
            )
        for risorsa in p.risorse:
            occupate.setdefault(risorsa, p.id)
        finali.append(p)

    return Piano(
        id=f"piano_{numero:03d}",
        t_min=t_min,
        proposte=finali,
        conflitti=conflitti,
        sintesi=sintesi(finali, conflitti),
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
