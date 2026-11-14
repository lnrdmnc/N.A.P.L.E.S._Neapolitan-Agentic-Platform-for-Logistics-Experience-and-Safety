"""Scenario provato sulla prossima partita vera al Maradona."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from napoles_agents import riferimento
from napoles_agents.api import app
from napoles_agents.fonti import partite_football
from napoles_agents.models import Partita, Partite

ADESSO = datetime(2026, 11, 14, 19, 0, tzinfo=UTC)


def _partita(id_: int, quando: str, stato: str = "TIMED") -> Partita:
    return Partita(
        id=id_, data_ora=quando, casa="Napoli", ospite=f"Squadra {id_}", competizione="Serie A", stato=stato
    )


def test_sceglie_la_prima_partita_non_finita():
    partite = Partite(
        partite=[
            _partita(3, "2026-12-05T19:45:00Z"),
            _partita(1, "2026-11-10T19:45:00Z", "FINISHED"),
            _partita(2, "2026-11-21T19:45:00Z"),
        ],
        disponibile=True,
    )
    assert riferimento.scegli(partite, ADESSO).id == 2


def test_una_partita_appena_iniziata_conta_ancora():
    partite = Partite(partite=[_partita(1, "2026-11-14T18:00:00Z", "IN_PLAY")], disponibile=True)
    assert riferimento.scegli(partite, ADESSO).id == 1


def test_senza_partite_nessuna_partita_inventata():
    assert riferimento.scegli(Partite(partite=[], disponibile=False), ADESSO) is None


def test_lo_stato_della_citta_porta_la_partita_reale(tmp_path, monkeypatch):
    risposta = {
        "matches": [
            {
                "id": 7,
                "utcDate": "2099-11-21T19:45:00Z",
                "homeTeam": {"name": "SSC Napoli", "shortName": "Napoli"},
                "awayTeam": {"name": "Torino FC", "shortName": "Torino"},
                "competition": {"name": "Serie A"},
                "status": "TIMED",
            }
        ]
    }
    finta = partite_football.FontePartite(
        chiave="x", chiamata=lambda _u, _k: risposta, copia=tmp_path / "p.json"
    )
    monkeypatch.setattr(partite_football, "_fonte", finta)
    stato = TestClient(app).get("/api/stato").json()
    assert stato["partita_reale"]["ospite"] == "Torino"
    assert stato["partita_reale"]["casa"] == "Napoli"


def test_senza_fonte_lo_stato_non_inventa_la_partita():
    assert TestClient(app).get("/api/stato").json()["partita_reale"] is None
