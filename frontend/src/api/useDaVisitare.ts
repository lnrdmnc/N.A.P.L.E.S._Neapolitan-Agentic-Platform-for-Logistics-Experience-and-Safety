import { useEffect, useState } from 'react'
import type { components } from './contratto'

export type DaVisitare = components['schemas']['DaVisitare']
export type LuogoConsigliato = components['schemas']['LuogoConsigliato']

const POLL_MS = 120_000

// Places to visit at a given moment (GET /api/napoli/da-visitare): real places, real events and strikes.
export function useDaVisitare(quando: string | null) {
  const [dati, setDati] = useState<DaVisitare | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    const load = async () => {
      try {
        const query = quando ? `?quando=${encodeURIComponent(quando)}` : ''
        const response = await fetch(`/api/napoli/da-visitare${query}`)
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        const next = (await response.json()) as DaVisitare
        if (alive) {
          setDati(next)
          setError(null)
        }
      } catch {
        if (alive) setError('Consigli non raggiungibili')
      }
    }
    load()
    const timer = setInterval(load, POLL_MS)
    return () => {
      alive = false
      clearInterval(timer)
    }
  }, [quando])

  return { dati, error }
}
