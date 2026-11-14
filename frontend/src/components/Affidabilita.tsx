import type { Evento } from '../api/client'

const LABELS: Record<string, string> = {
  ufficiale: 'ufficiale',
  misurata: 'misurata',
  stimata: 'stimata',
  non_verificata: 'non verificata',
}

// Reliability of a piece of data, always shown next to it (contracts/README.md).
export function Affidabilita({ value }: { value: Evento['affidabilita'] }) {
  const unconfirmed = value === 'non_verificata' || value === 'stimata'
  return (
    <span className={`badge ${unconfirmed ? 'badge-unconfirmed' : 'badge-reliable'}`}>
      {LABELS[value] ?? value}
    </span>
  )
}
