import type { Alert } from '../api/client'
import { CERTAINTY, MSG_TYPE, severityLevel } from '../api/notices'
import { SimulationBadge } from '../components/SimulationBadge'

// One CAP alert as the citizen sees it (PROGETTO.md 6.2):
// case A, official alert: text forwarded unchanged, source in evidence;
// case B, event detected: "in attesa di comunicazioni ufficiali", operational measures only.
export function AlertCard({ alert, featured = false }: { alert: Alert; featured?: boolean }) {
  const level = severityLevel(alert.severity)
  return (
    <article className={`ct-alert ct-alert-${level}${featured ? ' is-featured' : ''}`} role={featured ? 'alert' : undefined}>
      <div className="ct-alert-tags">
        {alert.simulato && <SimulationBadge label="simulato" />}
        {alert.ufficiale ? (
          <span className="badge badge-official">Allarme ufficiale</span>
        ) : (
          <span className="badge badge-unconfirmed">Evento rilevato · in attesa di comunicazioni ufficiali</span>
        )}
        <span className="badge badge-reliable">Certezza: {CERTAINTY[alert.certainty] ?? alert.certainty}</span>
        {alert.msgType !== 'Alert' && <span className="badge badge-reliable">{MSG_TYPE[alert.msgType] ?? alert.msgType}</span>}
      </div>

      <h3 className="ct-alert-title">{alert.headline}</h3>
      {alert.ufficiale && <p className="ct-alert-label">Testo ufficiale, non modificato</p>}
      <p className="ct-alert-text">{alert.description}</p>

      {alert.instruction && (
        <div className="ct-alert-instruction">
          <strong>Indicazioni operative</strong>
          <p>{alert.instruction}</p>
        </div>
      )}

      <p className="ct-alert-source">
        Fonte: <strong>{alert.source}</strong> · inviato da {alert.sender}
      </p>
    </article>
  )
}
