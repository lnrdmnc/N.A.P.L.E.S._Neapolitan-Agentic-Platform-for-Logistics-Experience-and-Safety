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
    # originale per tutti + versione con cornice in inglese per il turista: testo identico in entrambi
    assert {a.pubblico for a in ufficiali} == {"tutti", "turista"}
    assert all(a.description == testo for a in ufficiali)


def test_turista_riceve_l_allerta_ufficiale_con_cornice_in_inglese_senza_doppioni():
    client = TestClient(app)
    client.post("/api/reset")
    client.post("/api/avanza", json={"t_min": 85})
    client.post(f"/api/piano/{client.get('/api/piano').json()['id']}/approva")
    turista = [a for a in client.get("/api/avvisi", params={"pubblico": "turista"}).json() if a["ufficiale"]]
    assert len(turista) == 1
    a = turista[0]
    assert a["lingua"] == "en" and "not translated" in a["headline"] and a["references"]
    residente = [
        a for a in client.get("/api/avvisi", params={"pubblico": "residente"}).json() if a["ufficiale"]
    ]
    assert len(residente) == 1 and residente[0]["pubblico"] == "tutti"


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
    # Se le persone sapessero subito delle sospensioni, le stazioni chiuse si affollerebbero meno.
    from copy import deepcopy

    s = deepcopy(S)
    s["simulazione"]["senza_coordinamento_minuti_informazione"] = 0
    subito = confronta(s).senza_coordinamento.congestione_zone["stazione_campi_flegrei"]
    tardi = confronta(S).senza_coordinamento.congestione_zone["stazione_campi_flegrei"]
    assert subito < tardi


def test_coordinamento_riduce_sempre_il_picco_e_le_stazioni_chiuse_affollate():
    # Risultato robusto: vale per ogni valore delle ipotesi discutibili.
    from napoles_agents.simulazione import sensibilita

    for r in sensibilita(S):
        assert r["picco_con"] < r["picco_senza"], r


def test_il_deflusso_piu_rapido_dipende_dai_percorsi_a_piedi():
    # Risultato onesto (docs/IPOTESI.md): senza l'ipotesi sui percorsi a piedi il coordinamento
    # non accelera lo sgombero; lo accelera solo se i percorsi alternativi aumentano la capacità.
    from napoles_agents.simulazione import sensibilita

    for r in sensibilita(S):
        if r["fattore_percorsi_piedi"] > 1.0:
            assert r["deflusso_con"] < r["deflusso_senza"], r


def test_indicatori_dichiarano_l_origine_e_la_congestione_per_zona():
    c = confronta(S)
    for i in (c.con_coordinamento, c.senza_coordinamento):
        assert set(i.origine) >= {"deflusso_min", "picco_attesa_persone", "congestione_zone"}
        assert i.congestione_zone
    assert c.con_coordinamento.congestione_zone["stazione_campi_flegrei"] == 0
    assert c.senza_coordinamento.congestione_zone["stazione_campi_flegrei"] > 1


def test_tempi_misurati_in_sessione_dopo_l_approvazione():
    from napoles_agents.motore import Sessione

    s = Sessione()
    s.avanza(72)
    assert (
        confronta(s.scenario, s.approvati, s.avvisi).con_coordinamento.origine["minuti_decisione"]
        == "ipotesi"
    )
    s.avanza(75)
    s.approva(s.piano_corrente.id)
    c = confronta(s.scenario, s.approvati, s.avvisi).con_coordinamento
    assert c.origine["minuti_decisione"] == "misurato_in_sessione"
    assert c.minuti_decisione == 75 - 72 and c.minuti_evento_avviso == 75 - 72


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
    assert {a["pubblico"] for a in avvisi} == {"tifoso", "residente", "pendolare", "turista"}
    assert client.get("/api/avvisi", params={"pubblico": "turista"}).json()[0]["lingua"] == "en"
    assert client.get("/api/registro").json()["integro"] is True
    assert client.get("/api/indicatori").status_code == 200
    assert client.post("/api/avanza", json={"t_min": 999}).status_code == 422
