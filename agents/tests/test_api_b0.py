from fastapi.testclient import TestClient

from napoles_agents.api import PORTA, app
from napoles_agents.motore import Sessione

client = TestClient(app)


def _percorso_demo() -> None:
    client.post("/api/reset")
    client.post("/api/avanza", json={"t_min": 72})
    piano = client.get("/api/piano").json()
    client.post(f"/api/piano/{piano['id']}/approva")


def test_porta_concordata():
    assert PORTA == 8001


def test_messaggi_raccontano_il_percorso_demo():
    _percorso_demo()
    msg = client.get("/api/messaggi").json()
    tipi = [m["tipo"] for m in msg]
    for tipo in ("evento", "proposta", "conflitto", "piano", "decisione", "avviso"):
        assert tipo in tipi, tipo
    assert [m["seq"] for m in msg] == list(range(1, len(msg) + 1))
    # l'avviso arriva solo dopo la decisione dell'operatore
    assert tipi.index("decisione") < tipi.index("avviso")


def test_messaggi_da_seq_restituisce_solo_i_nuovi():
    _percorso_demo()
    tutti = client.get("/api/messaggi").json()
    nuovi = client.get("/api/messaggi", params={"da_seq": tutti[-2]["seq"]}).json()
    assert nuovi == tutti[-1:]


def test_proposta_ripetuta_non_viene_ripubblicata():
    s = Sessione()
    s.avanza(72)
    prima = len([m for m in s.bus.messaggi if m.tipo == "proposta"])
    s.avanza(74)  # nessun fatto nuovo tra 72 e 74
    assert len([m for m in s.bus.messaggi if m.tipo == "proposta"]) == prima


def test_sciame_non_genera_avvisi_quando_le_scosse_invecchiano():
    s = Sessione()
    for t in range(s.scenario["durata_min"] + 1):
        s.avanza(t)
        p = s.piano_corrente
        if p and p.stato == "proposto":
            s.approva(p.id)
    conteggi = [
        p.dettagli["numero_scosse"]
        for piano in s.piani
        for p in piano.proposte
        if p.id == "rischio_sciame_campi_flegrei"
    ]
    assert conteggi == sorted(conteggi)  # il conteggio dello sciame non scende mai


def test_piano_ha_affidabilita_minima():
    s = Sessione()
    s.avanza(76)  # c'è anche la notizia non verificata
    assert s.piano_corrente.affidabilita_minima == "non_verificata"


def test_indicatori_dichiarano_l_origine():
    c = client.get("/api/indicatori").json()["con_coordinamento"]
    assert c["origine"]["deflusso_min"] == "calcolato"
    assert c["origine"]["minuti_decisione"] == "ipotesi"


def test_stub_rispondono_con_la_forma_del_contratto():
    _percorso_demo()
    assert client.get("/api/simulazione").json()["stub"] is True
    assert client.get("/api/contesto").json()["stub"] is True
    it = client.get("/api/itinerario").json()
    assert it["stub"] is True and it["tratte"][0]["percorribile"] is False
    avviso = client.get("/api/avvisi").json()[0]["identifier"]
    assert client.post(f"/api/avvisi/{avviso}/visto").status_code == 202
    assert client.get("/api/avvisi/ricezione").json()[0]["simulato"] is True
