"""P1: strumento di prova."""

from napoles_agents import prova


def test_tre_prove_con_controlli_superati(tmp_path, monkeypatch):
    monkeypatch.setattr(prova, "CARTELLA", tmp_path / "prove")
    monkeypatch.setattr(prova, "FILE_PREDEFINITO", tmp_path / "registro.jsonl")
    assert prova.main([]) == 0
    for strategia in ("subito", "tardi", "mai"):
        testo = (tmp_path / "prove" / f"prova-{strategia}.md").read_text(encoding="utf-8")
        assert testo.startswith(f"# Prova «{strategia}»")
        assert "⚠️" not in testo
    assert (tmp_path / "registro.jsonl").exists()


def test_approvare_subito_tardi_o_mai_cambia_la_citta():
    risultati = {}
    for strategia in ("subito", "tardi", "mai"):
        s = prova.esegui(strategia)
        picco = prova.confronta(s.scenario, s.approvati, s.avvisi).con_coordinamento.picco_attesa_persone
        risultati[strategia] = (len(s.avvisi), prova._deflusso(s.scenario, s.simulazione()), picco)
    assert risultati["mai"][0] == 0
    # Con le capacità reali delle linee (R2) approvare 10 minuti dopo non allunga lo sgombero,
    # ma lascia più persone in attesa: decidere subito conta sul picco.
    assert risultati["subito"][1] <= risultati["tardi"][1] < risultati["mai"][1]
    assert risultati["subito"][2] < risultati["tardi"][2]


def test_strategia_sconosciuta():
    assert prova.main(["forse"]) == 2
