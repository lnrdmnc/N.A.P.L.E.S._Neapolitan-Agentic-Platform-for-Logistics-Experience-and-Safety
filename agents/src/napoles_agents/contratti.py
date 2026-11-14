"""Genera i contratti in contracts/ dai modelli e dall'API. Uso: `make contracts`."""

import json
from pathlib import Path

from .api import app

RADICE = Path(__file__).resolve().parents[3]
CONTRATTI = RADICE / "contracts"


def openapi() -> str:
    return json.dumps(app.openapi(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main() -> None:
    CONTRATTI.mkdir(exist_ok=True)
    (CONTRATTI / "agenti.openapi.json").write_text(openapi(), encoding="utf-8")
    print(f"scritto {CONTRATTI / 'agenti.openapi.json'}")


if __name__ == "__main__":
    main()
