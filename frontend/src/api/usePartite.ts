import { useEffect, useState } from 'react'
import type { Schemas } from './client'

export type Partite = Schemas['Partite']
export type Partita = Schemas['Partita']

// The agents keep football-data.org's answer for hours (PARTITE_TTL_S): polling every
// ten minutes costs no extra requests to the source.
const POLL_MS = 10 * 60_000

export function usePartite() {
  const [partite, setPartite] = useState<Partite | null>(null)

  useEffect(() => {
    let alive = true
    const load = async () => {
      try {
        const response = await fetch('/api/partite')
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        const next = (await response.json()) as Partite
        if (alive) setPartite(next)
      } catch {
        // keep what we have; the card says when data is missing
      }
    }
    load()
    const timer = setInterval(load, POLL_MS)
    return () => {
      alive = false
      clearInterval(timer)
    }
  }, [])

  return partite
}
