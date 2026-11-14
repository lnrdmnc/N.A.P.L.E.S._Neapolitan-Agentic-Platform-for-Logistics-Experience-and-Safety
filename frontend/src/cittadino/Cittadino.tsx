import { toNotices } from '../api/notices'
import { useLiveEvents } from '../api/useLiveEvents'
import { useStato } from '../api/useStato'
import { LiveStatus } from '../components/LiveStatus'
import { SimulationBadge } from '../components/SimulationBadge'
import './Cittadino.css'

export function Cittadino() {
  const { status, events } = useLiveEvents()
  const { stato } = useStato()
  const notices = toNotices(events)
  const latest = notices[0]

  return (
    <div className="ct">
      <header className="ct-header">
        <span className="ct-logo">N.A.P.L.E.S.</span>
        <LiveStatus status={status} inverse />
      </header>

      <div className="ct-sim">
        <SimulationBadge label="DEMO · eventi simulati" />
      </div>

      {latest && (
        <section className="ct-banner" role="alert">
          <div className="ct-banner-head">
            <strong>{latest.title}</strong>
            {latest.simulated && <SimulationBadge label="simulato" />}
          </div>
          <p>{latest.body}</p>
          <small>
            Fonte: {latest.source} · {new Date(latest.at).toLocaleTimeString('it-IT')}
          </small>
        </section>
      )}

      <main className="ct-main">
        <section className="ct-card">
          <h2>Meteo</h2>
          <span className="badge badge-unconfirmed">In costruzione</span>
        </section>
        <section className="ct-card">
          <h2>Trasporti</h2>
          {!stato ? (
            <p className="ct-muted">Dati non disponibili.</p>
          ) : (
            <ul className="ct-list">
              {stato.linee.map((linea) => (
                <li key={linea.id}>
                  <span className={`dot ${linea.attiva ? 'is-up' : 'is-down'}`} aria-hidden="true" />
                  <span>
                    {linea.nome}: {linea.attiva ? 'attiva' : 'sospesa'}
                  </span>
                </li>
              ))}
            </ul>
          )}
          <SimulationBadge label="simulato" />
        </section>
        <section className="ct-card">
          <h2>Avvisi</h2>
          {notices.length === 0 ? (
            <p className="ct-muted">Nessun avviso attivo.</p>
          ) : (
            <ul className="ct-list">
              {notices.map((notice) => (
                <li key={notice.key}>
                  <time>{new Date(notice.at).toLocaleTimeString('it-IT')}</time>
                  <span>{notice.title}</span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>

      <footer className="ct-footer">
        Gli allarmi ufficiali arrivano da IT-Alert e dalla Protezione Civile. Questa app aggiunge
        solo informazioni operative.
      </footer>
    </div>
  )
}
