"""Stato del modello linguistico e una prova da browser (http://localhost:8001/docs)."""

from fastapi import APIRouter

from ..llm import Richiesta, servizio
from ..llm.finto import ModelloFinto
from ..models import ProvaLLM, StatoLLM

router = APIRouter(tags=["llm"])

SISTEMA_PROVA = (
    "Scrivi avvisi operativi per cittadini e turisti di Napoli. Regole: usa solo i fatti forniti, "
    "non aggiungere numeri, luoghi o orari; niente istruzioni di evacuazione; cita la fonte; "
    "massimo tre frasi; la prima parola è SIMULAZIONE perché la situazione è simulata."
)
TESTO_PROVA = (
    "Scrivi l'avviso in inglese per un turista allo stadio Maradona. Fatti (simulati): "
    "Linea 2 e Cumana sospese per verifiche dopo una scossa rilevata da INGV; navette sostitutive "
    "da Piazzale Tecchio; uscita dallo stadio a ondate, curve per ultime. Fonte: Comune di Napoli, "
    "control room."
)


@router.get("/api/llm", response_model=StatoLLM)
def stato() -> StatoLLM:
    s = servizio()
    finto = isinstance(s.modello, ModelloFinto)
    return StatoLLM(
        provider="finto" if finto else "anthropic",
        modello=s.modello.nome,
        chiave_configurata=not finto,
        voci_in_cache=s.cache.voci(),
        ultima_chiamata_ora=s.ultima.ora if s.ultima else None,
        ultima_chiamata_esito=s.ultima.esito if s.ultima else None,
        ultima_chiamata_dettaglio=s.ultima.dettaglio if s.ultima else None,
    )


@router.post("/api/llm/prova", response_model=ProvaLLM)
def prova() -> ProvaLLM:
    """Scrive un avviso di prova su una situazione simulata fissa. La seconda volta viene dalla cache."""
    risposta = servizio().scrivi(Richiesta(sistema=SISTEMA_PROVA, testo=TESTO_PROVA, max_token=2000))
    return ProvaLLM(
        richiesta=TESTO_PROVA,
        testo=risposta.testo if risposta else None,
        modello=risposta.modello if risposta else None,
        da_cache=risposta.da_cache if risposta else False,
    )
