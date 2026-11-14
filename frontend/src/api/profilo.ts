import { useCallback, useState } from 'react'
import type { Alert } from './client'

// Who the citizen is (U1). Stored on the phone only, never sent with personal data.
export type Profilo = Exclude<Alert['pubblico'], 'tutti'>

export const PROFILI: { id: Profilo; titolo: string; sottotitolo: string; lingua: 'it' | 'en' }[] = [
  { id: 'tifoso', titolo: 'Sono allo stadio', sottotitolo: 'Tifoso al Maradona', lingua: 'it' },
  { id: 'residente', titolo: 'Abito a Fuorigrotta', sottotitolo: 'Residente vicino allo stadio', lingua: 'it' },
  {
    id: 'pendolare',
    titolo: 'Torno verso Bagnoli o Pozzuoli',
    sottotitolo: 'Con Cumana o Linea 2',
    lingua: 'it',
  },
  { id: 'turista', titolo: "I'm visiting Naples", sottotitolo: 'Tourist · English', lingua: 'en' },
]

const CHIAVE_PROFILO = 'naples.profilo'
const CHIAVE_DISPOSITIVO = 'naples.dispositivo'

// localStorage can be missing or blocked (private mode): the app keeps working without it.
function leggi(chiave: string): string | null {
  try {
    return window.localStorage.getItem(chiave)
  } catch {
    return null
  }
}

function scrivi(chiave: string, valore: string | null) {
  try {
    if (valore === null) window.localStorage.removeItem(chiave)
    else window.localStorage.setItem(chiave, valore)
  } catch {
    // nothing to do: the choice lasts until the page is closed
  }
}

export function useProfilo() {
  const [profilo, setProfilo] = useState<Profilo | null>(() => {
    const salvato = leggi(CHIAVE_PROFILO)
    return PROFILI.some((p) => p.id === salvato) ? (salvato as Profilo) : null
  })

  const scegli = useCallback((nuovo: Profilo | null) => {
    scrivi(CHIAVE_PROFILO, nuovo)
    setProfilo(nuovo)
  }, [])

  return { profilo, scegli }
}

let dispositivoInMemoria: string | null = null

// Random, anonymous id of this phone: only used so the control room does not count
// the same phone twice when it confirms an alert was shown (B3).
export function dispositivo(): string {
  const salvato = leggi(CHIAVE_DISPOSITIVO) ?? dispositivoInMemoria
  if (salvato) return salvato
  const nuovo =
    typeof crypto !== 'undefined' && 'randomUUID' in crypto
      ? crypto.randomUUID()
      : `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`
  dispositivoInMemoria = nuovo
  scrivi(CHIAVE_DISPOSITIVO, nuovo)
  return nuovo
}
