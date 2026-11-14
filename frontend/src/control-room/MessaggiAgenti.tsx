import { useMemo, useState } from 'react'
import { type Messaggio, useMessaggi } from '../api/useMessaggi'
import { Affidabilita } from '../components/Affidabilita'
import { SimulationBadge } from '../components/SimulationBadge'
import './MessaggiAgenti.css'

// C2 · Timeline of what the agents say to each other (PIANO.md, section 7).
// Newest on top, readable from three metres: who speaks, to whom, about what.

const TIPI: Record<Messaggio['tipo'], string> = {
  evento: 'Evento',
  proposta: 'Proposta',
  conflitto: 'Conflitto',
  piano: 'Piano',
  decisione: 'Decisione',
  avviso: 'Avviso',
}

const FILTRI = [
  { id: 'tutti', label: 'Tutti' },
  { id: 'agenti', label: 'Solo agenti' },
  { id: 'avvisi', label: 'Avvisi' },
] as const

type Filtro = (typeof FILTRI)[number]['id']

const MAX_VISIBILI = 40

function visibile(m: Messaggio, filtro: Filtro) {
  if (filtro === 'agenti') return m.tipo === 'proposta' || m.tipo === 'conflitto' || m.tipo === 'piano'
  if (filtro === 'avvisi') return m.tipo === 'avviso' || m.tipo === 'decisione'
  return true
}

export function MessaggiAgenti() {
  const { messaggi, error } = useMessaggi()
  const [filtro, setFiltro] = useState<Filtro>('tutti')

  const elenco = useMemo(
    () =>
      messaggi
        .filter((m) => visibile(m, filtro))
        .slice(-MAX_VISIBILI)
        .reverse(),
    [messaggi, filtro],
  )

  return (
    <section className="cr-panel cr-panel-messages" aria-labelledby="msg-title">
      <div className="msg-head">
        <h2 id="msg-title">Messaggi tra agenti</h2>
        <div className="msg-filters" role="group" aria-label="Filtra i messaggi">
          {FILTRI.map((f) => (
            <button
              key={f.id}
              type="button"
              className={filtro === f.id ? 'is-active' : ''}
              aria-pressed={filtro === f.id}
              onClick={() => setFiltro(f.id)}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {error && <p className="cr-error">{error}</p>}
      {!error && elenco.length === 0 && <p className="cr-todo">Nessun messaggio fino a questo minuto.</p>}

      <ol className="msg-list" aria-live="polite">
        {elenco.map((m) => (
          <li key={m.seq} className={`msg msg-${m.tipo}`}>
            <time className="msg-time">{m.ora}</time>
            <span className="msg-kind">{TIPI[m.tipo]}</span>
            <div className="msg-body">
              <p className="msg-route">
                <strong>{m.da}</strong>
                <span aria-hidden="true"> → </span>
                <span className="sr-only"> a </span>
                <strong>{m.a}</strong>
              </p>
              <p className="msg-title">{m.titolo}</p>
              {m.testo && m.testo !== m.titolo && <p className="msg-text">{m.testo}</p>}
              <div className="msg-tags">
                {m.affidabilita && <Affidabilita value={m.affidabilita} />}
                {m.simulato && <SimulationBadge label="simulato" />}
              </div>
            </div>
          </li>
        ))}
      </ol>
    </section>
  )
}
