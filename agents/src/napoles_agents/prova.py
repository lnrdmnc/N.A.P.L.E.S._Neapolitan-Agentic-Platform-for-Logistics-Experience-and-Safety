"""Strumento di prova del team (compito P1). Uso: `make prova`.

Esegue lo scenario tre volte, con tre comportamenti dell'operatore, e salva per ognuna un
rapporto leggibile in docs/prove/:

- `subito`: approva ogni piano appena proposto;
- `tardi`: approva un piano solo dopo che è rimasto in attesa per 10 minuti;
- `mai`: non approva nulla.

Ogni rapporto contiene i controlli automatici, la linea del tempo dei messaggi tra agenti,
i piani con impatto, gli avvisi per profilo e gli indicatori. Va letto a mano cercando
decisioni assurde, ripetute o vaghe (docs/PIANO.md, P1). Nessuna rete: pochi secondi.
"""

import itertools
import sys
from collections import Counter
from pathlib import Path

from .models import Caso
from .motore import Sessione
from .registro import FILE_PREDEFINITO
from .simulazione import _deflusso, confronta, sensibilita

CARTELLA = Path(__file__).resolve().parents[3] / "docs" / "prove"
RITARDO_TARDI = 10
STRATEGIE = {
    "subito": "approva ogni piano appena proposto",
    "tardi": f"approva un piano solo dopo {RITARDO_TARDI} minuti di attesa",
    "mai": "non approva nulla",
}


def esegui(strategia: str, file_registro: Path | None = None) -> Sessione:
    s = Sessione(file_registro=file_registro)
    for t in range(s.scenario["durata_min"] + 1):
        s.avanza(t)
        p = s.piano_corrente
        if not p or p.stato not in ("proposto", "modificato"):
            continue
        if strategia == "subito" or (strategia == "tardi" and t - p.t_min >= RITARDO_TARDI):
            s.approva(p.id, operatore=f"prova ({strategia})")
    return s


def controlli(s: Sessione) -> list[tuple[bool, str]]:
    testi = [f"{a.headline} {a.description} {a.instruction or ''}" for a in s.avvisi]
    ufficiali = [e for e in s.stato.eventi if e.testo_ufficiale]
    inoltri_ok = all(
        any(a.ufficiale and a.description == e.testo_ufficiale for a in s.avvisi) for e in ufficiali
    ) or not any(a.ufficiale for a in s.avvisi)
    ripetuti = 0
    for pubblico in {a.pubblico for a in s.avvisi}:
        catena = [a for a in s.avvisi if a.pubblico == pubblico]
        ripetuti += sum(
            1
            for prima, dopo in itertools.pairwise(catena)
            if (prima.description, prima.instruction) == (dopo.description, dopo.instruction)
        )
    notizie = {p.id for piano in s.piani for p in piano.proposte if p.caso == Caso.C_NON_VERIFICATO}
    # Il testo della voce stessa, tra «», non il nome del quartiere: «Bagnoli» compare anche,
    # legittimamente, nelle navette dei pendolari.
    voci = [
        e.titolo.split("«", 1)[1].split("»", 1)[0]
        for e in s.stato.eventi
        if e.affidabilita.value == "non_verificata" and "«" in e.titolo
    ]
    integro, _ = s.registro.verifica()
    senza_decisione = sum(1 for p in s.piani if p.stato == "superato")
    return [
        (not any("evacu" in t.lower() for t in testi), "Nessuna istruzione di evacuazione negli avvisi"),
        (
            not any(v in t for v in voci for t in testi),
            "Le notizie non verificate non sono mai diventate un avviso"
            + (f" ({len(notizie)} segnalate all'operatore)" if notizie else ""),
        ),
        (inoltri_ok, "Le allerte ufficiali inoltrate hanno il testo originale identico"),
        (ripetuti == 0, f"Avvisi identici ripetuti allo stesso profilo: {ripetuti}"),
        (integro, "Registro delle decisioni integro"),
        (True, f"Piani superati da fatti nuovi prima di una decisione: {senza_decisione} (informativo)"),
    ]


def rapporto(strategia: str, s: Sessione) -> str:
    sc_ = s.scenario
    righe = [
        f"# Prova «{strategia}» — {STRATEGIE[strategia]}",
        "",
        (
            f"Scenario: {sc_['titolo']} · {sc_['durata_min']} minuti dalle {sc_['ora_inizio']}. "
            "Tutto simulato. Rapporto generato da `make prova`: non modificarlo a mano."
        ),
        "",
        "## Controlli automatici",
        "",
    ]
    righe += [f"- {'✅' if ok else '⚠️'} {testo}" for ok, testo in controlli(s)]

    stati = Counter(p.stato for p in s.piani)
    pubblici = Counter(a.pubblico for a in s.avvisi)
    sgombero = _deflusso(sc_, s.simulazione())
    c = confronta(sc_, s.approvati, s.avvisi)
    righe += [
        "",
        "## In sintesi",
        "",
        f"- Piani: {len(s.piani)} ({', '.join(f'{k} {v}' for k, v in sorted(stati.items()))})",
        f"- Avvisi inviati: {len(s.avvisi)} ({', '.join(f'{k} {v}' for k, v in sorted(pubblici.items()))})",
        f"- Messaggi tra agenti: {len(s.bus.messaggi)}; voci nel registro: {len(s.registro.voci)}",
        "- Area dello stadio sgombra (città di questa sessione): "
        + (f"{sgombero} minuti dopo il fischio finale" if sgombero is not None else "non entro la fine"),
        (
            f"- Indicatori «con coordinamento» ({c.con_coordinamento.origine['minuti_decisione']}): "
            f"sgombero {c.con_coordinamento.deflusso_min} min, picco {c.con_coordinamento.picco_attesa_persone} "
            f"persone; «senza»: {c.senza_coordinamento.deflusso_min} min, "
            f"{c.senza_coordinamento.picco_attesa_persone} persone"
        ),
        "",
        "## Da leggere a mano",
        "",
        "- [ ] Ci sono decisioni assurde (navette nel posto sbagliato, ondate dopo che lo stadio è vuoto)?",
        "- [ ] Ci sono messaggi ripetuti o che non aggiungono nulla?",
        "- [ ] Ci sono testi vaghi, allarmisti o che parlano del rischio invece che del servizio?",
        "- [ ] Ogni avviso dice da dove viene l'informazione?",
        "",
        "## Linea del tempo dei messaggi",
        "",
        "| # | Ora | Tipo | Da → A | Messaggio |",
        "| --- | --- | --- | --- | --- |",
    ]
    for m in s.bus.messaggi:
        etichetta = f" *({m.affidabilita.value})*" if m.affidabilita else ""
        righe.append(f"| {m.seq} | {m.ora} | {m.tipo} | {m.da} → {m.a} | {m.titolo}{etichetta} |")

    righe += ["", "## Piani", ""]
    for p in s.piani:
        decisione = f", deciso alle min {p.t_decisione}" if p.t_decisione is not None else ""
        righe += [f"### {p.id} — minuto {p.t_min}, {p.stato}{decisione}", "", p.sintesi, ""]
        righe += [
            f"- [{q.agente.value}] {q.titolo} *(priorità {q.priorita}, {q.affidabilita.value})*"
            for q in p.proposte
        ]
        if p.impatto:
            peggiori = sorted(p.impatto.zone, key=lambda z: -z.picco_carico_senza_piano)[:3]
            righe.append(
                "- Impatto stimato (picco di carico senza → con il piano): "
                + "; ".join(
                    f"{z.zona} {z.picco_carico_senza_piano} → {z.picco_carico_con_piano}" for z in peggiori
                )
            )
        righe.append("")

    righe += ["## Avvisi per profilo", ""]
    for pubblico in sorted({a.pubblico for a in s.avvisi}):
        righe += [f"### {pubblico}", ""]
        for a in (a for a in s.avvisi if a.pubblico == pubblico):
            righe.append(f"- **min {a.sent_t_min} · {a.msgType}** — {a.headline}")
            righe.append(f"  - {a.description}")
            if a.instruction:
                righe.append(f"  - *Istruzioni:* {a.instruction}")
            righe.append(
                f"  - *Fonte:* {a.source}"
                + (" · **allerta ufficiale, testo non modificato**" if a.ufficiale else "")
            )
        righe.append("")
    if not s.avvisi:
        righe += ["Nessun avviso inviato: nessun piano approvato.", ""]
    return "\n".join(righe)


def main(argomenti: list[str]) -> int:
    scelte = argomenti or ["tutte"]
    strategie = list(STRATEGIE) if scelte == ["tutte"] else scelte
    sconosciute = [x for x in strategie if x not in STRATEGIE]
    if sconosciute:
        print(f"Strategie sconosciute: {', '.join(sconosciute)}. Valide: {', '.join(STRATEGIE)}, tutte")
        return 2
    CARTELLA.mkdir(parents=True, exist_ok=True)
    esito = 0
    for strategia in strategie:
        s = esegui(strategia, FILE_PREDEFINITO if strategia == "subito" else None)
        percorso = CARTELLA / f"prova-{strategia}.md"
        percorso.write_text(rapporto(strategia, s) + "\n", encoding="utf-8")
        avvisi_controlli = controlli(s)
        falliti = [t for ok, t in avvisi_controlli if not ok]
        esito |= 1 if falliti else 0
        sgombero = _deflusso(s.scenario, s.simulazione())
        print(
            f"{strategia:6s} · piani {len(s.piani):2d} · avvisi {len(s.avvisi):2d} · sgombero "
            f"{sgombero if sgombero is not None else '—'} min · controlli "
            f"{'ok' if not falliti else 'DA GUARDARE: ' + '; '.join(falliti)} → {percorso.relative_to(CARTELLA.parents[1])}"
        )
    print(f"Registro della prova «subito» in {FILE_PREDEFINITO}: verificalo con make verifica-registro")
    print("\nSensibilità (fattore percorsi a piedi, decisione senza coordinamento):")
    for r in sensibilita(Sessione().scenario):
        print(
            f"  fattore {r['fattore_percorsi_piedi']}, decisione {r['decisione_senza_min']} min: "
            f"sgombero {r['deflusso_con']} → {r['deflusso_senza']} min, picco {r['picco_con']} → {r['picco_senza']}"
        )
    return esito


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
