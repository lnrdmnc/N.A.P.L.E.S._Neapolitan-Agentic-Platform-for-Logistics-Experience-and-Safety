"""Controlli sul testo del modello prima di usarlo. Se uno fallisce il testo si scarta
e resta quello a regole: il modello riformula, non aggiunge fatti.
"""

import re

NUMERO = re.compile(r"\d+(?:[.,:]\d+)?")
# Parole che porterebbero a un'istruzione di evacuazione, che il sistema non dà mai (CLAUDE.md).
EVACUAZIONE = re.compile(
    r"evacu|sgombr|abbandona(?:te|re)? (?:le |la )?(?:case|casa|abitazion)", re.IGNORECASE
)


MARKDOWN = re.compile(r"\*\*|__|^#+\s*", re.MULTILINE)


def pulisci(testo: str) -> str:
    """Testo semplice per il telefono: niente grassetti o titoli Markdown, spazi in ordine."""
    return re.sub(r"\n{3,}", "\n\n", MARKDOWN.sub("", testo)).strip()


def numeri(testo: str) -> set[str]:
    return {n.replace(",", ".") for n in NUMERO.findall(testo)}


def motivo_scarto(testo: str, fonte: str, prefissi: tuple[str, ...] = ()) -> str | None:
    """None se il testo si può usare, altrimenti il motivo dello scarto."""
    extra = numeri(testo) - numeri(fonte)
    if extra:
        return f"numeri non presenti nella fonte: {', '.join(sorted(extra))}"
    if EVACUAZIONE.search(testo) and not EVACUAZIONE.search(fonte):
        return "istruzione di evacuazione"
    if prefissi and not testo.lstrip().upper().startswith(tuple(p.upper() for p in prefissi)):
        return f"manca l'etichetta {prefissi[0]}"
    return None
