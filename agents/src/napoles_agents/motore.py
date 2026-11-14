"""Sessione demo: fa avanzare lo scenario, chiama gli agenti, gestisce approvazioni e registro."""

from pathlib import Path
from typing import Any

from . import riferimento
from . import scenario as sc
from .agenti import AGENTI
from .agenti.comunicazione import prepara_avvisi
from .agenti.orchestratore import pianifica
from .bus import Bus
from .decisioni import impatto, misure_da_decisioni
from .luoghi import luogo
from .models import Alert, Caso, Piano, Proposta, SerieSimulazione, StatoCitta
from .registro import Registro
from .ricezione import Ricezioni
from .simulatore import simula

# Stati in cui il piano aspetta la decisione dell'operatore.
IN_ATTESA = ("proposto", "modificato")

NOMI_AGENTI = {
    "rischio": "Rischio",
    "mobilita": "Mobilità",
    "folla": "Folla",
    "comunicazione": "Comunicazione",
}


class Sessione:
    def __init__(self, nome_scenario: str = "scenario_maradona", file_registro: Path | None = None) -> None:
        self.nome_scenario = nome_scenario
        self.scenario: dict[str, Any] = sc.carica(nome_scenario)
        self.t_min = -1
        self.piani: list[Piano] = []
        self.avvisi: list[Alert] = []
        self.file_registro = file_registro
        self.registro = Registro(file_registro)
        self.bus = Bus()
        self.ricezioni = Ricezioni()
        self._firma: tuple = ()
        self._eventi_visti: set[str] = set()
        self._proposte_viste: dict[str, str] = {}
        self._conflitti_visti: set[tuple[str, ...]] = set()
        self.avanza(0)

    def _pubblica(self, **campi: Any) -> None:
        self.bus.pubblica(t_min=self.t_min, ora=sc.ora(self.scenario, self.t_min), **campi)

    @property
    def stato(self) -> StatoCitta:
        stato = sc.stato(self.scenario, self.t_min)
        stato.partita_reale = riferimento.partita_reale()
        return stato

    @property
    def piano_corrente(self) -> Piano | None:
        return self.piani[-1] if self.piani else None

    @property
    def approvati(self) -> list[Piano]:
        return [p for p in self.piani if p.stato == "approvato"]

    def simulazione(self) -> SerieSimulazione:
        """La città secondo le decisioni approvate fin qui (proiezione fino a fine scenario)."""
        return simula(self.scenario, misure_da_decisioni(self.scenario, self.approvati), "sessione")

    def proposte(self) -> list[Proposta]:
        stato = self.stato
        return [p for agente in AGENTI for p in agente(stato, self.scenario)]

    def avanza(self, t_min: int) -> StatoCitta:
        """Porta la simulazione al minuto t_min. Tornare indietro riparte da zero."""
        if t_min < self.t_min:
            self.__init__(self.nome_scenario, self.file_registro)
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
                self._pubblica(
                    da=e.fonte,
                    a="agenti",
                    tipo="evento",
                    titolo=e.titolo,
                    testo=f"{e.titolo} ({e.zona}). Affidabilità: {e.affidabilita.value}.",
                    affidabilita=e.affidabilita,
                    simulato=e.simulato,
                    rif=e.id,
                )
        proposte = self.proposte()
        for p in proposte:
            impronta = repr(sorted(p.dettagli.items()))
            if self._proposte_viste.get(p.id) != impronta:
                self._proposte_viste[p.id] = impronta
                self._pubblica(
                    da=NOMI_AGENTI[p.agente.value],
                    a="Orchestratore",
                    tipo="proposta",
                    titolo=p.titolo,
                    testo=p.motivazione,
                    affidabilita=p.affidabilita,
                    rif=p.id,
                )
        firma = tuple(sorted((p.id, repr(sorted(p.dettagli.items()))) for p in proposte))
        if not proposte or firma == self._firma:
            return
        self._firma = firma
        corrente = self.piano_corrente
        if corrente and corrente.stato in IN_ATTESA:
            corrente.stato = "superato"
        piano = pianifica(proposte, self.t_min, len(self.piani) + 1)
        piano.impatto = impatto(self.scenario, self.approvati, piano, self.t_min)
        self.piani.append(piano)
        self.registro.aggiungi(
            self.t_min,
            "piano_proposto",
            {"piano": piano.id, "azioni": [p.id for p in piano.proposte], "sintesi": piano.sintesi},
        )
        for c in piano.conflitti:
            # Il piano elenca sempre i suoi conflitti; sulla linea del tempo compaiono una volta sola.
            chiave = (c.risorsa, *c.proposte)
            if chiave in self._conflitti_visti:
                continue
            self._conflitti_visti.add(chiave)
            per_id = {p.id: p for p in piano.proposte}
            coinvolti = [NOMI_AGENTI[per_id[pid].agente.value] for pid in c.proposte if pid in per_id]
            self._pubblica(
                da="Orchestratore",
                a=", ".join(coinvolti) or "agenti",
                tipo="conflitto",
                titolo=f"Conflitto su {luogo(c.risorsa)}",
                testo=c.risoluzione,
                rif=piano.id,
            )
        self._pubblica(
            da="Orchestratore",
            a="Operatore",
            tipo="piano",
            titolo=f"Piano {piano.id}: {len(piano.proposte)} azioni da approvare",
            testo=piano.sintesi,
            affidabilita=piano.affidabilita_minima,
            rif=piano.id,
        )

    def _trova(self, piano_id: str) -> Piano:
        for p in self.piani:
            if p.id == piano_id:
                return p
        raise KeyError(piano_id)

    def modifica(
        self, piano_id: str, proposte_escluse: list[str], motivo: str = "", operatore: str = "operatore"
    ) -> Piano:
        """L'operatore toglie una o più proposte prima di approvare. Il piano resta in attesa
        di approvazione («modificato»); le proposte tolte non generano avvisi."""
        piano = self._trova(piano_id)
        if piano.stato not in IN_ATTESA:
            raise ValueError(f"Il piano {piano_id} è {piano.stato}: non si può modificare")
        tutte = piano.proposte + piano.proposte_escluse
        escluse = set(proposte_escluse)
        sconosciute = escluse - {p.id for p in tutte}
        if sconosciute:
            raise KeyError(", ".join(sorted(sconosciute)))
        ufficiali = [p.id for p in tutte if p.id in escluse and p.caso == Caso.A_UFFICIALE]
        if ufficiali:
            raise ValueError("Le allerte ufficiali non si possono escludere: vanno sempre inoltrate")
        rimaste = [p for p in tutte if p.id not in escluse]
        ricalcolato = pianifica(rimaste, piano.t_min, 0)
        piano.proposte = ricalcolato.proposte
        piano.conflitti = ricalcolato.conflitti
        piano.sintesi = ricalcolato.sintesi
        piano.sintesi_modello = ricalcolato.sintesi_modello
        piano.affidabilita_minima = ricalcolato.affidabilita_minima
        piano.proposte_escluse = [p for p in tutte if p.id in escluse]
        piano.motivo_modifica = motivo or None
        piano.stato = "modificato"
        piano.impatto = impatto(self.scenario, self.approvati, piano, self.t_min)
        titoli = ", ".join(p.titolo for p in piano.proposte_escluse) or "nessuna"
        self.registro.aggiungi(
            self.t_min,
            "piano_modificato",
            {
                "piano": piano.id,
                "operatore": operatore,
                "escluse": sorted(escluse),
                "motivo": motivo,
            },
        )
        self._pubblica(
            da="Operatore",
            a="Orchestratore",
            tipo="decisione",
            titolo=f"Piano {piano.id} modificato",
            testo=f"Escluse da {operatore}: {titoli}." + (f" Motivo: {motivo}" if motivo else ""),
            simulato=False,
            rif=piano.id,
        )
        return piano

    def approva(self, piano_id: str, operatore: str = "operatore") -> list[Alert]:
        piano = self._trova(piano_id)
        if piano.stato not in IN_ATTESA:
            raise ValueError(f"Il piano {piano_id} è {piano.stato}: non si può approvare")
        piano.stato = "approvato"
        piano.t_decisione = self.t_min
        self.registro.aggiungi(self.t_min, "piano_approvato", {"piano": piano.id, "operatore": operatore})
        self._pubblica(
            da="Operatore",
            a="Orchestratore",
            tipo="decisione",
            titolo=f"Piano {piano.id} approvato",
            testo=f"Approvato da {operatore}.",
            simulato=False,
            rif=piano.id,
        )
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
            self._pubblica(
                da="Comunicazione",
                a=f"Pubblico: {a.pubblico} ({a.lingua})",
                tipo="avviso",
                titolo=a.headline,
                testo=a.description + (f" {a.instruction}" if a.instruction else ""),
                simulato=a.simulato,
                rif=a.identifier,
            )
        return nuovi

    def rifiuta(self, piano_id: str, operatore: str = "operatore", motivo: str = "") -> Piano:
        piano = self._trova(piano_id)
        if piano.stato not in IN_ATTESA:
            raise ValueError(f"Il piano {piano_id} è {piano.stato}: non si può rifiutare")
        piano.stato = "rifiutato"
        piano.t_decisione = self.t_min
        self.registro.aggiungi(
            self.t_min, "piano_rifiutato", {"piano": piano.id, "operatore": operatore, "motivo": motivo}
        )
        self._pubblica(
            da="Operatore",
            a="Orchestratore",
            tipo="decisione",
            titolo=f"Piano {piano.id} rifiutato",
            testo=f"Rifiutato da {operatore}." + (f" Motivo: {motivo}" if motivo else ""),
            simulato=False,
            rif=piano.id,
        )
        return piano
