import { useEffect, useState } from 'react'
import { fetchAvvisi, type Alert } from './client'

const POLL_MS = 2000

// Alerts already sent, read from /api/avvisi: they survive a reload and reach a phone
// opened after the approval. `refreshKey` changes when the live channel announces new ones.
export function useAvvisi(refreshKey: unknown) {
  const [avvisi, setAvvisi] = useState<Alert[]>([])

  useEffect(() => {
    let alive = true
    const load = async () => {
      try {
        const next = await fetchAvvisi()
        if (alive) setAvvisi(next)
      } catch {
        // keep what we have: the backend or the agents may be restarting
      }
    }
    load()
    const timer = setInterval(load, POLL_MS)
    return () => {
      alive = false
      clearInterval(timer)
    }
  }, [refreshKey])

  return avvisi
}
