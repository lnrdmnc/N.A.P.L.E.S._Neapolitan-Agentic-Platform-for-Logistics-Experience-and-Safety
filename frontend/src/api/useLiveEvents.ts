import { useEffect, useState } from 'react'
import type { LiveEvent } from './client'

export type LiveStatus = 'connecting' | 'live' | 'offline'

const MAX_EVENTS = 50

// Subscribes to the backend's Server-Sent Events stream. EventSource reconnects by itself.
export function useLiveEvents() {
  const [status, setStatus] = useState<LiveStatus>('connecting')
  const [events, setEvents] = useState<LiveEvent[]>([])

  useEffect(() => {
    const source = new EventSource('/api/events')
    source.onopen = () => setStatus('live')
    source.onerror = () => setStatus(source.readyState === EventSource.CLOSED ? 'offline' : 'connecting')

    const onEvent = (message: MessageEvent<string>) => {
      const event = JSON.parse(message.data) as LiveEvent
      setEvents((previous) => [event, ...previous].slice(0, MAX_EVENTS))
    }
    source.onmessage = onEvent
    source.addEventListener('avvisi', onEvent)

    return () => source.close()
  }, [])

  return { status, events }
}
