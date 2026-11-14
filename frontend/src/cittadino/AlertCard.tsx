import type { Alert } from '../api/client'
import { CERTAINTY, MSG_TYPE, severityLevel } from '../api/notices'
import { SimulationBadge } from '../components/SimulationBadge'

// One CAP alert as the citizen sees it (PROGETTO.md 6.2):
// case A, official alert: text forwarded unchanged, source in evidence;
// case B, event detected: "in attesa di comunicazioni ufficiali", operational measures only.
// Labels in the alert's language: the tourist gets English, the official text stays as issued.
const ETICHETTE = {
  it: {
    simulato: 'simulato',
    ufficiale: 'Allarme ufficiale',
    rilevato: 'Evento rilevato · in attesa di comunicazioni ufficiali',
    certezza: 'Certezza',
    testoUfficiale: 'Testo ufficiale, non modificato',
    indicazioni: 'Indicazioni operative',
    fonte: 'Fonte',
    inviato: 'inviato da',
    tipi: MSG_TYPE,
    certezze: CERTAINTY,
  },
  en: {
    simulato: 'simulated',
    ufficiale: 'Official alert',
    rilevato: 'Event detected · awaiting official communications',
    certezza: 'Certainty',
    testoUfficiale: 'Official text in Italian, not translated',
    indicazioni: 'Operational guidance',
    fonte: 'Source',
    inviato: 'sent by',
    tipi: { Alert: 'Alert', Update: 'Update', Cancel: 'All clear (operational)' } as Record<string, string>,
    certezze: {
      Observed: 'observed',
      Likely: 'likely',
      Possible: 'possible',
      Unlikely: 'unlikely',
      Unknown: 'uncertain',
    } as Record<string, string>,
  },
}

export function AlertCard({ alert, featured = false }: { alert: Alert; featured?: boolean }) {
  const level = severityLevel(alert.severity)
  const t = ETICHETTE[alert.lingua === 'en' ? 'en' : 'it']
  return (
    <article className={`ct-alert ct-alert-${level}${featured ? ' is-featured' : ''}`} role={featured ? 'alert' : undefined}>
      <div className="ct-alert-tags">
        {alert.simulato && <SimulationBadge label={t.simulato} />}
        {alert.ufficiale ? (
          <span className="badge badge-official">{t.ufficiale}</span>
        ) : (
          <span className="badge badge-unconfirmed">{t.rilevato}</span>
        )}
        <span className="badge badge-reliable">{t.certezza}: {t.certezze[alert.certainty] ?? alert.certainty}</span>
        {alert.msgType !== 'Alert' && <span className="badge badge-reliable">{t.tipi[alert.msgType] ?? alert.msgType}</span>}
      </div>

      <h3 className="ct-alert-title">{alert.headline}</h3>
      {alert.ufficiale && <p className="ct-alert-label">{t.testoUfficiale}</p>}
      <p className="ct-alert-text">{alert.description}</p>

      {alert.instruction && (
        <div className="ct-alert-instruction">
          <strong>{t.indicazioni}</strong>
          <p>{alert.instruction}</p>
        </div>
      )}

      <p className="ct-alert-source">
        {t.fonte}: <strong>{alert.source}</strong> · {t.inviato} {alert.sender}
      </p>
    </article>
  )
}
