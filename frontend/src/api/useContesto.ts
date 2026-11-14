import { useEffect, useState } from 'react'
import type { Schemas } from './client'

export type Contesto = Schemas['Contesto']

// Real context (INGV, weather, official volcanic levels). The agents cache the sources:
// reading every two minutes adds no load on INGV or Open-Meteo.
const POLL_MS = 120_000

export function useContesto() {
  const [contesto, setContesto] = useState<Contesto | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    const load = async () => {
      try {
        const response = await fetch('/api/contesto')
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        const next = (await response.json()) as Contesto
        if (alive) {
          setContesto(next)
          setError(null)
        }
      } catch {
        if (alive) setError('Contesto reale non raggiungibile')
      }
    }
    load()
    const timer = setInterval(load, POLL_MS)
    return () => {
      alive = false
      clearInterval(timer)
    }
  }, [])

  return { contesto, error }
}

// WMO weather codes used by Open-Meteo, grouped for a short Italian/English label.
export function descriviMeteo(codice: number, en = false): string {
  const voci: [number[], string, string][] = [
    [[0], 'sereno', 'clear'],
    [[1, 2], 'poco nuvoloso', 'partly cloudy'],
    [[3], 'coperto', 'overcast'],
    [[45, 48], 'nebbia', 'fog'],
    [[51, 53, 55, 56, 57], 'pioviggine', 'drizzle'],
    [[61, 63, 65, 66, 67, 80, 81, 82], 'pioggia', 'rain'],
    [[71, 73, 75, 77, 85, 86], 'neve', 'snow'],
    [[95, 96, 99], 'temporale', 'thunderstorm'],
  ]
  const voce = voci.find(([codici]) => codici.includes(codice))
  return voce ? (en ? voce[2] : voce[1]) : en ? 'unknown' : 'n.d.'
}
