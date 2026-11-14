"""S0: simulatore a zone."""

from copy import deepcopy

from napoles_agents import scenario as sc
from napoles_agents.simulatore import Misure, misure_da_scenario, ripartisci, simula

S = sc.carica()
TOTALE = sum(s["spettatori"] for s in S["settori"])


def _serie(coordinato: bool):
    return simula(S, misure_da_scenario(S, coordinato))


def _zona(passo, zid):
    return next(z for z in passo.zone if z.id == zid)


def test_ripartisci_somma_esatta():
    for n in (0, 1, 7, 2500, 12345):
        assert sum(ripartisci(n, {"a": 0.55, "b": 0.2, "c": 0.1, "d": 0.15}).values()) == n


def test_persone_conservate_a_ogni_passo():
    for coordinato in (True, False):
        for p in _serie(coordinato).passi:
            in_zone = sum(z.persone for z in p.zone if z.id != "stadio")
            assert p.dentro_stadio + in_zone + p.arrivati == TOTALE


def test_capienza_superata_diventa_coda():
    for p in _serie(False).passi:
        for z in p.zone:
            assert z.in_coda == max(0, z.persone - z.capienza)
    assert any(z.in_coda > 0 for p in _serie(False).passi for z in p.zone)


def test_stessa_entrata_stessa_uscita():
    assert _serie(True) == _serie(True)


def test_senza_informazione_le_stazioni_chiuse_si_riempiono():
    picco = max(_zona(p, "stazione_campi_flegrei").persone for p in _serie(False).passi)
    assert picco > 0
    assert all(_zona(p, "stazione_campi_flegrei").persone == 0 for p in _serie(True).passi)


def test_coordinamento_sgombra_prima_e_con_meno_coda():
    def sgombro(serie):
        return next(
            p.t_min
            for p in serie.passi
            if p.t_min >= S["fine_partita_t_min"]
            and p.dentro_stadio == 0
            and sum(z.persone for z in p.zone if z.id != "stadio") <= 500
        )

    con, senza = _serie(True), _serie(False)
    assert sgombro(con) < sgombro(senza)
    picco = lambda serie: max(_zona(p, "piazzale_tecchio").carico for p in serie.passi)
    assert picco(con) < picco(senza)


def test_le_navette_compaiono_solo_quando_attive():
    m = misure_da_scenario(S, True)
    for p in simula(S, m).passi:
        attive = any(x.startswith("navette") for x in p.misure_attive)
        assert attive == (p.t_min >= m.navette_dal_t)


def test_linea_riattivata_torna_a_smaltire():
    # Nessuna informazione mai: chi è alla stazione aspetta finché la linea non riparte (minuto 130).
    serie = simula(S, Misure())
    prima = _zona(next(p for p in serie.passi if p.t_min == 125), "stazione_campi_flegrei").persone
    dopo = _zona(next(p for p in serie.passi if p.t_min == 140), "stazione_campi_flegrei").persone
    assert prima > 0 and dopo < prima


def test_senza_sospensioni_le_stazioni_smaltiscono_la_coda():
    # Dopo una partita una coda alle stazioni è normale; con le linee attive deve calare, non restare.
    s = deepcopy(S)
    s["eventi"] = [e for e in s["eventi"] if e["tipo"] != "sospensione_linea"]
    serie = simula(s, Misure())
    for zid in ("stazione_campi_flegrei", "stazione_mostra"):
        persone = [_zona(p, zid).persone for p in serie.passi]
        assert max(persone) > 0 and persone[-1] < max(persone)
