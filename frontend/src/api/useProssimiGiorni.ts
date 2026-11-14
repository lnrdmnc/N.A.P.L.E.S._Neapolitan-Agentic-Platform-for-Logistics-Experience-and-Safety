import { useEffect, useState } from 'react'
import type { components } from './contratto'

export type NapoliProssimiGiorni = components['schemas']['NapoliProssimiGiorni']
export type EventoPrevisto = components['schemas']['EventoPrevisto']
export type ScioperoPrevisto = components['schemas']['ScioperoPrevisto']

const POLL_MS = 60_000

// Upcoming events in Naples (GET /api/napoli/prossimi-giorni): real matches and the team's list.
// Read once a minute: it is a calendar, not the minute-by-minute scenario.
export function useProssimiGiorni(giorni = 10) {
  const [dati, setDati] = useState<NapoliProssimiGiorni | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    const load = async () => {
      try {
        const response = await fetch(`/api/napoli/prossimi-giorni?giorni=${giorni}`)
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        const next = (await response.json()) as NapoliProssimiGiorni
        if (alive) {
          setDati(next)
          setError(null)
        }
      } catch {
        if (alive) setError('Calendario non raggiungibile')
      }
    }
    load()
    const timer = setInterval(load, POLL_MS)
    return () => {
      alive = false
      clearInterval(timer)
    }
  }, [giorni])

  return { dati, error }
}
