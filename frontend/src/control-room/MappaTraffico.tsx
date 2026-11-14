import { useEffect, useRef, useState } from 'react'
import { fetchMapsKey, loadGoogleMaps } from '../api/googleMaps'
import { useTraffico, type PercorsoTraffico } from '../api/useTraffico'
import './MappaTraffico.css'

const STADIO = { lat: 40.828, lng: 14.193 }

const COLORI: Record<string, string> = {
  scorrevole: '#24a148',
  rallentato: '#ff832b',
  congestionato: '#da1e28',
}

const ETICHETTE: Record<string, string> = {
  scorrevole: 'scorrevole',
  rallentato: 'rallentato',
  congestionato: 'congestionato',
}

function ora(iso: string | null | undefined) {
  return iso ? new Date(iso).toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' }) : ''
}

// Real traffic only (Google): the map's traffic layer plus travel times from Routes API.
// Nothing here is simulated, and nothing is shown in place of missing data.
export function MappaTraffico() {
  const mapRef = useRef<HTMLDivElement>(null)
  const [map, setMap] = useState<google.maps.Map | null>(null)
  const [mapError, setMapError] = useState<string | null>(null)
  const { traffico, error } = useTraffico()

  useEffect(() => {
    let alive = true
    ;(async () => {
      try {
        const key = await fetchMapsKey()
        if (!key) throw new Error('Mappa non disponibile: chiave MAPS_JS_API_KEY non configurata')
        const maps = await loadGoogleMaps(key)
        if (!alive || !mapRef.current) return
        const m = new maps.Map(mapRef.current, {
          center: STADIO,
          zoom: 13,
          disableDefaultUI: true,
          zoomControl: true,
          clickableIcons: false,
        })
        new maps.TrafficLayer().setMap(m)
        setMap(m)
      } catch (e) {
        if (alive) setMapError(e instanceof Error ? e.message : 'Mappa non disponibile')
      }
    })()
    return () => {
      alive = false
    }
  }, [])

  useEffect(() => {
    if (!map || !traffico?.disponibile) return
    const lines = traffico.percorsi
      .filter((p) => p.polilinea && p.livello)
      .map(
        (p) =>
          new google.maps.Polyline({
            map,
            path: google.maps.geometry.encoding.decodePath(p.polilinea!),
            strokeColor: COLORI[p.livello!],
            strokeOpacity: 0.55,
            strokeWeight: 5,
          }),
      )
    return () => lines.forEach((l) => l.setMap(null))
  }, [map, traffico])

  return (
    <section className="cr-panel cr-panel-map mt">
      <div className="mt-head">
        <h2>Traffico in tempo reale</h2>
        <span className="badge badge-reliable">DATO REALE · Google Maps</span>
      </div>

      <div className="mt-body">
        <div className="mt-map" ref={mapRef}>
          {mapError && <p className="mt-missing">{mapError}</p>}
        </div>

        <div className="mt-side">
          {error && <p className="mt-missing">{error}</p>}
          {traffico && !traffico.disponibile && <p className="mt-missing">{traffico.motivo}</p>}
          {traffico?.disponibile && (
            <>
              <p className="mt-meta">
                Tempi in auto dallo stadio · rilevati alle {ora(traffico.rilevato_alle)}
                {traffico.motivo && <span className="badge badge-unconfirmed">{traffico.motivo}</span>}
              </p>
              <ul className="mt-list">
                {traffico.percorsi.map((p) => (
                  <Riga key={p.id} p={p} />
                ))}
              </ul>
            </>
          )}
          <p className="mt-source">{traffico?.fonte ?? 'Google Maps Platform'}</p>
        </div>
      </div>
    </section>
  )
}

function Riga({ p }: { p: PercorsoTraffico }) {
  if (p.durata_min == null) {
    return (
      <li>
        <strong>{p.a}</strong>
        <span className="mt-na">non disponibile</span>
      </li>
    )
  }
  return (
    <li>
      <span className="mt-dot" style={{ background: COLORI[p.livello ?? ''] }} aria-hidden="true" />
      <strong>{p.a}</strong>
      <span className="mt-min">{Math.round(p.durata_min)} min</span>
      <span className="mt-delay">
        {p.ritardo_min && p.ritardo_min >= 1 ? `+${Math.round(p.ritardo_min)} min di traffico` : ETICHETTE[p.livello ?? '']}
      </span>
    </li>
  )
}
