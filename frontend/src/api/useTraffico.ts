import { useEffect, useState } from 'react'
import type { Schemas } from './client'

export type Traffico = Schemas['Traffico']
export type PercorsoTraffico = Schemas['PercorsoTraffico']

// The agents cache Google's answer (TRAFFICO_TTL_S, 10 minutes by default):
// polling every minute costs no extra requests to Google.
const POLL_MS = 60_000

export function useTraffico() {
  const [traffico, setTraffico] = useState<Traffico | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    const load = async () => {
      try {
        const response = await fetch('/api/traffico')
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        const next = (await response.json()) as Traffico
        if (alive) {
          setTraffico(next)
          setError(null)
        }
      } catch {
        if (alive) setError('Traffico non raggiungibile')
      }
    }
    load()
    const timer = setInterval(load, POLL_MS)
    return () => {
      alive = false
      clearInterval(timer)
    }
  }, [])

  return { traffico, error }
}
