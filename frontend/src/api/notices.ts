import type { Alert, LiveEvent } from './client'

export type Notice = {
  key: string
  at: string
  title: string
  body: string
  source: string
  simulated: boolean
}

// Turns live-channel events into notices for the citizen view.
// "avvisi" events carry the CAP alerts the agents return when the operator approves a plan.
export function toNotices(events: LiveEvent[]): Notice[] {
  return events.flatMap((event) => {
    if (event.kind === 'avvisi') {
      const alerts = (event.data.avvisi ?? []) as Alert[]
      return alerts.map((alert) => ({
        key: `${event.id}-${alert.identifier}`,
        at: event.at,
        title: alert.headline,
        body: alert.description,
        source: alert.source,
        simulated: alert.simulato,
      }))
    }
    return [
      {
        key: String(event.id),
        at: event.at,
        title: 'Messaggio di prova',
        body: String(event.data.message ?? ''),
        source: 'control room N.A.P.L.E.S.',
        simulated: event.data.simulated === true,
      },
    ]
  })
}
