"""Fonte traffico: solo dati reali, nessuna rete nei test (la chiamata a Google è sostituita)."""

import urllib.error
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from napoles_agents.api import app
from napoles_agents.fonti import traffico_google
from napoles_agents.fonti.traffico_google import FonteTraffico, livello, percorsi
from napoles_agents.models import LivelloTraffico

RISPOSTA = {
    "routes": [
        {
            "duration": "1200s",
            "staticDuration": "900s",
            "distanceMeters": 9100,
            "polyline": {"encodedPolyline": "abc"},
        }
    ]
}


class Orologio:
    def __init__(self) -> None:
        self.t = datetime(2026, 11, 14, 17, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.t


def _fonte(chiamata=lambda corpo, chiave: RISPOSTA, **kw) -> FonteTraffico:
    kw.setdefault("ttl_s", 600)
    kw.setdefault("max_chiamate_giorno", 150)
    return FonteTraffico(chiave="k", chiamata=chiamata, **kw)


def test_senza_chiave_nessun_dato_inventato():
    t = FonteTraffico(chiave="", chiamata=lambda c, k: RISPOSTA).leggi()
    assert not t.disponibile
    assert t.motivo and "MAPS_API_KEY" in t.motivo
    assert all(p.durata_min is None for p in t.percorsi)
    assert not t.simulato


def test_risposta_reale_convertita():
    corpi = []
    t = _fonte(chiamata=lambda corpo, chiave: corpi.append(corpo) or RISPOSTA).leggi()
    assert t.disponibile and t.rilevato_alle
    p = t.percorsi[0]
    assert (p.durata_min, p.durata_senza_traffico_min, p.ritardo_min, p.distanza_km) == (20.0, 15.0, 5.0, 9.1)
    assert p.livello == LivelloTraffico.RALLENTATO
    assert corpi[0]["routingPreference"] == "TRAFFIC_AWARE"
    assert len(t.percorsi) == len(percorsi())


def test_soglie_livello():
    assert livello(100, 100) == LivelloTraffico.SCORREVOLE
    assert livello(120, 100) == LivelloTraffico.RALLENTATO
    assert livello(150, 100) == LivelloTraffico.CONGESTIONATO


def test_cache_rispetta_il_ttl():
    chiamate = []
    orologio = Orologio()
    f = _fonte(chiamata=lambda c, k: chiamate.append(1) or RISPOSTA, adesso=orologio)
    f.leggi()
    f.leggi()
    assert len(chiamate) == len(percorsi())
    orologio.t += timedelta(seconds=601)
    f.leggi()
    assert len(chiamate) == 2 * len(percorsi())


def test_quota_giornaliera_tiene_gli_ultimi_dati_reali():
    orologio = Orologio()
    f = _fonte(adesso=orologio, ttl_s=0, max_chiamate_giorno=len(percorsi()))
    primo = f.leggi()
    secondo = f.leggi()
    assert secondo.disponibile and secondo.rilevato_alle == primo.rilevato_alle
    assert secondo.motivo and "Quota" in secondo.motivo


def test_errore_di_rete_senza_dati_precedenti():
    def guasto(corpo, chiave):
        raise urllib.error.URLError("offline")

    t = _fonte(chiamata=guasto).leggi()
    assert not t.disponibile
    assert all(p.durata_min is None for p in t.percorsi)


def test_endpoint(monkeypatch):
    monkeypatch.setattr(traffico_google, "_fonte", FonteTraffico(chiave="", chiamata=lambda c, k: RISPOSTA))
    body = TestClient(app).get("/api/traffico").json()
    assert body["disponibile"] is False
    assert body["simulato"] is False
