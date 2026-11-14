import os

# Nei test la sessione dell'API non scrive il registro su file.
os.environ.setdefault("NAPOLES_REGISTRO", "")

# Nei test nessuna chiamata al modello linguistico, anche se l'ambiente ha una chiave.
os.environ["LLM_PROVIDER"] = "finto"


import pytest


@pytest.fixture(autouse=True)
def _fonti_reali_senza_rete(tmp_path, monkeypatch):
    """Nei test le fonti reali (INGV, meteo, vulcani) non usano mai la rete: rispondono «non disponibile»."""
    from napoles_agents.fonti import ingv, meteo, partite_football, scioperi, vulcani

    def senza_rete(*_args, **_kwargs):
        raise OSError("rete disattivata nei test")

    monkeypatch.setattr(ingv, "_fonte", ingv.FonteINGV(chiamata=senza_rete, copia=tmp_path / "ingv.json"))
    monkeypatch.setattr(meteo, "_fonte", meteo.FonteMeteo(chiamata=senza_rete, copia=tmp_path / "meteo.json"))
    monkeypatch.setattr(
        vulcani, "_fonte", vulcani.FonteVulcani(chiamata=senza_rete, copia=tmp_path / "vulcani.json")
    )
    # Partite: nessuna chiave e nessuna copia, quindi nessuna partita (i test che servono la iniettano).
    monkeypatch.setattr(
        partite_football, "_fonte", partite_football.FontePartite(chiave="", copia=tmp_path / "partite.json")
    )
    monkeypatch.setattr(
        scioperi, "_fonte", scioperi.FonteScioperi(chiamata=senza_rete, copia=tmp_path / "scioperi.json")
    )
