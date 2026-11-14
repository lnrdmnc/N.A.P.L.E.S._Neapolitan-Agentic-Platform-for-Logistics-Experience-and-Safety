import { useEffect, useState } from 'react'
import type { components } from './contratto'

export type ConfrontoIndicatori = components['schemas']['ConfrontoIndicatori']
export type Indicatori = components['schemas']['Indicatori']

const POLL_MS = 2000

// Reads GET /api/indicatori every two seconds: the numbers change once the operator decides.
export function useIndicatori() {
  const [dati, setDati] = useState<ConfrontoIndicatori | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    const load = async () => {
      try {
        const response = await fetch('/api/indicatori')
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        const next = (await response.json()) as ConfrontoIndicatori
        if (alive) {
          setDati(next)
          setError(null)
        }
      } catch {
        if (alive) setError('Indicatori non raggiungibili')
      }
    }
    load()
    const timer = setInterval(load, POLL_MS)
    return () => {
      alive = false
      clearInterval(timer)
    }
  }, [])

  return { dati, error }
}
