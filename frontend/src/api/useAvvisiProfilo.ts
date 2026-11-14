import { useEffect, useRef, useState } from 'react'
import type { Alert } from './client'
import { dispositivo, type Profilo } from './profilo'

const POLL_MS = 2000

// Alerts for one profile (GET /api/avvisi?pubblico=…): its own alerts plus those for everyone,
// in its language. Every alert shown is confirmed once (POST /api/avvisi/{id}/visto) with the
// anonymous id of this phone, so the control room can count real readers.
export function useAvvisiProfilo(profilo: Profilo | null, refreshKey: unknown) {
  const [avvisi, setAvvisi] = useState<Alert[]>([])
  const confermati = useRef(new Set<string>())

  useEffect(() => {
    if (!profilo) {
      setAvvisi([])
      return
    }
    let alive = true
    const load = async () => {
      try {
        const response = await fetch(`/api/avvisi?pubblico=${encodeURIComponent(profilo)}`)
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        const next = (await response.json()) as Alert[]
        if (!alive) return
        setAvvisi(next)
        for (const a of next) {
          if (confermati.current.has(a.identifier)) continue
          confermati.current.add(a.identifier)
          void fetch(`/api/avvisi/${encodeURIComponent(a.identifier)}/visto`, {
            method: 'POST',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({ dispositivo: dispositivo() }),
          }).catch(() => confermati.current.delete(a.identifier))
        }
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
  }, [profilo, refreshKey])

  return avvisi
}
