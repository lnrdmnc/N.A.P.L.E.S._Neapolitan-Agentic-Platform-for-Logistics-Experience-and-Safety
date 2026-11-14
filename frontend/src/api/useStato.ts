import { useEffect, useState } from 'react'
import { fetchStato, type StatoCitta } from './client'

const POLL_MS = 1000

// Reads the shared session state from /api/stato once a second (PIANO.md, section 4).
export function useStato() {
  const [stato, setStato] = useState<StatoCitta | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    const load = async () => {
      try {
        const next = await fetchStato()
        if (alive) {
          setStato(next)
          setError(null)
        }
      } catch {
        if (alive) setError('API degli agenti non raggiungibile')
      }
    }
    load()
    const timer = setInterval(load, POLL_MS)
    return () => {
      alive = false
      clearInterval(timer)
    }
  }, [])

  return { stato, error }
}
