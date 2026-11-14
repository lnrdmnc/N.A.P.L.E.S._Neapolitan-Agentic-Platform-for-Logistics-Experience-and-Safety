"""B3: conferma di ricezione degli avvisi."""

from fastapi.testclient import TestClient

from napoles_agents.api import app

client = TestClient(app)


def _avvisi_al_72() -> list[dict]:
    client.post("/api/reset")
    client.post("/api/avanza", json={"t_min": 72})
    piano = client.get("/api/piano").json()
    return client.post(f"/api/piano/{piano['id']}/approva").json()


def _ricezione(avviso: str) -> dict:
    return next(r for r in client.get("/api/avvisi/ricezione").json() if r["avviso"] == avviso)


def test_si_conta_solo_un_avviso_inviato():
    _avvisi_al_72()
    assert client.post("/api/avvisi/inesistente/visto", json={"dispositivo": "a"}).status_code == 404


def test_una_conferma_per_dispositivo():
    avviso = _avvisi_al_72()[0]["identifier"]
    for _ in range(3):
        r = client.post(f"/api/avvisi/{avviso}/visto", json={"dispositivo": "telefono-1"})
        assert r.status_code == 200
    client.post(f"/api/avvisi/{avviso}/visto", json={"dispositivo": "telefono-2"})
    assert _ricezione(avviso)["visti_reali"] == 2


def test_conferma_senza_dispositivo_conta_ogni_volta():
    avviso = _avvisi_al_72()[0]["identifier"]
    client.post(f"/api/avvisi/{avviso}/visto")
    client.post(f"/api/avvisi/{avviso}/visto")
    assert _ricezione(avviso)["visti_reali"] == 2


def test_le_conferme_restano_sul_proprio_avviso():
    avvisi = _avvisi_al_72()
    client.post(f"/api/avvisi/{avvisi[0]['identifier']}/visto", json={"dispositivo": "x"})
    assert _ricezione(avvisi[1]["identifier"])["visti_reali"] == 0


def test_le_stime_crescono_col_tempo_e_restano_simulate():
    avviso = _avvisi_al_72()[0]
    subito = _ricezione(avviso["identifier"])
    client.post("/api/avanza", json={"t_min": 90})
    dopo = _ricezione(avviso["identifier"])
    assert subito["simulato"] and dopo["simulato"]
    assert subito["minuti_dall_invio"] == 0 and dopo["minuti_dall_invio"] == 18
    assert dopo["visti_stimati"] > subito["visti_stimati"]
    assert dopo["visti_stimati"] <= dopo["consegnati_stimati"]


def test_reset_azzera_le_conferme():
    avviso = _avvisi_al_72()[0]["identifier"]
    client.post(f"/api/avvisi/{avviso}/visto", json={"dispositivo": "x"})
    avviso_nuovo = _avvisi_al_72()[0]["identifier"]
    assert _ricezione(avviso_nuovo)["visti_reali"] == 0
