"""R1: registro delle decisioni su file e verifica."""

import json

from napoles_agents.motore import Sessione
from napoles_agents.registro import main, verifica_file


def _sessione_su_file(tmp_path):
    file = tmp_path / "registro.jsonl"
    s = Sessione(file_registro=file)
    s.avanza(72)
    s.approva(s.piano_corrente.id)
    return s, file


def test_il_file_contiene_una_riga_per_voce(tmp_path):
    s, file = _sessione_su_file(tmp_path)
    righe = file.read_text(encoding="utf-8").splitlines()
    assert len(righe) == len(s.registro.voci)
    assert json.loads(righe[-1])["hash"] == s.registro.voci[-1].hash


def test_file_integro(tmp_path):
    _, file = _sessione_su_file(tmp_path)
    assert verifica_file(file)[0] is True
    assert main(["verifica", str(file)]) == 0


def test_riga_cambiata_a_mano(tmp_path):
    _, file = _sessione_su_file(tmp_path)
    righe = file.read_text(encoding="utf-8").splitlines()
    righe[3] = righe[3].replace('"t_min":', '"t_min":1', 1)
    file.write_text("\n".join(righe) + "\n", encoding="utf-8")
    integro, messaggio = verifica_file(file)
    assert not integro and "riga 4" in messaggio
    assert main(["verifica", str(file)]) == 1


def test_riga_tolta(tmp_path):
    _, file = _sessione_su_file(tmp_path)
    righe = file.read_text(encoding="utf-8").splitlines()
    del righe[2]
    file.write_text("\n".join(righe) + "\n", encoding="utf-8")
    assert verifica_file(file)[0] is False


def test_righe_scambiate(tmp_path):
    _, file = _sessione_su_file(tmp_path)
    righe = file.read_text(encoding="utf-8").splitlines()
    righe[1], righe[2] = righe[2], righe[1]
    file.write_text("\n".join(righe) + "\n", encoding="utf-8")
    assert verifica_file(file)[0] is False


def test_riga_non_valida(tmp_path):
    _, file = _sessione_su_file(tmp_path)
    with file.open("a", encoding="utf-8") as f:
        f.write("non è json\n")
    integro, messaggio = verifica_file(file)
    assert not integro and "formato" in messaggio


def test_file_mancante(tmp_path):
    assert verifica_file(tmp_path / "manca.jsonl")[0] is False


def test_tornare_indietro_riparte_con_un_registro_nuovo(tmp_path):
    s, file = _sessione_su_file(tmp_path)
    s.avanza(10)  # tornare indietro riparte da zero
    assert verifica_file(file)[0] is True
    assert len(file.read_text(encoding="utf-8").splitlines()) == len(s.registro.voci)
