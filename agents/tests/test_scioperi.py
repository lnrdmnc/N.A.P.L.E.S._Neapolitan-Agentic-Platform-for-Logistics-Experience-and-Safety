"""Scioperi dei trasporti ufficiali (MIT) nei prossimi giorni di Napoli."""

from datetime import UTC, datetime

from napoles_agents.agenti import calendario
from napoles_agents.fonti import scioperi
from napoles_agents.fonti.scioperi import FonteScioperi, converti


def _item(guid, inizio, settore, rilevanza, regione, provincia, modalita, fine, categoria, sindacati="SIND"):
    return f"""<item><title>Data inizio: {inizio} - Settore: {settore} - Rilevanza: {rilevanza}
    - Regione: {regione} - Provincia: {provincia}</title><description>modalità: {modalita}&lt;br/&gt;Data fine: {fine}
    &lt;br/&gt;Settore: {settore}&lt;br/&gt;Rilevanza: {rilevanza}&lt;br/&gt;Regione: {regione}&lt;br/&gt;Provincia: {provincia}
    &lt;br/&gt;Sindacati: {sindacati}&lt;br/&gt;Categoria interessata: {categoria}&lt;br/&gt;Data proclamazione: 01/11/2026
    </description><guid>http://scioperi.mit.gov.it/{guid}</guid></item>"""


# Estratto nella forma del feed RSS del Ministero (scioperi.mit.gov.it), campi che usiamo.
FEED = (
    "<rss><channel>"
    + _item(
        1,
        "16/11/2026",
        "Trasporto pubblico locale",
        "Locale",
        "Campania",
        "Napoli",
        "4 ORE: DALLE 11.00 ALLE 15.00",
        "16/11/2026",
        "PERSONALE SOC. ANM DI NAPOLI",
        "A",
    )
    + _item(
        2,
        "16/11/2026",
        "Trasporto pubblico locale",
        "Locale",
        "Campania",
        "Napoli",
        "4 ORE: DALLE 11.00 ALLE 15.00",
        "16/11/2026",
        "PERSONALE SOC. ANM DI NAPOLI",
        "B",
    )
    + _item(
        3,
        "20/11/2026",
        "Ferroviario",
        "Nazionale",
        " Italia",
        "Tutte",
        "23 ORE: DALLE 21.00 DEL 20/11 ALLE 20.00 DEL 21/11",
        "21/11/2026",
        "PERSONALE DI MACCHINA E DI BORDO DEL GRUPPO FERROVIE DELLO STATO ITALIANE",
    )
    + _item(
        4,
        "14/11/2026",
        "Trasporto pubblico locale",
        "Locale",
        "Puglia",
        "Bari",
        "24 ORE",
        "14/11/2026",
        "PERSONALE AMTAB",
    )
    + _item(
        5,
        "22/11/2026",
        "Aereo",
        "Nazionale",
        " Italia",
        "Tutte",
        "4 ORE: DALLE 13.00 ALLE 17.00",
        "22/11/2026",
        "CONTROLLORI",
    )
    + _item(
        6,
        "20/11/2026",
        "Generale",
        "Nazionale",
        " Italia",
        "Tutte",
        "INTERA GIORNATA",
        "20/11/2026",
        "SCIOPERO GENERALE CON ESCLUSIONE SETTORE TRASPORTI",
    )
    + _item(
        7,
        "20/11/2026",
        "Plurisettoriale",
        "Nazionale",
        " Italia",
        "Tutte",
        "SETTORE FERROVIARIO 23 ORE: DALLE 21.00 DEL 20/11 ALLE 20.00 DEL 21/11; *TPL: INTERA PRESTAZIONE DEL 21/11",
        "21/11/2026",
        "PERSONALE IMPRESE CHE SVOLGONO ATTIVITA' FERROVIARIA",
    )
    + "</channel></rss>"
).encode()

OGGI = datetime(2026, 11, 14, 19, 0, tzinfo=UTC)
PARTITA = {
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


def test_solo_scioperi_che_toccano_napoli_e_doppioni_uniti():
    s = converti(FEED)
    assert [x.id for x in s] == ["1,2", "3", "7"]  # niente Bari, aereo, generale senza trasporti
    anm = s[0]
    assert anm.inizio.startswith("2026-11-16T11:00") and anm.fine.startswith("2026-11-16T15:00")
    assert anm.sindacati == ["A", "B"] and anm.affidabilita == "ufficiale" and not anm.simulato


def test_orario_su_due_giorni_e_intera_prestazione():
    s = {x.id: x for x in converti(FEED)}
    assert s["3"].inizio.startswith("2026-11-20T21:00") and s["3"].fine.startswith("2026-11-21T20:00")
    assert s["7"].fine.startswith("2026-11-22T00:00")  # il TPL sciopera tutto il 21/11


def test_linee_coinvolte_e_alternative_senza_inventare():
    s = {x.id: x for x in converti(FEED)}
    coinvolte, fuori = calendario.linee_di(s["1,2"])
    assert "bus ANM" in coinvolte and "Cumana (EAV)" in fuori
    coinvolte, fuori = calendario.linee_di(s["3"])
    assert "Linea 2 (Trenitalia)" in coinvolte and "Linea 1 e bus (ANM)" in fuori
    coinvolte, fuori = calendario.linee_di(s["7"])
    assert fuori == []  # coinvolge anche il TPL: nessuna linea dichiarata fuori


def test_sciopero_durante_l_arrivo_alla_partita(tmp_path, monkeypatch):
    from napoles_agents.fonti.partite_football import FontePartite

    monkeypatch.setattr(
        calendario,
        "fonte_partite",
        lambda: FontePartite(chiave="x", chiamata=lambda _u, _k: PARTITA, copia=tmp_path / "p.json"),
    )
    monkeypatch.setattr(
        scioperi, "_fonte", FonteScioperi(chiamata=lambda _u: FEED, copia=tmp_path / "s.json")
    )
    r = calendario.prossimi_giorni(OGGI, 10)
    fs = next(p for p in r.scioperi if p.sciopero.id == "3")
    assert any("Napoli" in e and "arrivo" in e for e in fs.eventi_coinvolti)
    assert "verifica sul sito dell'azienda" in fs.consiglio
    tpl = next(p for p in r.scioperi if p.sciopero.id == "7")
    assert any("arrivo e uscita" in e for e in tpl.eventi_coinvolti)
    assert any(f.nome.startswith("Ministero") and f.disponibile for f in r.fonti)


def test_senza_rete_usa_la_copia_e_poi_nulla(tmp_path):
    copia = tmp_path / "s.json"
    FonteScioperi(chiamata=lambda _u: FEED, copia=copia, adesso=lambda: OGGI).leggi()

    def guasto(_u):
        raise OSError("giù")

    lista, stato = FonteScioperi(chiamata=guasto, copia=copia).leggi()
    assert stato.copia and len(lista) == 3
    lista, stato = FonteScioperi(chiamata=guasto, copia=tmp_path / "manca.json").leggi()
    assert lista == [] and not stato.disponibile
