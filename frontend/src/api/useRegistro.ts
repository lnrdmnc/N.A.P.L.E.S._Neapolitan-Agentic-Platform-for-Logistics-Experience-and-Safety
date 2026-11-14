import { useCallback, useEffect, useState } from 'react'
import type { components } from './contratto'

export type StatoRegistro = components['schemas']['StatoRegistro']
export type VoceRegistro = components['schemas']['VoceRegistro']

const POLL_MS = 2000

// Reads GET /api/registro every two seconds. Every response is a fresh check of the hash chain
// done by the server; `verifica()` asks for one right now and records when it happened.
export function useRegistro() {
  const [registro, setRegistro] = useState<StatoRegistro | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [verificatoAlle, setVerificatoAlle] = useState<Date | null>(null)

  const carica = useCallback(async () => {
    try {
      const response = await fetch('/api/registro')
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      setRegistro((await response.json()) as StatoRegistro)
      setVerificatoAlle(new Date())
      setError(null)
    } catch {
      setError('Registro non raggiungibile')
    }
  }, [])

  useEffect(() => {
    let alive = true
    const load = () => {
      if (alive) void carica()
    }
    load()
    const timer = setInterval(load, POLL_MS)
    return () => {
      alive = false
      clearInterval(timer)
    }
  }, [carica])

  return { registro, error, verificatoAlle, verifica: carica }
}
