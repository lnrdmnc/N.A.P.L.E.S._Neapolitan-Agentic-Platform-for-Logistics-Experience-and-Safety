// Client for the backend on :8000. Agents endpoints are forwarded to agents/ (:8001).
// Types come from contracts/agenti.openapi.json via `npm run contract`.
import type { components } from './contratto'

export type Schemas = components['schemas']
export type StatoCitta = Schemas['StatoCitta']
export type Evento = Schemas['Evento']
export type StatoLinea = Schemas['StatoLinea']
export type Alert = Schemas['Alert']

export type LiveEvent = {
  id: number
  kind: string
  at: string
  data: Record<string, unknown>
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(path)
  if (!response.ok) throw new Error(`${path}: HTTP ${response.status}`)
  return response.json() as Promise<T>
}

export const fetchStato = () => getJson<StatoCitta>('/api/stato')

export async function publishTestEvent(): Promise<LiveEvent> {
  const response = await fetch('/api/events/test', { method: 'POST' })
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  return response.json()
}
