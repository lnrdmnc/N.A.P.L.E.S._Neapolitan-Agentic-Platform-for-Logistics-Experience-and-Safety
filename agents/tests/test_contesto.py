"""F1 e F2: contesto reale da INGV e Open-Meteo, mai inventato e mai mescolato al simulato."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from napoles_agents.api import app
from napoles_agents.fonti.ingv import AREE, FonteINGV
from napoles_agents.fonti.meteo import FonteMeteo

ORA = datetime(2026, 11, 14, 18, 0, tzinfo=UTC)


def _risposta_ingv(luogo: str, mag: float, tempo: str) -> dict:
    return {
        "features": [
            {
                "properties": {
                    "eventId": hash((luogo, tempo)) % 10**8,
                    "time": tempo,
                    "mag": mag,
                    "magType": "Md",
                    "place": luogo,
                },
                "geometry": {"coordinates": [14.14, 40.83, 2.1]},
            }
        ]
    }


def _ingv_finto(url: str) -> dict:
    if "lon=14.426" in url:
        return _risposta_ingv("Vesuvio", 2.6, "2026-11-12T03:11:16")
    return _risposta_ingv("Campi Flegrei", 2.6, "2026-11-13T07:22:11")


METEO_FINTO = {
    "current": {
        "time": "2026-11-14T18:45",
        "temperature_2m": 18.1,
        "precipitation": 0.0,
        "weather_code": 2,
        "wind_speed_10m": 7.7,
    }
}


def test_ingv_legge_entrambe_le_aree_dal_piu_recente(tmp_path):
    eventi, stato = FonteINGV(chiamata=_ingv_finto, copia=tmp_path / "i.json", adesso=lambda: ORA).leggi()
    assert stato.disponibile and not stato.copia
    assert [e.luogo for e in eventi] == ["Campi Flegrei", "Vesuvio"]
    assert all(e.simulato is False for e in eventi)
    assert len(AREE) == 2


def test_ingv_tiene_in_memoria_e_non_richiama_prima_del_ttl(tmp_path):
    chiamate = []

    def conta(url):
        chiamate.append(url)
        return _ingv_finto(url)

    f = FonteINGV(chiamata=conta, copia=tmp_path / "i.json", ttl_s=120, adesso=lambda: ORA)
    f.leggi()
    f.leggi()
    assert len(chiamate) == 2  # una per area, una volta sola


def test_ingv_senza_rete_usa_la_copia_con_la_sua_data(tmp_path):
    copia = tmp_path / "i.json"
    FonteINGV(chiamata=_ingv_finto, copia=copia, adesso=lambda: ORA).leggi()

    def guasto(_url):
        raise OSError("giù")

    dopo = ORA + timedelta(hours=1)
    eventi, stato = FonteINGV(chiamata=guasto, copia=copia, adesso=lambda: dopo).leggi()
    assert stato.disponibile and stato.copia and stato.aggiornato_al == ORA.isoformat()
    assert len(eventi) == 2


def test_ingv_senza_rete_e_senza_copia_non_inventa_nulla(tmp_path):
    def guasto(_url):
        raise OSError("giù")

    eventi, stato = FonteINGV(chiamata=guasto, copia=tmp_path / "manca.json").leggi()
    assert eventi == [] and not stato.disponibile and stato.motivo


def test_meteo_reale_e_copia(tmp_path):
    copia = tmp_path / "m.json"
    meteo, stato = FonteMeteo(chiamata=lambda _u: METEO_FINTO, copia=copia, adesso=lambda: ORA).leggi()
    assert stato.disponibile and meteo.temperatura_c == 18.1 and meteo.simulato is False

    def guasto(_url):
        raise OSError("giù")

    meteo2, stato2 = FonteMeteo(chiamata=guasto, copia=copia).leggi()
    assert stato2.copia and meteo2.temperatura_c == 18.1


def test_meteo_senza_rete_e_senza_copia_non_inventa_nulla(tmp_path):
    def guasto(_url):
        raise OSError("giù")

    meteo, stato = FonteMeteo(chiamata=guasto, copia=tmp_path / "manca.json").leggi()
    assert meteo is None and not stato.disponibile


def test_api_contesto_dichiara_lo_stato_delle_fonti():
    # Nei test le fonti sono senza rete (conftest): disponibili=False, nessun dato.
    c = TestClient(app).get("/api/contesto").json()
    assert c["stub"] is False
    assert {f["nome"] for f in c["fonti"]} == {"INGV FDSN", "Open-Meteo"}
    assert all(not f["disponibile"] for f in c["fonti"])
    assert c["eventi_ingv"] == [] and c["meteo"] is None
    # Livelli ufficiali verificati a mano sulla fonte, con data e indirizzo (data/livelli_vulcanici.json)
    livelli = {v["area"]: v for v in c["livelli_vulcanici"]}
    assert set(livelli) == {"Campi Flegrei", "Vesuvio"}
    assert all(v["verificato_il"] and v["url"].startswith("https://") for v in livelli.values())
