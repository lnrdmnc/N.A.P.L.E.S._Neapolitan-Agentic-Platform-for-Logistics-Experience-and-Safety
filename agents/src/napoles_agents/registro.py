"""Registro delle decisioni a catena di hash: ogni voce contiene l'hash della precedente.

Con un file, ogni voce viene anche scritta subito su disco, una riga JSON per voce (JSONL).
Chiunque può poi verificare il file senza fidarsi del programma che l'ha scritto:

    make verifica-registro                    # verifica agents/var/registro.jsonl
    python -m napoles_agents.registro verifica percorso/del/registro.jsonl

Se una riga viene cambiata, tolta, aggiunta o spostata, la verifica fallisce e indica la prima
riga che non torna.
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .models import VoceRegistro

GENESI = "0" * 64
FILE_PREDEFINITO = Path(__file__).resolve().parents[2] / "var" / "registro.jsonl"


def _hash(indice: int, t_min: int, tipo: str, contenuto: dict[str, Any], precedente: str) -> str:
    corpo = json.dumps(
        {"indice": indice, "t_min": t_min, "tipo": tipo, "contenuto": contenuto, "prec": precedente},
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(corpo.encode("utf-8")).hexdigest()


def verifica_voci(voci: list[VoceRegistro]) -> tuple[bool, int | None]:
    """Ritorna (integro, posizione della prima voce che non torna)."""
    precedente = GENESI
    for posizione, v in enumerate(voci):
        atteso = _hash(v.indice, v.t_min, v.tipo, v.contenuto, precedente)
        if v.indice != posizione or v.hash_precedente != precedente or v.hash != atteso:
            return False, posizione
        precedente = v.hash
    return True, None


class Registro:
    def __init__(self, file: Path | None = None) -> None:
        self.voci: list[VoceRegistro] = []
        self.file = file
        if file is not None:
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text("", encoding="utf-8")  # una sessione nuova, un registro nuovo

    def aggiungi(self, t_min: int, tipo: str, contenuto: dict[str, Any]) -> VoceRegistro:
        precedente = self.voci[-1].hash if self.voci else GENESI
        indice = len(self.voci)
        voce = VoceRegistro(
            indice=indice,
            t_min=t_min,
            tipo=tipo,
            contenuto=contenuto,
            hash_precedente=precedente,
            hash=_hash(indice, t_min, tipo, contenuto, precedente),
        )
        self.voci.append(voce)
        if self.file is not None:
            with self.file.open("a", encoding="utf-8") as f:
                f.write(voce.model_dump_json() + "\n")
        return voce

    def verifica(self) -> tuple[bool, int | None]:
        """Ritorna (integro, indice della prima voce alterata)."""
        return verifica_voci(self.voci)


def verifica_file(file: Path) -> tuple[bool, str]:
    """Verifica un registro su file. Ritorna (integro, messaggio per una persona)."""
    if not file.exists():
        return False, f"{file}: non esiste. Avvia la demo (make agents-run) o esegui make prova."
    voci: list[VoceRegistro] = []
    for numero, riga in enumerate(file.read_text(encoding="utf-8").splitlines(), start=1):
        if not riga.strip():
            continue
        try:
            voci.append(VoceRegistro.model_validate_json(riga))
        except ValidationError:
            return False, f"Riga {numero}: non è una voce valida del registro (formato alterato)."
    if not voci:
        return False, f"{file}: registro vuoto."
    integro, posizione = verifica_voci(voci)
    if integro:
        return True, f"Registro integro: {len(voci)} voci, ultima catena {voci[-1].hash[:12]}…"
    v = voci[posizione]
    return False, (
        f"Registro ALTERATO alla riga {posizione + 1} (voce «{v.tipo}» al minuto {v.t_min}): "
        "il contenuto o l'ordine non corrisponde alla catena di hash."
    )


def main(argomenti: list[str]) -> int:
    if not argomenti or argomenti[0] != "verifica":
        print("Uso: python -m napoles_agents.registro verifica [file.jsonl]")
        return 2
    file = Path(argomenti[1]) if len(argomenti) > 1 else FILE_PREDEFINITO
    integro, messaggio = verifica_file(file)
    print(messaggio)
    return 0 if integro else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
