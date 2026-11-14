import { useCallback, useEffect, useRef, useState } from 'react'

// Time direction of the demo (checkpoint 14:50: «real time»). The scenario clock advances by
// itself while playing: one simulated minute every `velocita` milliseconds, through
// POST /api/avanza. When a new plan arrives the clock can pause on its own, so the operator
// decides before time moves on. Only the control room drives the clock: phones just read.

export const VELOCITA = [
  { ms: 2000, label: '1 min ogni 2 s' },
  { ms: 1000, label: '1 min al secondo' },
  { ms: 250, label: 'veloce' },
] as const

type Scenario = { durata_min: number; timeline: { t_min: number; ora: string; titolo: string }[] }

async function post<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(path, {
    method: 'POST',
    headers: body ? { 'content-type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!response.ok) throw new Error(`${path}: HTTP ${response.status}`)
  return response.json() as Promise<T>
}

export function useRegia(tMinPagina: number | undefined) {
  // The clock follows the server's answer to each step, not the page's once-a-second refresh.
  // Never moves backwards on a late page refresh: asking the server for an earlier minute would
  // restart the whole scenario. Only «Ricomincia» sets it back (from the server's reply).
  const [tMin, setTMin] = useState<number | undefined>(tMinPagina)
  useEffect(() => {
    setTMin((prima) =>
      prima === undefined || (tMinPagina !== undefined && tMinPagina > prima) ? tMinPagina : prima,
    )
  }, [tMinPagina])
  const [inCorso, setInCorso] = useState(false)
  const [velocita, setVelocita] = useState<number>(VELOCITA[0].ms)
  const [pausaSuPiano, setPausaSuPiano] = useState(true)
  const [scenario, setScenario] = useState<Scenario | null>(null)
  const [error, setError] = useState<string | null>(null)
  const ultimoPiano = useRef<string | null>(null)
  const occupato = useRef(false)

  useEffect(() => {
    fetch('/api/scenario')
      .then((r) => (r.ok ? (r.json() as Promise<Scenario>) : Promise.reject(new Error(String(r.status)))))
      .then(setScenario)
      .catch(() => setError('Scenario non raggiungibile'))
  }, [])

  const durata = scenario?.durata_min ?? 0
  const fine = tMin !== undefined && durata > 0 && tMin >= durata

  const vaiA = useCallback(
    async (t: number) => {
      if (occupato.current) return
      occupato.current = true
      try {
        const nuovo = await post<{ t_min: number }>('/api/avanza', { t_min: Math.max(0, Math.min(t, durata || t)) })
        setTMin(nuovo.t_min)
        setError(null)
        if (pausaSuPiano) {
          const r = await fetch('/api/piano')
          const piano = r.ok ? ((await r.json()) as { id: string; stato: string } | null) : null
          if (piano && piano.stato === 'proposto' && piano.id !== ultimoPiano.current) {
            ultimoPiano.current = piano.id
            setInCorso(false)
          }
        }
      } catch {
        setError("Non riesco a far avanzare il tempo: l'API degli agenti risponde?")
        setInCorso(false)
      } finally {
        occupato.current = false
      }
    },
    [durata, pausaSuPiano],
  )

  // The clock: one minute per tick while playing, stops at the end of the scenario.
  useEffect(() => {
    if (!inCorso || tMin === undefined) return
    if (fine) {
      setInCorso(false)
      return
    }
    const timer = setTimeout(() => void vaiA(tMin + 1), velocita)
    return () => clearTimeout(timer)
  }, [inCorso, tMin, velocita, fine, vaiA])

  const prossimoEvento = scenario?.timeline.find((e) => tMin !== undefined && e.t_min > tMin) ?? null

  const ricomincia = useCallback(async () => {
    setInCorso(false)
    ultimoPiano.current = null
    try {
      const nuovo = await post<{ t_min: number }>('/api/reset')
      setTMin(nuovo.t_min)
      setError(null)
    } catch {
      setError('Non riesco a ricominciare lo scenario')
    }
  }, [])

  return {
    inCorso,
    avvia: () => setInCorso(true),
    pausa: () => setInCorso(false),
    velocita,
    setVelocita,
    pausaSuPiano,
    setPausaSuPiano,
    avanzaUnMinuto: () => tMin !== undefined && void vaiA(tMin + 1),
    saltaAlProssimo: () => prossimoEvento && void vaiA(prossimoEvento.t_min),
    prossimoEvento,
    ricomincia,
    durata,
    fine,
    error,
  }
}
