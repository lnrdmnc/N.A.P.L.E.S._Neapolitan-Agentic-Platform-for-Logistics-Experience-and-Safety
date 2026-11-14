"""Budget anti-allarme, cessato allarme operativo e conflitti mostrati una volta."""

import itertools

from napoles_agents.motore import Sessione


def _scenario_completo() -> Sessione:
    s = Sessione()
    for t in range(s.scenario["durata_min"] + 1):
        s.avanza(t)
        p = s.piano_corrente
        if p and p.stato == "proposto":
            s.approva(p.id)
    return s


def test_scossa_della_stessa_gravita_non_genera_notifiche():
    s = _scenario_completo()
    # La scossa Md 2.5 al minuto 101 non cambia gravità né istruzioni: nessun avviso a quel minuto.
    assert not [a for a in s.avvisi if a.sent_t_min == 101]


def test_linee_riattivate_generano_un_aggiornamento():
    s = _scenario_completo()
    a = next(a for a in s.avvisi if a.sent_t_min == 130 and a.pubblico == "residente")
    assert a.msgType == "Update" and "Di nuovo in servizio" in (a.instruction or "")


def test_cessato_allarme_chiude_ogni_profilo_e_rimanda_alla_protezione_civile():
    s = _scenario_completo()
    cancel = [a for a in s.avvisi if a.msgType == "Cancel"]
    assert {a.pubblico for a in cancel} == {"tifoso", "residente", "pendolare", "turista"}
    for a in cancel:
        precedente = next(p for p in s.avvisi if p.identifier == a.references)
        assert precedente.pubblico == a.pubblico and precedente.msgType != "Cancel"
        assert "Protezione Civile" in a.description or "Civil Protection" in a.description
        assert "evacu" not in a.description.lower()


def test_ogni_profilo_ha_una_catena_coerente():
    s = _scenario_completo()
    for pubblico in ("tifoso", "residente", "pendolare", "turista"):
        catena = [a for a in s.avvisi if a.pubblico == pubblico and a.event == "Evento sismico"]
        assert catena[0].msgType == "Alert" and catena[-1].msgType == "Cancel"
        for prima, dopo in itertools.pairwise(catena):
            assert dopo.references == prima.identifier


def test_conflitto_pubblicato_una_sola_volta_sul_bus():
    s = _scenario_completo()
    conflitti = [m for m in s.bus.messaggi if m.tipo == "conflitto"]
    assert len(conflitti) == 1
    assert sum(1 for p in s.piani if p.conflitti) > 1  # il piano continua a elencarlo


def test_pendolare_riceve_navette_per_l_area_flegrea_e_rimando_alla_protezione_civile():
    s = _scenario_completo()
    pendolare = [a for a in s.avvisi if a.pubblico == "pendolare"]
    sospese = next(a for a in pendolare if a.sent_t_min == 72)
    assert "Bagnoli e Pozzuoli" in sospese.instruction
    for a in pendolare:
        testo = f"{a.description} {a.instruction or ''}"
        assert "Protezione Civile" in testo
        assert "evacu" not in testo.lower()


def test_una_scossa_al_singolare():
    s = Sessione()
    s.avanza(70)
    s.approva(s.piano_corrente.id)
    testi = {a.lingua: a.description for a in s.avvisi}
    assert "una scossa" in testi["it"] and "1 scosse" not in testi["it"]
    assert "one tremor" in testi["en"]
