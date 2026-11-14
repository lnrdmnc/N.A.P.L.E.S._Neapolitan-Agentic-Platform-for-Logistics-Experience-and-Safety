import { descriviMeteo, useContesto } from '../api/useContesto'
import './ContestoReale.css'

const MAX_EVENTI = 5

const quando = (iso: string) =>
  new Date(iso.endsWith('Z') || iso.includes('+') ? iso : `${iso}Z`).toLocaleString('it-IT', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'Europe/Rome',
  })

const giorno = (data: string) =>
  new Date(`${data}T12:00:00Z`).toLocaleDateString('it-IT', { day: 'numeric', month: 'short' })

// Real data of today, never simulated: official volcanic levels, latest INGV earthquakes,
// weather at the stadium. Kept apart from the scenario events, which are all simulated.
export function ContestoReale() {
  const { contesto, error } = useContesto()
  const fonti = Object.fromEntries((contesto?.fonti ?? []).map((f) => [f.nome, f]))
  const ingv = fonti['INGV FDSN']
  const openMeteo = fonti['Open-Meteo']

  return (
    <section className="cr-panel cr-panel-real cx">
      <div className="cx-head">
        <h2>Contesto reale di oggi</h2>
        <span className="badge badge-reliable">DATO REALE · non fa parte dello scenario</span>
      </div>
      {error && <p className="cr-todo">{error}</p>}
      {contesto && (
        <div className="cx-grid">
          <div className="cx-block">
            <h3>Allerta vulcanica ufficiale</h3>
            <ul className="cx-list">
              {contesto.livelli_vulcanici.map((v) => (
                <li key={v.area}>
                  <span className={`cx-level cx-level-${v.livello}`} aria-hidden="true" />
                  <strong>{v.area}</strong>
                  <span className="cx-value">{v.livello}</span>
                </li>
              ))}
            </ul>
            <p className="cx-source">
              Stabilito dalla Protezione Civile · letto su{' '}
              <a href={contesto.livelli_vulcanici[0]?.url ?? '#'} target="_blank" rel="noreferrer">
                Osservatorio Vesuviano – INGV
              </a>
              {contesto.livelli_vulcanici[0]?.verificato_il &&
                ` il ${giorno(contesto.livelli_vulcanici[0].verificato_il)}`}
            </p>
          </div>

          <div className="cx-block">
            <h3>Terremoti reali, ultimi 7 giorni</h3>
            {!ingv?.disponibile ? (
              <p className="cr-todo">INGV non disponibile{ingv?.motivo ? `: ${ingv.motivo}` : ''}</p>
            ) : contesto.eventi_ingv.length === 0 ? (
              <p className="cr-todo">Nessun evento registrato.</p>
            ) : (
              <ul className="cx-list">
                {contesto.eventi_ingv.slice(0, MAX_EVENTI).map((e) => (
                  <li key={e.id}>
                    <time>{quando(e.tempo)}</time>
                    <strong>{e.luogo}</strong>
                    <span className="cx-value">
                      {e.tipo_magnitudo} {e.magnitudo.toFixed(1)}
                    </span>
                  </li>
                ))}
              </ul>
            )}
            <p className="cx-source">
              INGV, servizio FDSN · {ingv?.copia ? 'copia salvata del ' : 'letto il '}
              {ingv?.aggiornato_al ? quando(ingv.aggiornato_al) : '—'}
            </p>
          </div>

          <div className="cx-block">
            <h3>Meteo allo stadio, adesso</h3>
            {!contesto.meteo ? (
              <p className="cr-todo">
                Meteo non disponibile{openMeteo?.motivo ? `: ${openMeteo.motivo}` : ''}
              </p>
            ) : (
              <dl className="cx-weather">
                <div>
                  <dt>Cielo</dt>
                  <dd>{descriviMeteo(contesto.meteo.codice_meteo)}</dd>
                </div>
                <div>
                  <dt>Temperatura</dt>
                  <dd>{contesto.meteo.temperatura_c.toFixed(0)} °C</dd>
                </div>
                <div>
                  <dt>Pioggia</dt>
                  <dd>{contesto.meteo.precipitazione_mm.toFixed(1)} mm</dd>
                </div>
                <div>
                  <dt>Vento</dt>
                  <dd>{contesto.meteo.vento_kmh.toFixed(0)} km/h</dd>
                </div>
              </dl>
            )}
            <p className="cx-source">
              Open-Meteo · {openMeteo?.copia ? 'copia salvata del ' : 'letto il '}
              {openMeteo?.aggiornato_al ? quando(openMeteo.aggiornato_al) : '—'}
            </p>
          </div>
        </div>
      )}
    </section>
  )
}
