"""Cosa visitare: luoghi reali, eventi e scioperi veri."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from napoles_agents.agenti import calendario, visite
from napoles_agents.api import app
from napoles_agents.models import (
    Affidabilita,
    EventoCitta,
    EventoPrevisto,
    NapoliProssimiGiorni,
    Sciopero,
    ScioperoPrevisto,
)

ADESSO = datetime(2026, 11, 14, 19, 0, tzinfo=UTC)


def _concerto_plebiscito() -> EventoPrevisto:
    e = EventoCitta(
        id="c",
        titolo="Concerto",
        tipo="concerto",
        luogo_id="plebiscito",
        luogo="Piazza del Plebiscito",
        quartiere="San Ferdinando",
        inizio="2026-11-16T21:00:00+01:00",
        fine="2026-11-16T23:00:00+01:00",
        persone_attese=30000,
        fonte="test",
        affidabilita=Affidabilita.STIMATA,
    )
    return EventoPrevisto(evento=e, impatto=calendario.impatto(e), giorno="16/11")


def _sciopero_anm() -> ScioperoPrevisto:
    s = Sciopero(
        id="1",
        inizio="2026-11-16T11:00:00+01:00",
        fine="2026-11-16T15:00:00+01:00",
        orario="DALLE 11.00 ALLE 15.00",
        settore="Trasporto pubblico locale",
        rilevanza="Locale",
        area="Napoli",
        categoria="PERSONALE SOC. ANM DI NAPOLI",
        sindacati=["X"],
    )
    return calendario.sciopero_previsto(s, [], ADESSO)


def _cal(eventi=(), scioperi=()) -> NapoliProssimiGiorni:
    return NapoliProssimiGiorni(
        eventi=list(eventi), giorni=10, generato_al="", fonti=[], scioperi=list(scioperi)
    )


def test_luoghi_reali_con_fonte_e_fermate():
    assert len(visite.luoghi()) >= 15
    for luogo in visite.luoghi():
        assert luogo["fonte_coordinate"].startswith("OpenStreetMap") and luogo["accessi"]
        assert 40.7 < luogo["lat"] < 40.9 and 14.1 < luogo["lon"] < 14.4


def test_senza_eventi_ne_scioperi_tutto_consigliato():
    r = visite.consigli(ADESSO, _cal())
    assert {luogo.stato for luogo in r.luoghi} == {"consigliato"}


def test_durante_un_concerto_la_zona_si_evita():
    quando = datetime.fromisoformat("2026-11-16T20:30:00+01:00")
    r = visite.consigli(quando, _cal(eventi=[_concerto_plebiscito()]))
    stato = {luogo.id: luogo for luogo in r.luoghi}
    assert stato["plebiscito"].stato == "da_evitare_ora" and stato["san_carlo"].stato == "da_evitare_ora"
    assert stato["mann"].stato == "consigliato"  # il centro storico resta lontano
    assert r.luoghi[-1].stato == "da_evitare_ora"  # i luoghi da evitare in fondo


def test_sciopero_anm_segna_le_linee_e_lascia_la_linea_2():
    quando = datetime.fromisoformat("2026-11-16T12:00:00+01:00")
    r = visite.consigli(quando, _cal(scioperi=[_sciopero_anm()]))
    mann = next(luogo for luogo in r.luoghi if luogo.id == "mann")
    linee = {a.codice: a for a in mann.accessi}
    assert not linee["L1"].disponibile and "Sciopero" in linee["L1"].motivo
    assert linee["L2"].disponibile and mann.stato == "consigliato"
    elmo = next(luogo for luogo in r.luoghi if luogo.id == "sant_elmo")  # solo funicolari ANM
    assert elmo.stato == "con_disagi" and elmo.motivi_en


def test_momenti_e_api():
    r = visite.consigli(ADESSO, _cal(eventi=[_concerto_plebiscito()], scioperi=[_sciopero_anm()]))
    assert r.momenti[0].etichetta == "Adesso" and len(r.momenti) == 3
    # scegliendo un momento futuro, la lista dei momenti resta quella di adesso
    dopo = visite.consigli(
        datetime.fromisoformat(r.momenti[1].quando), _cal(scioperi=[_sciopero_anm()]), ADESSO
    )
    assert r.momenti[1].quando in [m.quando for m in dopo.momenti]
    risposta = TestClient(app).get("/api/napoli/da-visitare")
    assert risposta.status_code == 200 and risposta.json()["luoghi"]
    assert TestClient(app).get("/api/napoli/da-visitare", params={"quando": "ieri"}).status_code == 422
