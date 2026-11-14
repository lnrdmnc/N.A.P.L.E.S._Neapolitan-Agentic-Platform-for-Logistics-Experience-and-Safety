"""B5: il modello riformula i testi, non decide e non tocca il caso A. Nessuna rete."""

import pytest

from napoles_agents import llm
from napoles_agents.llm import Risposta, Servizio
from napoles_agents.llm.cache import Cache
from napoles_agents.llm.controlli import motivo_scarto
from napoles_agents.motore import Sessione


class ModelloScrive:
    """Modello di prova: la funzione decide cosa «scrive» Claude per ogni richiesta."""

    nome = "prova"

    def __init__(self, scrivi):
        self._scrivi = scrivi
        self.richieste = []

    def scrivi(self, richiesta):
        self.richieste.append(richiesta)
        return Risposta(testo=self._scrivi(richiesta), modello=self.nome)


def _riformula(richiesta):
    inglese = "inglese" in richiesta.testo
    return ("SIMULATION – " if inglese else "SIMULAZIONE – ") + "testo riformulato."


@pytest.fixture
def modello(monkeypatch, tmp_path):
    def installa(scrivi=_riformula):
        m = ModelloScrive(scrivi)
        monkeypatch.setattr(llm, "_servizio", Servizio(modello=m, cache=Cache(tmp_path)))
        return m

    return installa


def _percorso(s: Sessione, fino_a: int = 100):
    avvisi = []
    for t in range(fino_a + 1):
        s.avanza(t)
        p = s.piano_corrente
        if p and p.stato == "proposto":
            avvisi += s.approva(p.id)
    return avvisi


def test_senza_modello_nessun_testo_del_modello():
    s = Sessione()
    avvisi = _percorso(s)
    assert avvisi and all(a.messaggio_modello is None for a in avvisi)
    assert all(p.sintesi_modello is None for p in s.piani)


def test_messaggi_per_profilo_ma_mai_per_il_caso_a(modello):
    m = modello()
    avvisi = _percorso(Sessione())
    ufficiali = [a for a in avvisi if a.ufficiale]
    operativi = [a for a in avvisi if not a.ufficiale]
    assert ufficiali and operativi
    assert all(a.messaggio_modello is None for a in ufficiali)
    assert all(a.messaggio_modello for a in operativi)
    testi_ufficiali = {a.description for a in ufficiali}
    assert not any(t in r.testo for r in m.richieste for t in testi_ufficiali)


def test_campi_cap_identici_con_e_senza_modello(modello):
    senza = _percorso(Sessione())
    modello()
    con = _percorso(Sessione())
    escludi = {"messaggio_modello"}
    assert [a.model_dump(exclude=escludi) for a in con] == [a.model_dump(exclude=escludi) for a in senza]


def test_sintesi_del_piano(modello):
    modello()
    s = Sessione()
    _percorso(s, fino_a=72)
    assert any(p.sintesi_modello and p.sintesi_modello.startswith("SIMULAZIONE") for p in s.piani)


def test_numero_inventato_scarta_il_testo(modello):
    modello(lambda r: "SIMULAZIONE – navette ogni 7 minuti.")
    avvisi = _percorso(Sessione())
    assert all(a.messaggio_modello is None for a in avvisi)
    assert llm.servizio().ultima.esito == "scartato"


def test_evacuazione_scarta_il_testo(modello):
    modello(lambda r: "SIMULAZIONE – evacuate lo stadio.")
    assert all(a.messaggio_modello is None for a in _percorso(Sessione()))


def test_controlli():
    assert motivo_scarto("SIMULAZIONE Md 3.2 alle 22:10", "Md 3,2 alle 22:10", ("SIMULAZIONE",)) is None
    assert "numeri" in motivo_scarto("SIMULAZIONE 5 navette", "navette", ("SIMULAZIONE",))
    assert "etichetta" in motivo_scarto("Linee sospese", "Linee sospese", ("SIMULAZIONE",))
    assert "evacuazione" in motivo_scarto("SIMULAZIONE evacuare", "linee", ("SIMULAZIONE",))


def test_markdown_tolto_prima_dei_controlli(modello):
    modello(lambda r: "**SIMULAZIONE:** testo riformulato.")
    avvisi = [a for a in _percorso(Sessione()) if not a.ufficiale and a.lingua == "it"]
    assert avvisi and all(a.messaggio_modello == "SIMULAZIONE: testo riformulato." for a in avvisi)
