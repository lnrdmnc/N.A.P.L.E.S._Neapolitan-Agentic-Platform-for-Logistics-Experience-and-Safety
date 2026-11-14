import urllib.error
from datetime import UTC, datetime, timedelta

from napoles_agents.fonti.partite_football import FontePartite, al_maradona, url_partite

ORA = datetime(2026, 11, 14, 18, 0, tzinfo=UTC)

RISPOSTA = {
    "matches": [
        {
            "id": 2,
            "utcDate": "2026-11-29T19:45:00Z",
            "homeTeam": {"name": "SSC Napoli", "shortName": "Napoli"},
            "awayTeam": {"name": "AS Roma", "shortName": "Roma"},
            "competition": {"name": "Serie A"},
            "status": "TIMED",
            "venue": "Stadio Diego Armando Maradona",
        },
        {
            "id": 1,
            "utcDate": "2026-11-22T17:00:00Z",
            "homeTeam": {"name": "SSC Napoli", "shortName": "Napoli"},
            "awayTeam": {"name": "Juventus FC", "shortName": "Juventus"},
            "competition": {"name": "Serie A"},
            "status": "SCHEDULED",
        },
        {
            "id": 3,
            "utcDate": "2026-12-03T20:00:00Z",
            "homeTeam": {"name": "SSC Napoli", "shortName": "Napoli"},
            "awayTeam": {"name": "Bari", "shortName": "Bari"},
            "competition": {"name": "Coppa Italia"},
            "status": "SCHEDULED",
            "venue": "Stadio San Nicola",
        },
    ]
}


def fonte(tmp_path, chiave="k", chiamata=None):
    return FontePartite(
        chiave=chiave,
        chiamata=chiamata or (lambda url, k: RISPOSTA),
        ttl_s=60,
        copia=tmp_path / "partite.json",
        adesso=lambda: ORA,
    )


def test_url_chiede_le_partite_in_casa_nei_prossimi_giorni():
    url = url_partite(ORA)
    assert "/v4/teams/113/matches?" in url
    assert "venue=HOME" in url and "dateFrom=2026-11-14" in url and "dateTo=2027-01-13" in url


def test_solo_maradona_e_ordinate(tmp_path):
    dati = fonte(tmp_path).leggi()
    assert dati.disponibile and not dati.simulato and not dati.copia
    assert [p.ospite for p in dati.partite] == ["Juventus", "Roma"]
    assert not al_maradona({"venue": "Stadio San Nicola"})


def test_senza_chiave_e_senza_copia_niente_dati_inventati(tmp_path):
    dati = fonte(tmp_path, chiave="").leggi()
    assert not dati.disponibile and dati.partite == []
    assert "FOOTBALL_DATA_API_KEY" in dati.motivo


def test_offline_usa_la_copia_salvata(tmp_path):
    fonte(tmp_path).leggi()  # salva la copia

    def giu(url, k):
        raise urllib.error.URLError("offline")

    dopo = FontePartite(
        chiave="k",
        chiamata=giu,
        ttl_s=60,
        copia=tmp_path / "partite.json",
        adesso=lambda: ORA + timedelta(hours=1),
    )
    dati = dopo.leggi()
    assert dati.disponibile and dati.copia
    assert len(dati.partite) == 2 and "copia salvata" in dati.motivo


def test_risposta_tenuta_in_memoria(tmp_path):
    chiamate = []
    f = fonte(tmp_path, chiamata=lambda url, k: chiamate.append(url) or RISPOSTA)
    f.leggi()
    f.leggi()
    assert len(chiamate) == 1
