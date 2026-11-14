import { useEffect, useState } from 'react'
import type { components } from './contratto'

export type Messaggio = components['schemas']['Messaggio']

const POLL_MS = 1000

// Reads the agents' message bus (GET /api/messaggi) once a second.
// The whole list is re-read on purpose: after /api/reset the sequence restarts from 1,
// and an incremental ?da_seq= request would miss the new session.
export function useMessaggi() {
  const [messaggi, setMessaggi] = useState<Messaggio[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    const load = async () => {
      try {
        const response = await fetch('/api/messaggi')
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        const next = (await response.json()) as Messaggio[]
        if (alive) {
          setMessaggi((prev) =>
            prev.length === next.length && prev[prev.length - 1]?.seq === next[next.length - 1]?.seq
              ? prev
              : next,
          )
          setError(null)
        }
      } catch {
        if (alive) setError('Messaggi non raggiungibili')
      }
    }
    load()
    const timer = setInterval(load, POLL_MS)
    return () => {
      alive = false
      clearInterval(timer)
    }
  }, [])

  return { messaggi, error }
}
