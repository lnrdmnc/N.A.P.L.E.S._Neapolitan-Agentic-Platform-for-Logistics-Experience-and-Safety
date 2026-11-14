import type { LiveStatus as Status } from '../api/useLiveEvents'

const LABELS: Record<Status, { text: string; color: string }> = {
  live: { text: 'Collegato', color: 'var(--level-green)' },
  connecting: { text: 'Connessione…', color: 'var(--level-yellow)' },
  offline: { text: 'Non collegato', color: 'var(--level-red)' },
}

export function LiveStatus({ status, inverse = false }: { status: Status; inverse?: boolean }) {
  const { text, color } = LABELS[status]
  return (
    <span
      className="live-status"
      style={{ display: 'inline-flex', alignItems: 'center', gap: 8, color: inverse ? 'var(--inverse-ink)' : 'var(--ink-muted)' }}
    >
      <span className="dot" style={{ background: color }} aria-hidden="true" />
      {text}
    </span>
  )
}
