import { sortAlerts } from '../api/notices'
import { useProfilo } from '../api/profilo'
import { useAvvisiProfilo } from '../api/useAvvisiProfilo'
import { useLiveEvents } from '../api/useLiveEvents'
import { useStato } from '../api/useStato'
import { LiveStatus } from '../components/LiveStatus'
import { SimulationBadge } from '../components/SimulationBadge'
import { AlertCard } from './AlertCard'
import { PartiteMaradona } from './PartiteMaradona'
import { SceltaProfilo } from './SceltaProfilo'
import './Cittadino.css'

// Citizen view: phone first, also usable on tablet and desktop.
// Sections from PROGETTO.md 6: emergencies (approved alerts with source), traffic, weather.
export function Cittadino() {
  const { status, events } = useLiveEvents()
  const { stato } = useStato()
  const { profilo, scegli } = useProfilo()
  const en = profilo === 'turista'
  const avvisi = sortAlerts(useAvvisiProfilo(profilo, events.filter((e) => e.kind === 'avvisi').length))
  const [latest, ...older] = avvisi

  return (
    <div className="ct">
      <header className="ct-header">
        <div className="ct-header-inner">
          <span className="ct-logo">N.A.P.L.E.S.</span>
          <LiveStatus status={status} inverse />
        </div>
      </header>

      <div className="ct-body">
        <SimulationBadge label={en ? 'DEMO · simulated events' : 'DEMO · eventi simulati'} />
        <SceltaProfilo profilo={profilo} onScegli={scegli} />

        <main className="ct-grid">
          <section className="ct-card ct-card-alerts" aria-labelledby="ct-alerts-title">
            <h2 id="ct-alerts-title">{en ? 'Emergencies and alerts' : 'Emergenze e avvisi'}</h2>
            {!profilo ? (
              <p className="ct-muted">Scegli chi sei per ricevere i tuoi avvisi. · Choose who you are to get your alerts.</p>
            ) : !latest ? (
              <p className="ct-muted">
                {en
                  ? 'No active alerts. Alerts appear here only after the control room approves them.'
                  : "Nessun avviso attivo. Gli avvisi compaiono qui solo dopo l'approvazione della control room."}
              </p>
            ) : (
              <>
                <AlertCard alert={latest} featured />
                {older.map((alert) => (
                  <AlertCard key={alert.identifier} alert={alert} />
                ))}
              </>
            )}
          </section>

          <section className="ct-card ct-card-transit">
            <h2>Traffico e trasporti</h2>
            {!stato ? (
              <p className="ct-muted">Dati non disponibili.</p>
            ) : (
              <ul className="ct-list">
                {stato.linee.map((linea) => (
                  <li key={linea.id}>
                    <span className={`dot ${linea.attiva ? 'is-up' : 'is-down'}`} aria-hidden="true" />
                    <span>
                      {linea.nome}: <strong>{linea.attiva ? 'attiva' : 'sospesa'}</strong>
                    </span>
                  </li>
                ))}
              </ul>
            )}
            <SimulationBadge label="simulato" />
          </section>

          <PartiteMaradona />

          <section className="ct-card ct-card-weather">
            <h2>Meteo</h2>
            <span className="badge badge-unconfirmed">In costruzione · U2</span>
          </section>
        </main>

        <footer className="ct-footer">
          Gli allarmi ufficiali arrivano da IT-Alert e dalla Protezione Civile. Questa app aggiunge
          solo informazioni operative.
        </footer>
      </div>
    </div>
  )
}
