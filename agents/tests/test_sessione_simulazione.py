"""B1: la simulazione della sessione segue le decisioni approvate."""

from fastapi.testclient import TestClient

from napoles_agents.api import app
from napoles_agents.motore import Sessione


def _sgombro(serie) -> int:
    return next(
        p.t_min
        for p in serie.passi
        if p.t_min >= 95
        and p.dentro_stadio == 0
        and sum(z.persone for z in p.zone if z.id != "stadio") <= 500
    )


def _picco(serie, zona: str) -> float:
    return max(next(z for z in p.zone if z.id == zona).carico for p in serie.passi)


def _approva_al(t: int) -> Sessione:
    s = Sessione()
    s.avanza(t)
    s.approva(s.piano_corrente.id)
    s.avanza(170)
    return s


def test_senza_approvazione_nessuna_misura_attiva():
    s = Sessione()
    s.avanza(170)
    assert all(p.misure_attive == [] for p in s.simulazione().passi)


def test_approvare_cambia_la_citta():
    nessuna = Sessione()
    nessuna.avanza(170)
    subito = _approva_al(72)
    assert _sgombro(subito.simulazione()) < _sgombro(nessuna.simulazione())
    assert _picco(subito.simulazione(), "stazione_campi_flegrei") < _picco(
        nessuna.simulazione(), "stazione_campi_flegrei"
    )
    assert any("navette" in m for p in subito.simulazione().passi for m in p.misure_attive)


def test_approvare_tardi_costa():
    subito, tardi = _approva_al(72), _approva_al(101)
    assert _picco(subito.simulazione(), "piazzale_tecchio") < _picco(tardi.simulazione(), "piazzale_tecchio")
    assert _sgombro(subito.simulazione()) <= _sgombro(tardi.simulazione())


def test_rifiutare_non_cambia_la_citta():
    nessuna = Sessione()
    nessuna.avanza(72)
    rifiuto = Sessione()
    rifiuto.avanza(72)
    rifiuto.rifiuta(rifiuto.piano_corrente.id)
    assert rifiuto.simulazione() == nessuna.simulazione()


def test_il_piano_porta_l_impatto_stimato():
    s = Sessione()
    s.avanza(72)
    imp = s.piano_corrente.impatto
    assert imp is not None and imp.stub is False
    tecchio = next(z for z in imp.zone if z.zona == "piazzale_tecchio")
    assert tecchio.picco_carico_con_piano < tecchio.picco_carico_senza_piano


def test_escludere_le_navette_ricalcola_l_impatto():
    s = Sessione()
    s.avanza(72)
    pid = s.piano_corrente.id
    prima = {z.zona: z for z in s.piano_corrente.impatto.zone}
    s.modifica(pid, ["mobilita_navette_sostitutive"])
    dopo = {z.zona: z for z in s.piano_corrente.impatto.zone}
    assert dopo != prima


def test_api_simulazione_sessione_e_confronto():
    client = TestClient(app)
    client.post("/api/reset")
    assert client.get("/api/simulazione").json()["stub"] is False
    for nome in ("con_coordinamento", "senza_coordinamento"):
        serie = client.get("/api/simulazione", params={"scenario": nome}).json()
        assert serie["scenario"] == nome and serie["passi"]
