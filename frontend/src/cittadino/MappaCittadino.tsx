import { useEffect, useRef, useState } from 'react'
import type { Schemas, StatoLinea } from '../api/client'
import { fetchMapsKey, loadGoogleMaps } from '../api/googleMaps'
import { useStato } from '../api/useStato'
import './MappaCittadino.css'

// Citizen map: where the stadium is, which stations are open or closed, where to walk to.
// Places and coordinates are real (OpenStreetMap, GTFS ANM/EAV, via /api/simulazione);
// whether a station is open follows the simulated scenario; traffic is Google's live layer.
// Without key or network the map is replaced by the same list, so nothing is lost offline.

type Zona = Schemas['StatoZona']

// Which line a place depends on (ids from /api/stato)
const LINEA_DI: Record<string, string> = {
  stazione_campi_flegrei: 'linea2',
  stazione_mostra: 'cumana',
  fermata_marino_stadio: 'bus',
}

type Stato = 'aperta' | 'chiusa' | 'luogo'

function statoLuogo(z: Zona, linee: StatoLinea[]): { stato: Stato; testo: string } {
  const id = LINEA_DI[z.id]
  if (!id) return { stato: 'luogo', testo: z.tipo === 'stadio' ? 'stadio' : 'punto di raccolta' }
  const linea = linee.find((l) => l.id === id)
  if (!linea) return { stato: 'luogo', testo: '' }
  return linea.attiva ? { stato: 'aperta', testo: 'aperta' } : { stato: 'chiusa', testo: 'chiusa' }
}

const COLORE: Record<Stato, string> = { aperta: '#24a148', chiusa: '#da1e28', luogo: '#161616' }

function useZone() {
  const [zone, setZone] = useState<Zona[]>([])
  useEffect(() => {
    let alive = true
    fetch('/api/simulazione')
      .then((r) => (r.ok ? r.json() : null))
      .then((d: Schemas['SerieSimulazione'] | null) => {
        if (alive && d?.passi?.length) setZone(d.passi[0].zone)
      })
      .catch(() => {})
    return () => {
      alive = false
    }
  }, [])
  return zone
}

export function MappaCittadino() {
  const zone = useZone()
  const { stato } = useStato()
  const linee = stato?.linee ?? []
  const mapRef = useRef<HTMLDivElement>(null)
  const [map, setMap] = useState<google.maps.Map | null>(null)
  const [mapError, setMapError] = useState<string | null>(null)
  const markers = useRef<google.maps.Marker[]>([])

  useEffect(() => {
    let alive = true
    ;(async () => {
      try {
        const key = await fetchMapsKey()
        if (!key) throw new Error('chiave della mappa non configurata')
        const maps = await loadGoogleMaps(key)
        if (!alive || !mapRef.current) return
        const m = new maps.Map(mapRef.current, {
          center: { lat: 40.8262, lng: 14.1935 },
          zoom: 16,
          disableDefaultUI: true,
          zoomControl: true,
          clickableIcons: false,
          gestureHandling: 'cooperative',
        })
        new maps.TrafficLayer().setMap(m)
        setMap(m)
      } catch (e) {
        if (alive) setMapError(e instanceof Error ? e.message : 'mappa non disponibile')
      }
    })()
    return () => {
      alive = false
    }
  }, [])

  // One marker per place, coloured by the state of its line
  const firma = zone.map((z) => `${z.id}:${statoLuogo(z, linee).stato}`).join('|')
  useEffect(() => {
    if (!map) return
    markers.current.forEach((m) => m.setMap(null))
    markers.current = zone.map((z) => {
      const { stato: s, testo } = statoLuogo(z, linee)
      return new google.maps.Marker({
        map,
        position: { lat: z.lat, lng: z.lon },
        title: testo ? `${z.nome}: ${testo}` : z.nome,
        icon: {
          path: google.maps.SymbolPath.CIRCLE,
          scale: z.tipo === 'stadio' ? 11 : 8,
          fillColor: COLORE[s],
          fillOpacity: 1,
          strokeColor: '#ffffff',
          strokeWeight: 2,
        },
      })
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [map, firma])

  return (
    <section className="ct-card ct-card-map" aria-labelledby="ct-map-title">
      <div className="ct-card-head">
        <h2 id="ct-map-title">Mappa intorno allo stadio</h2>
        <span className="badge badge-reliable">Traffico reale · Google Maps</span>
      </div>

      {mapError ? (
        <p className="ct-muted">Mappa non disponibile ({mapError}): restano qui sotto i luoghi e il loro stato.</p>
      ) : (
        <div className="ct-map" ref={mapRef} role="img" aria-label="Mappa di Fuorigrotta con stadio, stazioni e fermate" />
      )}

      <ul className="ct-map-legend">
        {zone.map((z) => {
          const { stato: s, testo } = statoLuogo(z, linee)
          return (
            <li key={z.id}>
              <span className="ct-map-dot" style={{ background: COLORE[s] }} aria-hidden="true" />
              <span>
                {z.nome}
                {testo && <strong className={`ct-map-state is-${s}`}> · {testo}</strong>}
              </span>
            </li>
          )
        })}
      </ul>
      <p className="ct-muted ct-small">
        Luoghi reali (OpenStreetMap, orari GTFS di ANM ed EAV). Stato di stazioni e fermate:{' '}
        <strong>simulato</strong>, segue lo scenario della demo.
      </p>
    </section>
  )
}
