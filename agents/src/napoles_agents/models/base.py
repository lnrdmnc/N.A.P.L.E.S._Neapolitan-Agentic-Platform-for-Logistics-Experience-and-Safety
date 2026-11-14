"""Enumerazioni condivise da tutti i contratti."""

from enum import StrEnum


class Affidabilita(StrEnum):
    """Quanto è certa un'informazione: si mostra sempre a schermo."""

    UFFICIALE = "ufficiale"  # emessa da un'autorità (Protezione Civile, gestore)
    MISURATA = "misurata"  # misurata da una fonte affidabile (es. INGV)
    STIMATA = "stimata"  # stimata dal sistema
    NON_VERIFICATA = "non_verificata"  # voci, social


class Ambito(StrEnum):
    RISCHIO = "rischio"
    MOBILITA = "mobilita"
    FOLLA = "folla"
    COMUNICAZIONE = "comunicazione"


class Caso(StrEnum):
    """I tre casi di gestione degli alert (docs/PROGETTO.md, 6.2)."""

    A_UFFICIALE = "A_allarme_ufficiale"
    B_RILEVATO = "B_evento_rilevato"
    C_NON_VERIFICATO = "C_notizia_non_verificata"
