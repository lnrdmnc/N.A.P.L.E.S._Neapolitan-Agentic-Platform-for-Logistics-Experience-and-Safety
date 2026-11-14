from fastapi.testclient import TestClient

from napoles_agents import scenario as sc
from napoles_agents.agenti import mobilita, rischio
from napoles_agents.api import app
from napoles_agents.models import Caso
from napoles_agents.motore import Sessione
from napoles_agents.registro import Registro
from napoles_agents.simulazione import confronta

S = sc.carica()


def test_nessuna_azione_prima_delle_scosse():
    assert Sessione().avanza(60) and Sessione().piano_corrente is None


def test_rischio_unisce_lo_sciame_in_una_proposta():
    proposte = rischio.proponi(sc.stato(S, 71), S)
    sciame = [p for p in proposte if p.caso == Caso.B_RILEVATO]
    assert len(sciame) == 1
    assert sciame[0].dettagli["numero_scosse"] == 2


def test_notizia_non_verificata_mai_diffusa():
    s = Sessione()
    s.avanza(80)
    s.approva(s.piano_corrente.id)
    assert any(p.caso == Caso.C_NON_VERIFICATO for p in s.piano_corrente.proposte)
    assert not any("Bagnoli" in (a.description + a.headline) for a in s.avvisi)


def test_allerta_ufficiale_inoltrata_senza_modifiche():
    s = Sessione()
    s.avanza(85)
    s.approva(s.piano_corrente.id)
    ufficiali = [a for a in s.avvisi if a.ufficiale]
    testo = next(e["testo_ufficiale"] for e in S["eventi"] if e["id"] == "ev_meteo")
    assert len(ufficiali) == 1 and ufficiali[0].description == testo


def test_nessuna_istruzione_di_evacuazione():
    s = Sessione()
    for t in (72, 85, 101):
        s.avanza(t)
        s.approva(s.piano_corrente.id)
    for a in s.avvisi:
        assert "evacu" not in f"{a.description} {a.instruction or ''}".lower()


def test_orchestratore_risolve_conflitto_sul_punto_di_carico():
    s = Sessione()
    s.avanza(72)
    piano = s.piano_corrente
    navette = next(p for p in piano.proposte if p.azione == "attiva_navette")
    assert piano.conflitti and navette.dettagli["punto_carico"] == S["navette"]["punto_carico_alternativo"]


def test_aggiornamenti_dello_stesso_evento_sono_update():
    s = Sessione()
    s.avanza(70)
    s.approva(s.piano_corrente.id)
    s.avanza(72)
    s.approva(s.piano_corrente.id)
    tifoso = [a for a in s.avvisi if a.pubblico == "tifoso"]
    assert [a.msgType for a in tifoso] == ["Alert", "Update"]
    assert tifoso[1].references == tifoso[0].identifier


def test_piano_approvato_una_sola_volta():
    s = Sessione()
    s.avanza(72)
    s.approva(s.piano_corrente.id)
    try:
        s.approva(s.piano_corrente.id)
    except ValueError:
        return
    raise AssertionError("doppia approvazione accettata")


def test_registro_rileva_manomissioni():
    r = Registro()
    for i in range(3):
        r.aggiungi(i, "prova", {"i": i})
    assert r.verifica() == (True, None)
    r.voci[1].contenuto["i"] = 99
    assert r.verifica() == (False, 1)


def test_mobilita_senza_sospensioni_non_propone_nulla():
    assert mobilita.proponi(sc.stato(S, 10), S) == []


def test_ritardo_informazione_senza_coordinamento_ha_effetto():
    # Se il ritardo d'informazione non contasse, togliere il dimezzamento non cambierebbe nulla.
    from copy import deepcopy

    s = deepcopy(S)
    s["simulazione"]["senza_coordinamento_minuti_informazione"] = 0
    assert confronta(s).senza_coordinamento.deflusso_min < confronta(S).senza_coordinamento.deflusso_min


def test_coordinamento_vince_anche_senza_ipotesi_sui_percorsi_a_piedi():
    from napoles_agents.simulazione import sensibilita

    for r in sensibilita(S):
        assert r["deflusso_con"] < r["deflusso_senza"] and r["picco_con"] < r["picco_senza"], r


def test_coordinamento_migliora_gli_indicatori():
    c = confronta(S)
    assert c.con_coordinamento.deflusso_min < c.senza_coordinamento.deflusso_min
    assert c.con_coordinamento.picco_attesa_persone < c.senza_coordinamento.picco_attesa_persone


def test_api_percorso_demo():
    client = TestClient(app)
    assert client.post("/api/reset").status_code == 200
    assert client.post("/api/avanza", json={"t_min": 72}).json()["linee"][0]["attiva"] is False
    piano = client.get("/api/piano").json()
    avvisi = client.post(f"/api/piano/{piano['id']}/approva").json()
    assert {a["pubblico"] for a in avvisi} == {"tifoso", "residente", "turista"}
    assert client.get("/api/avvisi", params={"pubblico": "turista"}).json()[0]["lingua"] == "en"
    assert client.get("/api/registro").json()["integro"] is True
    assert client.get("/api/indicatori").status_code == 200
    assert client.post("/api/avanza", json={"t_min": 999}).status_code == 422
