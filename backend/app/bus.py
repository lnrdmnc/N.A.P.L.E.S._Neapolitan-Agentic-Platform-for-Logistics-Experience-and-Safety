"""In-memory event bus: the backend publishes, every open browser tab receives.

Each subscriber gets its own queue. Events are plain dicts; their shape will come
from contracts/ once the agents module publishes it.
"""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from itertools import count


class EventBus:
    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue[dict]] = set()
        self._ids = count(1)

    @property
    def subscriber_count(self) -> int:
        return len(self._subscribers)

    def publish(self, kind: str, data: dict) -> dict:
        event = {
            "id": next(self._ids),
            "kind": kind,
            "at": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        for queue in self._subscribers:
            queue.put_nowait(event)
        return event

    @asynccontextmanager
    async def subscribe(self) -> AsyncIterator[asyncio.Queue[dict]]:
        queue: asyncio.Queue[dict] = asyncio.Queue()
        self._subscribers.add(queue)
        try:
            yield queue
        finally:
            self._subscribers.discard(queue)


bus = EventBus()
