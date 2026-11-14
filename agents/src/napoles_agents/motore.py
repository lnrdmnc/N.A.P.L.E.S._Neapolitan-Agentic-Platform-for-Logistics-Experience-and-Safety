"""Sessione demo: fa avanzare lo scenario, chiama gli agenti, gestisce approvazioni e registro."""

from typing import Any

from . import scenario as sc
from .agenti import AGENTI
from .agenti.comunicazione import prepara_avvisi
from .agenti.orchestratore import pianifica
from .models import Alert, Piano, Proposta, StatoCitta
from .registro import Registro


class Sessione:
    def __init__(self, nome_scenario: str = "scenario_maradona") -> None:
        self.nome_scenario = nome_scenario
        self.scenario: dict[str, Any] = sc.carica(nome_scenario)
        self.t_min = -1
        self.piani: list[Piano] = []
        self.avvisi: list[Alert] = []
        self.registro = Registro()
        self._firma: tuple = ()
        self._eventi_visti: set[str] = set()
        self.avanza(0)

    @property
    def stato(self) -> StatoCitta:
        return sc.stato(self.scenario, self.t_min)

    @property
    def piano_corrente(self) -> Piano | None:
        return self.piani[-1] if self.piani else None

    def proposte(self) -> list[Proposta]:
        stato = self.stato
        return [p for agente in AGENTI for p in agente(stato, self.scenario)]

    def avanza(self, t_min: int) -> StatoCitta:
        """Porta la simulazione al minuto t_min. Tornare indietro riparte da zero."""
        if t_min < self.t_min:
            self.__init__(self.nome_scenario)
        for minuto in range(max(self.t_min + 1, 0), t_min + 1):
            self.t_min = minuto
            self._passo()
        return self.stato

    def _passo(self) -> None:
        stato = self.stato
        for e in stato.eventi:
            if e.id not in self._eventi_visti:
                self._eventi_visti.add(e.id)
                self.registro.aggiungi(
                    self.t_min,
                    "evento",
                    {"id": e.id, "titolo": e.titolo, "fonte": e.fonte, "affidabilita": e.affidabilita.value},
                )
        proposte = self.proposte()
        firma = tuple(sorted((p.id, repr(sorted(p.dettagli.items()))) for p in proposte))
        if not proposte or firma == self._firma:
            return
        self._firma = firma
        corrente = self.piano_corrente
        if corrente and corrente.stato == "proposto":
            corrente.stato = "superato"
        piano = pianifica(proposte, self.t_min, len(self.piani) + 1)
        self.piani.append(piano)
        self.registro.aggiungi(
            self.t_min,
            "piano_proposto",
            {"piano": piano.id, "azioni": [p.id for p in piano.proposte], "sintesi": piano.sintesi},
        )

    def _trova(self, piano_id: str) -> Piano:
        for p in self.piani:
            if p.id == piano_id:
                return p
        raise KeyError(piano_id)

    def approva(self, piano_id: str, operatore: str = "operatore") -> list[Alert]:
        piano = self._trova(piano_id)
        if piano.stato != "proposto":
            raise ValueError(f"Il piano {piano_id} è {piano.stato}: non si può approvare")
        piano.stato = "approvato"
        piano.t_decisione = self.t_min
        self.registro.aggiungi(self.t_min, "piano_approvato", {"piano": piano.id, "operatore": operatore})
        nuovi = prepara_avvisi(piano, self.stato, self.scenario, self.avvisi)
        self.avvisi.extend(nuovi)
        for a in nuovi:
            self.registro.aggiungi(
                self.t_min,
                "avviso_inviato",
                {
                    "avviso": a.identifier,
                    "pubblico": a.pubblico,
                    "ufficiale": a.ufficiale,
                    "headline": a.headline,
                },
            )
        return nuovi

    def rifiuta(self, piano_id: str, operatore: str = "operatore", motivo: str = "") -> Piano:
        piano = self._trova(piano_id)
        if piano.stato != "proposto":
            raise ValueError(f"Il piano {piano_id} è {piano.stato}: non si può rifiutare")
        piano.stato = "rifiutato"
        piano.t_decisione = self.t_min
        self.registro.aggiungi(
            self.t_min, "piano_rifiutato", {"piano": piano.id, "operatore": operatore, "motivo": motivo}
        )
        return piano
