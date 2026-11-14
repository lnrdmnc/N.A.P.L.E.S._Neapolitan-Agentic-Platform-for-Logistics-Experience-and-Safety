"""Bus dei messaggi della sessione: chi dice cosa a chi, in ordine. La control room lo osserva."""

from .models import Affidabilita, Messaggio, TipoMessaggio


class Bus:
    def __init__(self) -> None:
        self.messaggi: list[Messaggio] = []

    def pubblica(
        self,
        t_min: int,
        ora: str,
        da: str,
        a: str,
        tipo: TipoMessaggio,
        titolo: str,
        testo: str,
        affidabilita: Affidabilita | None = None,
        simulato: bool = True,
        rif: str | None = None,
    ) -> Messaggio:
        m = Messaggio(
            seq=len(self.messaggi) + 1,
            t_min=t_min,
            ora=ora,
            da=da,
            a=a,
            tipo=tipo,
            titolo=titolo,
            testo=testo,
            affidabilita=affidabilita,
            simulato=simulato,
            rif=rif,
        )
        self.messaggi.append(m)
        return m

    def da(self, seq: int = 0) -> list[Messaggio]:
        """Messaggi con numero maggiore di `seq`: la web app passa l'ultimo che ha già."""
        return [m for m in self.messaggi if m.seq > seq]
