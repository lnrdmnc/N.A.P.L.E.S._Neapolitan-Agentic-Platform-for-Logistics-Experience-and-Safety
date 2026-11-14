"""Napoli oggi e nei prossimi giorni: eventi previsti, zone, orari critici, alternative."""

import json
import re
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from napoles_agents.agenti import calendario
from napoles_agents.api import app
from napoles_agents.fonti.partite_football import FontePartite
from napoles_agents.scenario import DATA

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


# Elenco curato fisso: i test non dipendono dagli eventi veri del momento in eventi_napoli.json.
CURATI = {
    "eventi": [
        {
            "id": "concerto_verificato",
            "titolo": "Concerto",
            "tipo": "concerto",
            "luogo": "palapartenope",
            "inizio": "2026-11-15T21:00:00+01:00",
            "durata_min": 150,
            "persone_attese": 5000,
            "fonte": "Sito del locale",
            "esempio": False,
        },
        {
            "id": "esempio_corteo",
            "titolo": "Corteo",
            "tipo": "manifestazione",
            "luogo": "lungomare",
            "inizio": "2026-11-16T10:00:00+01:00",
            "durata_min": 180,
            "persone_attese": 5000,
            "fonte": "Esempio",
            "esempio": True,
        },
    ]
}


@pytest.fixture(autouse=True)
def partite_finte(tmp_path, monkeypatch):
    finta = FontePartite(
        chiave="x", chiamata=lambda _u, _k: RISPOSTA, copia=tmp_path / "p.json", adesso=lambda: OGGI
    )
    monkeypatch.setattr(calendario, "fonte_partite", lambda: finta)
    carica = calendario._carica
    monkeypatch.setattr(
        calendario, "_carica", lambda nome: CURATI if nome == "eventi_napoli" else carica(nome)
    )


def test_eventi_dal_piu_vicino_con_partita_reale_e_esempi_dichiarati():
    r = calendario.prossimi_giorni(OGGI, 10)
    inizi = [p.evento.inizio for p in r.eventi]
    assert inizi == sorted(inizi)
    partita = next(p for p in r.eventi if p.evento.tipo == "partita")
    assert partita.evento.affidabilita == "ufficiale" and not partita.evento.esempio
    assert partita.evento.inizio.startswith("2026-11-21T20:45")  # ora di Roma
    affidabilita = {p.evento.id: p.evento.affidabilita for p in r.eventi}
    assert affidabilita["esempio_corteo"] == "non_verificata"
    assert affidabilita["concerto_verificato"] == "stimata"  # evento vero, affluenza stimata
    assert any("esempio" in (f.motivo or "") for f in r.fonti)


def test_elenco_curato_reale_ha_fonte_e_luoghi_noti():
    """Il file vero: ogni evento ha una fonte, un luogo con coordinate e nessun esempio nascosto."""
    eventi = json.loads((DATA / "eventi_napoli.json").read_text(encoding="utf-8"))["eventi"]
    luoghi = calendario.luoghi()
    for e in eventi:
        assert e["fonte"] and e["luogo"] in luoghi
        datetime.fromisoformat(e["inizio"])
        assert e["esempio"] or not e["id"].startswith("esempio")


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
    assert d["eventi"] and {f["nome"] for f in d["fonti"]} == {
        "football-data.org",
        "Elenco curato dal team",
        "Ministero dei Trasporti (scioperi)",
    }
    assert TestClient(app).get("/api/napoli/prossimi-giorni", params={"giorni": 99}).status_code == 422
