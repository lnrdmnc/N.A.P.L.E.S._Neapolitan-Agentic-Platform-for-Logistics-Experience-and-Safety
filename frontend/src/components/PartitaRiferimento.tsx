import type { components } from '../api/contratto'
import './PartitaRiferimento.css'

type Partita = components['schemas']['Partita']

const quando = (iso: string, en: boolean) =>
  new Date(iso).toLocaleString(en ? 'en-GB' : 'it-IT', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'Europe/Rome',
  })

// The scenario is a dress rehearsal of the next real home match at the Maradona: teams, competition
// and kick-off are real (football-data.org); the earthquake swarm, closures and crowd are simulated.
export function PartitaRiferimento({ partita, en = false }: { partita?: Partita | null; en?: boolean }) {
  if (!partita) {
    return (
      <p className="pr pr-empty">
        {en
          ? 'No upcoming match at the Maradona from the source: demo scenario only.'
          : 'Nessuna partita in calendario dalla fonte: scenario solo dimostrativo.'}
      </p>
    )
  }
  return (
    <section className="pr" aria-label={en ? 'Reference match' : 'Partita di riferimento'}>
      <span className="pr-label">{en ? 'Dress rehearsal for' : 'Prova generale per'}</span>
      <strong className="pr-match">
        {partita.casa} – {partita.ospite}
      </strong>
      <span className="pr-when">
        {partita.competizione} · {quando(partita.data_ora, en)}
      </span>
      <span className="pr-tags">
        <span className="badge badge-reliable">{en ? 'Real match' : 'Partita reale'} · football-data.org</span>
        <span className="badge badge-simulated">
          {en ? 'Earthquakes, closures, crowd: simulated' : 'Scosse, chiusure e folla: simulate'}
        </span>
      </span>
    </section>
  )
}
