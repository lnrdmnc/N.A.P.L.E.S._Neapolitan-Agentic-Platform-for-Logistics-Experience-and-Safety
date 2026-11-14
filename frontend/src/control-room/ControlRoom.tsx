import { useState } from 'react'
import { publishTestEvent } from '../api/client'
import { useLiveEvents } from '../api/useLiveEvents'
import { useStato } from '../api/useStato'
import { Affidabilita } from '../components/Affidabilita'
import { LiveStatus } from '../components/LiveStatus'
import { SimulationBadge } from '../components/SimulationBadge'
import './ControlRoom.css'

// Panels still to build (PIANO.md: C1 map, C2 timeline, C3 plan, C5 indicators).
const TODO_PANELS = [
  { id: 'map', title: 'Mappa', task: 'C1' },
  { id: 'plan', title: 'Piano proposto', task: 'C3' },
  { id: 'kpi', title: 'Indicatori con e senza coordinamento', task: 'C5' },
]

export function ControlRoom() {
  const { status, events } = useLiveEvents()
  const { stato, error } = useStato()
  const [testError, setTestError] = useState<string | null>(null)

  const sendTest = async () => {
    setTestError(null)
    try {
      await publishTestEvent()
    } catch {
      setTestError('Backend non raggiungibile: avvialo con make backend')
    }
  }

  return (
    <div className="cr">
      <header className="cr-header">
        <div className="cr-brand">
          <span className="cr-logo">N.A.P.L.E.S.</span>
          <span className="cr-subtitle">Control room · Comune di Napoli</span>
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
        {TODO_PANELS.map((panel) => (
          <section key={panel.id} className={`cr-panel cr-panel-${panel.id}`}>
            <h2>{panel.title}</h2>
            <span className="badge badge-unconfirmed">In costruzione · {panel.task}</span>
          </section>
        ))}

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
              <ul className="cr-lines">
                {stato.linee.map((linea) => (
                  <li key={linea.id} className={linea.attiva ? '' : 'is-down'}>
                    <span className="dot" aria-hidden="true" />
                    <strong>{linea.nome}</strong>
                    <span>{linea.attiva ? 'attiva' : `sospesa${linea.motivo ? ` · ${linea.motivo}` : ''}`}</span>
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

        <section className="cr-panel cr-panel-log">
          <div className="cr-log-head">
            <h2>Canale in tempo reale</h2>
            <button className="btn-primary" onClick={sendTest}>
              Invia evento di prova
            </button>
          </div>
          {testError && <p className="cr-error">{testError}</p>}
          {events.length === 0 ? (
            <p className="cr-todo">Nessun messaggio ricevuto.</p>
          ) : (
            <ol className="cr-log">
              {events.map((event) => (
                <li key={event.id}>
                  <time>{new Date(event.at).toLocaleTimeString('it-IT')}</time>
                  <span className="cr-log-kind">{event.kind}</span>
                  <span className="cr-log-text">{String(event.data.message ?? '')}</span>
                  {event.data.simulated === true && <SimulationBadge label="simulato" />}
                </li>
              ))}
            </ol>
          )}
        </section>
      </main>
    </div>
  )
}
