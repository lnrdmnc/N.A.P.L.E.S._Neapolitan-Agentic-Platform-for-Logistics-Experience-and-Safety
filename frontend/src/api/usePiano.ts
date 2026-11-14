import { useCallback, useEffect, useState } from 'react'
import type { Alert, Schemas } from './client'

export type Piano = Schemas['Piano']
export type Proposta = Schemas['Proposta']

const POLL_MS = 1000

async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    const detail = data && typeof data.detail === 'string' ? data.detail : `HTTP ${response.status}`
    throw new Error(detail)
  }
  return data as T
}

// Current plan of the Orchestrator and the operator's three decisions (PROGETTO.md 6.2, step 4).
export function usePiano() {
  const [piano, setPiano] = useState<Piano | null>(null)
  const [loaded, setLoaded] = useState(false)

  const load = useCallback(async () => {
    try {
      const response = await fetch('/api/piano')
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      setPiano((await response.json()) as Piano | null)
      setLoaded(true)
    } catch {
      // keep the last plan on screen; the header shows when the agents are unreachable
    }
  }, [])

  useEffect(() => {
    load()
    const timer = setInterval(load, POLL_MS)
    return () => clearInterval(timer)
  }, [load])

  const approva = async (id: string) => {
    const avvisi = await post<Alert[]>(`/api/piano/${id}/approva`, { operatore: 'operatore' })
    await load()
    return avvisi
  }

  const modifica = async (id: string, escluse: string[], motivo: string) => {
    await post<Piano>(`/api/piano/${id}/modifica`, { proposte_escluse: escluse, motivo, operatore: 'operatore' })
    await load()
  }

  const rifiuta = async (id: string, motivo: string) => {
    await post<Piano>(`/api/piano/${id}/rifiuta`, { operatore: 'operatore', motivo })
    await load()
  }

  return { piano, loaded, approva, modifica, rifiuta }
}
