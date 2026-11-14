import { useLiveEvents } from '../api/useLiveEvents'
import { useStato } from '../api/useStato'
import { Affidabilita } from '../components/Affidabilita'
import { LiveStatus } from '../components/LiveStatus'
import { SimulationBadge } from '../components/SimulationBadge'
import { MappaTraffico } from './MappaTraffico'
import { Indicatori } from './Indicatori'
import { MessaggiAgenti } from './MessaggiAgenti'
import { Registro } from './Registro'
import { PianoProposto } from './PianoProposto'
import './ControlRoom.css'

export function ControlRoom() {
  const { status } = useLiveEvents()
  const { stato, error } = useStato()

  return (
    <div className="cr">
      <header className="cr-header">
        <div className="cr-brand">
          <span className="cr-logo">N.A.P.L.E.S.</span>
          <span className="cr-subtitle">Control room comunale · prototipo</span>
        </div>
        <div className="cr-header-right">
          {stato && (
            <span className="cr-clock">
              {stato.ora} <small>minuto {stato.t_min}</small>
            </span>
          )}
          <SimulationBadge label="SIMULAZIONE · nessun evento reale" />
          <LiveStatus status={status} inverse />
        </div>
      </header>

      {error && <p className="cr-banner-error">{error}: avviala con make agents-run</p>}

      <main className="cr-grid">
        <MappaTraffico />
        <MessaggiAgenti />
        <Indicatori />
        <Registro />
        <PianoProposto />

        <section className="cr-panel cr-panel-city">
          <h2>Stato della città</h2>
          {!stato ? (
            <p className="cr-todo">In attesa dei dati…</p>
          ) : (
            <>
              <dl className="cr-facts">
                <div>
                  <dt>Spettatori</dt>
                  <dd>{stato.spettatori.toLocaleString('it-IT')}</dd>
                </div>
                <div>
                  <dt>Partita</dt>
                  <dd>{stato.partita_finita ? 'finita' : 'in corso'}</dd>
                </div>
                <div>
                  <dt>Campi Flegrei, livello di allerta</dt>
                  <dd>{stato.livello_vulcanico_campi_flegrei}</dd>
                </div>
              </dl>
              <div className="cr-facts-tags">
                <SimulationBadge label="spettatori e partita: simulati" />
                <span className="badge badge-unconfirmed">livello vulcanico: da verificare</span>
              </div>
              <ul className="cr-lines">
                {stato.linee.map((linea) => (
                  <li key={linea.id} className={linea.attiva ? '' : 'is-down'}>
                    <span className="dot" aria-hidden="true" />
                    <span className="cr-line-text">
                      <strong>{linea.nome}</strong>{' '}
                      <span className="cr-line-state">
                        {linea.attiva ? 'attiva' : `sospesa${linea.motivo ? ` · ${linea.motivo}` : ''}`}
                      </span>
                    </span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </section>

        <section className="cr-panel cr-panel-events">
          <h2>Eventi dello scenario</h2>
          {!stato || stato.eventi.length === 0 ? (
            <p className="cr-todo">Nessun evento fino a questo minuto.</p>
          ) : (
            <ol className="cr-log">
              {[...stato.eventi].reverse().map((evento) => (
                <li key={evento.id}>
                  <time>min {evento.t_min}</time>
                  <span className="cr-log-text">{evento.titolo}</span>
                  <Affidabilita value={evento.affidabilita} />
                  {evento.simulato && <SimulationBadge label="simulato" />}
                </li>
              ))}
            </ol>
          )}
        </section>

      </main>
    </div>
  )
}
