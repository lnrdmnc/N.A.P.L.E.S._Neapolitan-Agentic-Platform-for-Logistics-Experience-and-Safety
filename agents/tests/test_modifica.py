"""B2: modifica del piano prima dell'approvazione."""

import pytest
from fastapi.testclient import TestClient

from napoles_agents.api import app
from napoles_agents.motore import Sessione

NAVETTE = "mobilita_navette_sostitutive"
SCIAME = "rischio_sciame_campi_flegrei"


def _al_minuto(t: int) -> Sessione:
    s = Sessione()
    s.avanza(t)
    return s


def test_escludere_le_navette_toglie_le_navette_dagli_avvisi():
    s = _al_minuto(72)
    piano = s.modifica(s.piano_corrente.id, [NAVETTE], motivo="mezzi non disponibili")
    assert piano.stato == "modificato"
    assert NAVETTE not in [p.id for p in piano.proposte]
    assert [p.id for p in piano.proposte_escluse] == [NAVETTE]
    avvisi = s.approva(piano.id)
    assert avvisi and all("navett" not in (a.instruction or "").lower() for a in avvisi)


def test_senza_navette_non_c_e_piu_conflitto():
    s = _al_minuto(72)
    assert s.piano_corrente.conflitti
    piano = s.modifica(s.piano_corrente.id, [NAVETTE])
    assert piano.conflitti == []


def test_la_modifica_finisce_nel_registro_e_sul_bus():
    s = _al_minuto(72)
    s.modifica(s.piano_corrente.id, [NAVETTE], motivo="prova", operatore="op1")
    voce = s.registro.voci[-1]
    assert voce.tipo == "piano_modificato" and voce.contenuto["escluse"] == [NAVETTE]
    assert s.registro.verifica() == (True, None)
    ultimo = s.bus.messaggi[-1]
    assert ultimo.tipo == "decisione" and "modificato" in ultimo.titolo


def test_si_puo_reincludere_una_proposta():
    s = _al_minuto(72)
    pid = s.piano_corrente.id
    s.modifica(pid, [NAVETTE])
    piano = s.modifica(pid, [])
    assert NAVETTE in [p.id for p in piano.proposte] and piano.proposte_escluse == []


def test_escludere_lo_sciame_non_genera_un_cessato_allarme():
    s = _al_minuto(70)
    s.approva(s.piano_corrente.id)
    s.avanza(72)
    s.modifica(s.piano_corrente.id, [SCIAME])
    avvisi = s.approva(s.piano_corrente.id)
    assert not [a for a in avvisi if a.msgType == "Cancel"]


def test_allerta_ufficiale_non_si_puo_escludere():
    s = _al_minuto(85)
    ufficiale = next(p.id for p in s.piano_corrente.proposte if p.caso == "A_allarme_ufficiale")
    with pytest.raises(ValueError):
        s.modifica(s.piano_corrente.id, [ufficiale])


def test_piano_approvato_non_si_modifica():
    s = _al_minuto(72)
    s.approva(s.piano_corrente.id)
    with pytest.raises(ValueError):
        s.modifica(s.piano_corrente.id, [NAVETTE])


def test_piano_modificato_viene_superato_da_un_fatto_nuovo():
    s = _al_minuto(72)
    pid = s.piano_corrente.id
    s.modifica(pid, [NAVETTE])
    s.avanza(76)  # arriva la notizia non verificata: nuovo piano
    assert s._trova(pid).stato == "superato" and s.piano_corrente.id != pid


def test_api_modifica_errori():
    client = TestClient(app)
    client.post("/api/reset")
    client.post("/api/avanza", json={"t_min": 72})
    pid = client.get("/api/piano").json()["id"]
    assert (
        client.post(f"/api/piano/{pid}/modifica", json={"proposte_escluse": ["inesistente"]}).status_code
        == 404
    )
    r = client.post(f"/api/piano/{pid}/modifica", json={"proposte_escluse": [NAVETTE], "motivo": "x"})
    assert r.status_code == 200 and r.json()["motivo_modifica"] == "x"
    assert client.get("/api/piano").json()["stato"] == "modificato"
    assert client.post(f"/api/piano/{pid}/approva").status_code == 200
    assert client.post(f"/api/piano/{pid}/modifica", json={"proposte_escluse": []}).status_code == 409
