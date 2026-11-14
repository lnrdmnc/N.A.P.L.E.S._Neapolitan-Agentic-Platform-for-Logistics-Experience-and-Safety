"""Napoli oggi e nei prossimi giorni: eventi previsti, zone, orari critici, alternative."""

import re
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from napoles_agents.agenti import calendario
from napoles_agents.api import app
from napoles_agents.fonti.partite_football import FontePartite

OGGI = datetime(2026, 11, 14, 19, 0, tzinfo=UTC)
RISPOSTA = {
    "matches": [
        {
            "id": 1,
            "utcDate": "2026-11-21T19:45:00Z",
            "homeTeam": {"name": "SSC Napoli", "shortName": "Napoli"},
            "awayTeam": {"name": "Torino FC", "shortName": "Torino"},
            "competition": {"name": "Serie A"},
            "status": "TIMED",
        }
    ]
}


@pytest.fixture(autouse=True)
def partite_finte(tmp_path, monkeypatch):
    finta = FontePartite(
        chiave="x", chiamata=lambda _u, _k: RISPOSTA, copia=tmp_path / "p.json", adesso=lambda: OGGI
    )
    monkeypatch.setattr(calendario, "fonte_partite", lambda: finta)


def test_eventi_dal_piu_vicino_con_partita_reale_e_esempi_dichiarati():
    r = calendario.prossimi_giorni(OGGI, 10)
    inizi = [p.evento.inizio for p in r.eventi]
    assert inizi == sorted(inizi)
    partita = next(p for p in r.eventi if p.evento.tipo == "partita")
    assert partita.evento.affidabilita == "ufficiale" and not partita.evento.esempio
    assert partita.evento.inizio.startswith("2026-11-21T20:45")  # ora di Roma
    for p in r.eventi:
        if p.evento.esempio:
            assert p.evento.affidabilita == "non_verificata"
    assert any("esempio" in (f.motivo or "") for f in r.fonti)


def test_finestre_di_arrivo_e_uscita():
    partita = next(p for p in calendario.prossimi_giorni(OGGI, 10).eventi if p.evento.tipo == "partita")
    arrivo, uscita = partita.impatto.finestre
    assert (arrivo.da, arrivo.a) == ("19:15", "20:45")
    assert (uscita.da, uscita.a) == ("22:40", "23:40")


def test_zona_fermate_da_evitare_e_alternative_senza_codici():
    partita = next(p for p in calendario.prossimi_giorni(OGGI, 10).eventi if p.evento.tipo == "partita")
    imp = partita.impatto
    assert imp.livello == "alto" and "Fuorigrotta" in imp.zona
    assert any("Campi Flegrei" in f for f in imp.da_evitare)
    assert any("Leopardi" in f for f in imp.alternative)
    assert not re.search(r"\(\d+\)", " ".join(imp.da_evitare + imp.alternative))
    assert "Leopardi" in imp.consiglio


def test_solo_i_giorni_richiesti():
    r = calendario.prossimi_giorni(OGGI, 2)
    assert all(p.evento.tipo != "partita" for p in r.eventi)  # la partita è tra 7 giorni
    assert r.eventi[0].giorno == "domani"


def test_api_prossimi_giorni():
    r = TestClient(app).get("/api/napoli/prossimi-giorni", params={"giorni": 10})
    assert r.status_code == 200
    d = r.json()
    assert d["eventi"] and {f["nome"] for f in d["fonti"]} == {"football-data.org", "Elenco curato dal team"}
    assert TestClient(app).get("/api/napoli/prossimi-giorni", params={"giorni": 99}).status_code == 422
