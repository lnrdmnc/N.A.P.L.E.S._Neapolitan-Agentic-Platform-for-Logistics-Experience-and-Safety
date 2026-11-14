import type { Alert } from './client'

// Italian labels for the CAP fields shown to citizens (contracts/README.md: always show
// simulato, certainty and source).
export const CERTAINTY: Record<string, string> = {
  Observed: 'osservato',
  Likely: 'probabile',
  Possible: 'possibile',
  Unlikely: 'improbabile',
  Unknown: 'incerto',
}

export const MSG_TYPE: Record<string, string> = {
  Alert: 'Avviso',
  Update: 'Aggiornamento',
  Cancel: 'Cessato avviso',
}

export type Level = 'red' | 'orange' | 'yellow' | 'neutral'

export function severityLevel(severity: string): Level {
  switch (severity) {
    case 'Extreme':
    case 'Severe':
      return 'red'
    case 'Moderate':
      return 'orange'
    case 'Minor':
      return 'yellow'
    default:
      return 'neutral'
  }
}

// Newest first: alerts carry the minute they were sent.
export function sortAlerts(alerts: Alert[]): Alert[] {
  return [...alerts].sort((a, b) => b.sent_t_min - a.sent_t_min)
}
