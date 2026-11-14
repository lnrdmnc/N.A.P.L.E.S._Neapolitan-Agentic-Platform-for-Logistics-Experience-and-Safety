import { VELOCITA, useRegia } from '../api/useRegia'
import './Regia.css'

// Demo direction bar: the scenario clock runs by itself; pauses when a new plan needs a decision.
export function Regia({ tMin, ora }: { tMin?: number; ora?: string }) {
  const r = useRegia(tMin)
  const progresso = r.durata && tMin !== undefined ? Math.min(100, (tMin / r.durata) * 100) : 0

  return (
    <section className="rg" aria-label="Regia della simulazione">
      <div className="rg-buttons">
        {r.inCorso ? (
          <button type="button" className="rg-main" onClick={r.pausa}>
            ⏸ Pausa
          </button>
        ) : (
          <button type="button" className="rg-main" onClick={r.avvia} disabled={r.fine || tMin === undefined}>
            ▶ {tMin ? 'Riprendi' : 'Avvia'}
          </button>
        )}
        <button type="button" onClick={r.avanzaUnMinuto} disabled={r.inCorso || r.fine}>
          +1 min
        </button>
        <button type="button" onClick={r.saltaAlProssimo} disabled={r.inCorso || !r.prossimoEvento}>
          ⏭ Prossimo evento
        </button>
        <button type="button" onClick={() => void r.ricomincia()}>
          ↺ Ricomincia
        </button>
      </div>

      <div className="rg-time">
        <div className="rg-bar" role="progressbar" aria-valuemin={0} aria-valuemax={r.durata} aria-valuenow={tMin ?? 0}>
          <span style={{ width: `${progresso}%` }} />
        </div>
        <span className="rg-status">
          {r.fine
            ? 'Scenario concluso'
            : r.inCorso
              ? `In corso · ${ora ?? ''}`
              : `In pausa · ${ora ?? ''}`}
          {r.prossimoEvento && !r.fine && (
            <small>
              {' '}
              · prossimo: {r.prossimoEvento.ora} {r.prossimoEvento.titolo}
            </small>
          )}
        </span>
      </div>

      <div className="rg-options">
        <label>
          Velocità{' '}
          <select value={r.velocita} onChange={(e) => r.setVelocita(Number(e.target.value))}>
            {VELOCITA.map((v) => (
              <option key={v.ms} value={v.ms}>
                {v.label}
              </option>
            ))}
          </select>
        </label>
        <label className="rg-check">
          <input type="checkbox" checked={r.pausaSuPiano} onChange={(e) => r.setPausaSuPiano(e.target.checked)} />
          Pausa quando arriva un piano
        </label>
      </div>

      {r.error && <p className="cr-error">{r.error}</p>}
    </section>
  )
}
