import { usePartite } from '../api/usePartite'

const MAX = 3

const giorno = new Intl.DateTimeFormat('it-IT', {
  weekday: 'short',
  day: 'numeric',
  month: 'short',
  hour: '2-digit',
  minute: '2-digit',
  timeZone: 'Europe/Rome',
})

const data = (iso: string) => new Date(iso).toLocaleString('it-IT', { timeZone: 'Europe/Rome' })

// Next home matches at the Maradona: real data from football-data.org, never simulated.
// Useful to the citizen: on match days Fuorigrotta and Linea 2 / Cumana are crowded.
export function PartiteMaradona() {
  const partite = usePartite()

  return (
    <section className="ct-card ct-card-matches">
      <div className="ct-card-head">
        <h2>Partite al Maradona</h2>
        <span className="badge badge-reliable">DATO REALE · football-data.org</span>
      </div>

      {!partite ? (
        <p className="ct-muted">Caricamento…</p>
      ) : !partite.disponibile ? (
        <p className="ct-muted">Calendario non disponibile: {partite.motivo}</p>
      ) : partite.partite.length === 0 ? (
        <p className="ct-muted">Nessuna partita al Maradona nei prossimi 60 giorni.</p>
      ) : (
        <ul className="ct-list">
          {partite.partite.slice(0, MAX).map((p) => (
            <li key={p.id} className="ct-match">
              <time dateTime={p.data_ora}>{giorno.format(new Date(p.data_ora))}</time>
              <span>
                <strong>
                  {p.casa} – {p.ospite}
                </strong>
                <small>{p.competizione}</small>
              </span>
            </li>
          ))}
        </ul>
      )}

      {partite?.disponibile && (
        <p className="ct-muted ct-small">
          {partite.copia ? 'Copia salvata del ' : 'Aggiornato il '}
          {partite.aggiornato_al ? data(partite.aggiornato_al) : '—'}
          {partite.copia && partite.motivo ? ` · ${partite.motivo}` : ''}
        </p>
      )}
    </section>
  )
}
