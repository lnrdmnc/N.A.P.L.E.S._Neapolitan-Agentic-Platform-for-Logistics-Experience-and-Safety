from datetime import UTC, datetime

from napoles_agents.fonti.vulcani import FonteVulcani, converti

# Estratto ridotto del GeoJSON pubblico della Protezione Civile (stessa forma, campi che usiamo).
RISPOSTA = {
    "features": [
        {"properties": {"Vulcano": '<a href="x">Campi Flegrei</a>', "livello_allerta": "giallo"}},
        {"properties": {"Vulcano": '<a href="y">Vesuvio</a>', "livello_allerta": "verde"}},
        {"properties": {"Vulcano": '<a href="z">Etna</a>', "livello_allerta": "giallo"}},
    ]
}
ADESSO = datetime(2026, 11, 14, 18, 0, tzinfo=UTC)


def test_converti_tiene_solo_le_aree_di_napoli_con_fonte_e_ora():
    livelli = converti(RISPOSTA, "2026-11-14T18:00:00+00:00")
    assert [(lv.area, lv.livello) for lv in livelli] == [("Campi Flegrei", "giallo"), ("Vesuvio", "verde")]
    assert all("Protezione Civile" in lv.fonte and lv.url.startswith("https://") for lv in livelli)
    assert all(lv.verificato_il == "2026-11-14T18:00:00+00:00" for lv in livelli)


def test_lettura_salva_una_copia_e_la_usa_se_la_fonte_cade(tmp_path):
    copia = tmp_path / "vulcani.json"
    livelli, stato = FonteVulcani(chiamata=lambda _u: RISPOSTA, copia=copia, adesso=lambda: ADESSO).leggi()
    assert stato.disponibile and not stato.copia and len(livelli) == 2

    def guasto(_url):
        raise OSError("giù")

    livelli, stato = FonteVulcani(chiamata=guasto, copia=copia).leggi()
    assert stato.copia and stato.aggiornato_al == ADESSO.isoformat()
    assert livelli[0].livello == "giallo"


def test_senza_rete_e_senza_copia_non_inventa_livelli(tmp_path):
    def guasto(_url):
        raise OSError("giù")

    manca = tmp_path / "manca.json"
    livelli, stato = FonteVulcani(chiamata=guasto, copia=manca, a_mano=manca).leggi()
    assert livelli == [] and not stato.disponibile


def test_senza_rete_e_senza_copia_usa_il_livello_verificato_a_mano(tmp_path):
    def guasto(_url):
        raise OSError("giù")

    livelli, stato = FonteVulcani(chiamata=guasto, copia=tmp_path / "manca.json").leggi()
    assert [lv.area for lv in livelli] == ["Campi Flegrei", "Vesuvio"]
    assert stato.copia and "verificato a mano" in (stato.motivo or "")
    assert all(lv.url and lv.verificato_il for lv in livelli)


def test_risposta_senza_aree_attese_non_e_un_dato(tmp_path):
    vuota = {"features": [{"properties": {"Vulcano": "Etna", "livello_allerta": "giallo"}}]}
    manca = tmp_path / "manca.json"
    livelli, stato = FonteVulcani(chiamata=lambda _u: vuota, copia=manca, a_mano=manca).leggi()
    assert livelli == [] and not stato.disponibile
