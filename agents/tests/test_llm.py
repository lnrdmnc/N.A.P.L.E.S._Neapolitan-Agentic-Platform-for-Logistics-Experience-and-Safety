"""Strato LLM: nessuna rete nei test. Claude è sostituito da un client finto con la stessa forma."""

from types import SimpleNamespace

import anthropic
import httpx
from fastapi.testclient import TestClient

from napoles_agents import llm
from napoles_agents.api import app
from napoles_agents.llm import Richiesta, Servizio
from napoles_agents.llm.anthropic_claude import ModelloClaude
from napoles_agents.llm.cache import Cache
from napoles_agents.llm.finto import ModelloFinto

RICHIESTA = Richiesta(sistema="regole", testo="scrivi un avviso")


class ClientFinto:
    """Imita anthropic.Anthropic: client.messages.create e client.beta.messages.create."""

    def __init__(self, stop_reason="end_turn", testo="Avviso di prova.", errore=None):
        self.chiamate = []
        self.stop_reason, self.testo, self.errore = stop_reason, testo, errore
        crea = SimpleNamespace(create=self._crea)
        self.messages = crea
        self.beta = SimpleNamespace(messages=crea)

    def _crea(self, **kw):
        self.chiamate.append(kw)
        if self.errore:
            raise self.errore
        blocchi = [SimpleNamespace(type="thinking"), SimpleNamespace(type="text", text=self.testo)]
        return SimpleNamespace(stop_reason=self.stop_reason, content=blocchi, model=kw["model"])


def _servizio(tmp_path, client):
    return Servizio(modello=ModelloClaude(chiave="k", client=client), cache=Cache(tmp_path))


def test_finto_e_deterministico_e_non_va_ai_cittadini(tmp_path):
    f = ModelloFinto()
    assert f.scrivi(RICHIESTA) == f.scrivi(RICHIESTA)
    s = Servizio(modello=ModelloFinto(), cache=Cache(tmp_path))
    assert s.scrivi(RICHIESTA) is None
    assert s.ultima.esito == "finto"


def test_senza_chiave_si_usa_il_finto(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    assert isinstance(llm.modello_da_ambiente(), ModelloFinto)


def test_risposta_e_cache(tmp_path):
    client = ClientFinto()
    s = _servizio(tmp_path, client)
    prima = s.scrivi(RICHIESTA)
    seconda = s.scrivi(RICHIESTA)
    assert prima.testo == seconda.testo == "Avviso di prova."
    assert not prima.da_cache and seconda.da_cache
    assert len(client.chiamate) == 1


def test_cache_riletta_identica_da_un_altro_servizio(tmp_path):
    _servizio(tmp_path, ClientFinto()).scrivi(RICHIESTA)
    client = ClientFinto(testo="diverso")
    assert _servizio(tmp_path, client).scrivi(RICHIESTA).testo == "Avviso di prova."
    assert client.chiamate == []


def test_ripiego_lato_server_sui_rifiuti(tmp_path):
    client = ClientFinto()
    _servizio(tmp_path, client).scrivi(RICHIESTA)
    kw = client.chiamate[0]
    assert kw["model"] == "claude-opus-5-5"
    assert kw["fallbacks"] == "default"
    assert "temperature" not in kw and "thinking" not in kw


def test_rifiuto_o_troncamento_diventano_testo_a_regole(tmp_path):
    for stop in ("refusal", "max_tokens"):
        s = _servizio(tmp_path / stop, ClientFinto(stop_reason=stop))
        assert s.scrivi(RICHIESTA) is None
        assert s.ultima.esito == "errore"
        assert Cache(tmp_path / stop).voci() == 0


def test_errore_di_rete_diventa_testo_a_regole(tmp_path):
    errore = anthropic.APIConnectionError(request=httpx.Request("POST", "https://api.anthropic.com"))
    s = _servizio(tmp_path, ClientFinto(errore=errore))
    assert s.scrivi(RICHIESTA) is None
    assert s.ultima.dettaglio == "Rete non raggiungibile"


def test_endpoint_stato_e_prova_senza_chiave(monkeypatch, tmp_path):
    monkeypatch.setattr(llm, "_servizio", Servizio(modello=ModelloFinto(), cache=Cache(tmp_path)))
    client = TestClient(app)
    stato = client.get("/api/llm").json()
    assert stato["provider"] == "finto" and stato["chiave_configurata"] is False
    prova = client.post("/api/llm/prova").json()
    assert prova["testo"] is None and prova["simulato"] is True
