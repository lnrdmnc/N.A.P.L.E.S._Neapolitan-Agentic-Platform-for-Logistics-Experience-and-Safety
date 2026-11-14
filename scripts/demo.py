"""make demo (compito X1): un comando avvia tutto il percorso demo.

1. controlla i prerequisiti (uv, backend/.venv, frontend/node_modules) e che le porte siano libere;
2. legge .env, se c'è, e dice quali chiavi sono configurate (solo i nomi, mai i valori);
3. compila la PWA (frontend/dist);
4. avvia gli agenti sulla 8001, aspetta che rispondano e riporta la sessione al minuto 0;
5. avvia il gateway sulla 8000, che serve la PWA, e stampa gli indirizzi da aprire.

Ctrl+C ferma tutto; se uno dei due processi si ferma, si ferma anche l'altro.
Solo libreria standard: lo esegue il Python di backend/.venv, su macOS, Linux e Windows.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
PORTA_AGENTI = 8001
PORTA_WEB = 8000
CHIAVI = {
    "LLM_API_KEY": "testi scritti dall'AI (senza: testi a regole)",
    "MAPS_API_KEY": "traffico reale intorno allo stadio",
    "MAPS_JS_API_KEY": "mappa Google nel browser",
    "FOOTBALL_DATA_API_KEY": "partite dal vivo (senza: copia salvata)",
}
WINDOWS = os.name == "nt"


def messaggio(testo: str) -> None:
    print(f"demo: {testo}", flush=True)


def errore(testo: str) -> None:
    print(f"demo: ERRORE · {testo}", file=sys.stderr, flush=True)
    sys.exit(1)


def leggi_env(file: Path) -> dict[str, str]:
    valori: dict[str, str] = {}
    if not file.is_file():
        return valori
    for riga in file.read_text(encoding="utf-8").splitlines():
        riga = riga.strip()
        if not riga or riga.startswith("#") or "=" not in riga:
            continue
        nome, valore = riga.split("=", 1)
        valore = valore.strip().strip('"').strip("'")
        if valore:
            valori[nome.strip()] = valore
    return valori


def porta_libera(porta: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", porta)) != 0


def ip_locale() -> str | None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("192.0.2.1", 80))  # nessun pacchetto parte: serve solo a scegliere l'interfaccia
            return s.getsockname()[0]
    except OSError:
        return None


def aspetta(url: str, processo: subprocess.Popen, secondi: int = 60) -> None:
    fine = time.monotonic() + secondi
    while time.monotonic() < fine:
        if processo.poll() is not None:
            errore(f"il processo si è fermato prima di rispondere su {url}")
        try:
            urllib.request.urlopen(url, timeout=1)
            return
        except OSError:
            time.sleep(0.5)
    errore(f"nessuna risposta da {url} dopo {secondi} secondi")


def ferma(*processi: subprocess.Popen) -> None:
    for p in processi:
        if p.poll() is None:
            p.terminate()
    for p in processi:
        try:
            p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            p.kill()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Avvia il percorso demo di N.A.P.L.E.S.")
    parser.add_argument("--senza-build", action="store_true", help="usa frontend/dist già compilato")
    parser.add_argument("--apri", action="store_true", help="apre la control room nel browser")
    opzioni = parser.parse_args(argv)

    uv = shutil.which("uv")
    if not uv:
        errore("manca uv (https://docs.astral.sh/uv/)")
    if not (RADICE / "frontend" / "node_modules").is_dir():
        errore("manca frontend/node_modules: esegui make install")
    for porta in (PORTA_AGENTI, PORTA_WEB):
        if not porta_libera(porta):
            errore(f"la porta {porta} è occupata: chiudi make agents-run, make backend o una demo già avviata")

    env_file = leggi_env(RADICE / ".env")
    ambiente = {**os.environ, **env_file}
    messaggio(".env trovato" if (RADICE / ".env").is_file() else ".env assente: si usano copie salvate e testi a regole")
    for nome, uso in CHIAVI.items():
        messaggio(f"  {'sì' if ambiente.get(nome) else 'no'} · {nome}: {uso}")

    if not opzioni.senza_build:
        messaggio("compilo la PWA (frontend/dist)…")
        npm = shutil.which("npm") or "npm"
        if subprocess.run([npm, "run", "build"], cwd=RADICE / "frontend", shell=WINDOWS).returncode != 0:
            errore("build del frontend fallita")
    if not (RADICE / "frontend" / "dist" / "index.html").is_file():
        errore("manca frontend/dist: togli --senza-build")

    agenti = subprocess.Popen(
        [uv, "run", "--quiet", "uvicorn", "napoles_agents.api:app", "--app-dir", "src", "--port", str(PORTA_AGENTI)]
        + ["--timeout-graceful-shutdown", "3"],
        cwd=RADICE / "agents",
        env={**ambiente, "PYTHONPATH": "src"},
    )
    try:
        aspetta(f"http://127.0.0.1:{PORTA_AGENTI}/api/stato", agenti)
        richiesta = urllib.request.Request(f"http://127.0.0.1:{PORTA_AGENTI}/api/reset", method="POST", data=b"")
        stato = json.loads(urllib.request.urlopen(richiesta, timeout=10).read())
        messaggio(f"agenti pronti sulla {PORTA_AGENTI}, scenario al minuto {stato['t_min']} ({stato['ora']})")

        gateway = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", str(PORTA_WEB), "--timeout-graceful-shutdown", "3"],
            cwd=RADICE / "backend",
            env={**ambiente, "AGENTS_URL": f"http://127.0.0.1:{PORTA_AGENTI}"},
        )
    except BaseException:
        ferma(agenti)
        raise
    try:
        aspetta(f"http://127.0.0.1:{PORTA_WEB}/api/health", gateway)
        locale = f"http://localhost:{PORTA_WEB}"
        messaggio("pronto. Apri:")
        messaggio(f"  control room  {locale}/control-room")
        messaggio(f"  cittadino     {locale}/cittadino")
        if ip := ip_locale():
            messaggio(f"  dal telefono sulla stessa Wi-Fi: http://{ip}:{PORTA_WEB}/cittadino")
        messaggio("Ctrl+C per fermare.")
        if opzioni.apri:
            webbrowser.open(f"{locale}/control-room")
        while agenti.poll() is None and gateway.poll() is None:
            time.sleep(1)
        messaggio("un processo si è fermato: chiudo anche l'altro")
        return 1
    except KeyboardInterrupt:
        messaggio("fermo la demo")
        return 0
    finally:
        ferma(gateway, agenti)


if __name__ == "__main__":
    sys.exit(main())
