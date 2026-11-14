import { useEffect, useState } from 'react'
import type { LiveEvent } from './client'

export type LiveStatus = 'connecting' | 'live' | 'offline'

const MAX_EVENTS = 50

// Subscribes to the backend's Server-Sent Events stream. EventSource reconnects by itself.
// Online the pages come through Firebase Hosting, which buffers streams: /api/config then
// gives the direct Cloud Run URL of the stream (events_url). Locally it is null: same origin.
async function eventsUrl(): Promise<string> {
  try {
    const response = await fetch('/api/config')
    const body = (await response.json()) as { events_url?: string | null }
    return body.events_url || '/api/events'
  } catch {
    return '/api/events'
  }
}

export function useLiveEvents() {
  const [status, setStatus] = useState<LiveStatus>('connecting')
  const [events, setEvents] = useState<LiveEvent[]>([])

  useEffect(() => {
    let source: EventSource | null = null
    let closed = false

    eventsUrl().then((url) => {
      if (closed) return
      source = new EventSource(url)
      const s = source
      s.onopen = () => setStatus('live')
      s.onerror = () => setStatus(s.readyState === EventSource.CLOSED ? 'offline' : 'connecting')

      const onEvent = (message: MessageEvent<string>) => {
        const event = JSON.parse(message.data) as LiveEvent
        setEvents((previous) => [event, ...previous].slice(0, MAX_EVENTS))
      }
      s.onmessage = onEvent
      s.addEventListener('avvisi', onEvent)
    })

    return () => {
      closed = true
      source?.close()
    }
  }, [])

  return { status, events }
}
