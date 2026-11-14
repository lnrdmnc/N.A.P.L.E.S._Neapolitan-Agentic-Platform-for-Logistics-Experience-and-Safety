"""Claude via SDK ufficiale `anthropic`. Chiave e modello da `.env` (LLM_API_KEY, LLM_MODEL).

Con i modelli che lo prevedono si attiva il ripiego lato server in caso di rifiuto
(`fallbacks: "default"`); un rifiuto finale diventa ErroreLLM e chi chiama usa il testo a regole.
"""

import anthropic

from .base import ErroreLLM, Richiesta, Risposta

MODELLO_PREDEFINITO = "claude-opus-5-5"
# Modelli che accettano il ripiego lato server sui rifiuti (beta server-side-fallback-2026-07-01)
CON_RIPIEGO = {
    "claude-opus-5-5",
    "claude-sonnet-5-5",
    "claude-opus-5",
    "claude-fable-5-2",
    "claude-fable-5-1",
}
BETA_RIPIEGO = "server-side-fallback-2026-07-01"


class ModelloClaude:
    def __init__(self, chiave: str, modello: str | None = None, client: anthropic.Anthropic | None = None):
        self.nome = modello or MODELLO_PREDEFINITO
        self.client = client or anthropic.Anthropic(api_key=chiave, timeout=60.0, max_retries=2)

    def scrivi(self, richiesta: Richiesta) -> Risposta:
        parametri = {
            "model": self.nome,
            "max_tokens": richiesta.max_token,
            "system": richiesta.sistema,
            "messages": [{"role": "user", "content": richiesta.testo}],
            "output_config": {"effort": "medium"},
        }
        try:
            if self.nome in CON_RIPIEGO:
                risposta = self.client.beta.messages.create(
                    betas=[BETA_RIPIEGO], fallbacks="default", **parametri
                )
            else:
                risposta = self.client.messages.create(**parametri)
        except anthropic.AuthenticationError as e:
            raise ErroreLLM("Chiave LLM_API_KEY non valida") from e
        except anthropic.RateLimitError as e:
            raise ErroreLLM("Limite di richieste raggiunto") from e
        except anthropic.APIStatusError as e:
            raise ErroreLLM(f"Errore dell'API ({e.status_code})") from e
        except anthropic.APIConnectionError as e:
            raise ErroreLLM("Rete non raggiungibile") from e

        if risposta.stop_reason == "refusal":
            raise ErroreLLM("Il modello ha rifiutato la richiesta")
        if risposta.stop_reason == "max_tokens":
            raise ErroreLLM("Testo troncato (max_tokens)")
        testo = "".join(b.text for b in risposta.content if b.type == "text").strip()
        if not testo:
            raise ErroreLLM("Risposta vuota")
        return Risposta(testo=testo, modello=risposta.model)
