"""Live channel to the browser via Server-Sent Events (SSE).

GET  /api/events       stream: one `data:` line of JSON per event
POST /api/events/test  publishes a test event, to check the channel end to end
"""

import asyncio
import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.bus import bus

router = APIRouter(prefix="/api/events", tags=["events"])

KEEPALIVE_SECONDS = 15


def format_sse(event: dict) -> str:
    return f"id: {event['id']}\nevent: {event['kind']}\ndata: {json.dumps(event)}\n\n"


@router.get("")
async def stream(request: Request) -> StreamingResponse:
    async def generate():
        async with bus.subscribe() as queue:
            yield ": connected\n\n"
            while not await request.is_disconnected():
                try:
                    event = await asyncio.wait_for(queue.get(), KEEPALIVE_SECONDS)
                except TimeoutError:
                    yield ": keepalive\n\n"
                    continue
                yield format_sse(event)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/test")
def publish_test() -> dict:
    return bus.publish(
        "test",
        {"message": "Canale in tempo reale attivo", "simulated": True},
    )
