import { descriviMeteo, useContesto } from '../api/useContesto'

const ora = (iso: string) =>
  new Date(iso).toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Rome' })

// Real weather at the stadium now (Open-Meteo), never simulated. Official weather alerts
// come from Civil Protection: this card only shows the conditions.
export function MeteoReale({ en = false }: { en?: boolean }) {
  const { contesto, error } = useContesto()
  const meteo = contesto?.meteo
  const fonte = contesto?.fonti?.find((f) => f.nome === 'Open-Meteo')

  return (
    <section className="ct-card ct-card-weather">
      <div className="ct-card-head">
        <h2>{en ? 'Weather in Fuorigrotta' : 'Meteo a Fuorigrotta'}</h2>
        <span className="badge badge-reliable">{en ? 'REAL DATA · Open-Meteo' : 'DATO REALE · Open-Meteo'}</span>
      </div>
      {error || (contesto && !meteo) ? (
        <p className="ct-muted">
          {en ? 'Weather not available' : 'Meteo non disponibile'}
          {fonte?.motivo ? `: ${fonte.motivo}` : ''}
        </p>
      ) : !meteo ? (
        <p className="ct-muted">{en ? 'Loading…' : 'Caricamento…'}</p>
      ) : (
        <>
          <p className="ct-weather-now">
            <strong>{meteo.temperatura_c.toFixed(0)} °C</strong> · {descriviMeteo(meteo.codice_meteo, en)}
          </p>
          <p className="ct-muted">
            {en ? 'Rain' : 'Pioggia'} {meteo.precipitazione_mm.toFixed(1)} mm ·{' '}
            {en ? 'wind' : 'vento'} {meteo.vento_kmh.toFixed(0)} km/h
          </p>
        </>
      )}
      {fonte?.aggiornato_al && (
        <p className="ct-muted ct-small">
          {fonte.copia ? (en ? 'Saved copy from ' : 'Copia salvata delle ') : en ? 'Updated at ' : 'Aggiornato alle '}
          {ora(fonte.aggiornato_al)}
        </p>
      )}
    </section>
  )
}
