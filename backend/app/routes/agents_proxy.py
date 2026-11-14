"""Gateway to the agents API (agents/, port 8001), contract: contracts/agenti.openapi.json.

Every /api/* path not handled by this backend is forwarded as is. When the operator
approves a plan, the alerts the agents return are also pushed on the live channel,
so the citizen view gets them at once.
Registered last in the router index, so the backend's own routes win.
"""

import os
import re

import httpx
from fastapi import APIRouter, Request, Response

from app.bus import bus

AGENTS_URL = os.environ.get("AGENTS_URL", "http://127.0.0.1:8001")
APPROVE_PATH = re.compile(r"^piano/[^/]+/approva$")
HOP_HEADERS = {"host", "content-length", "connection", "transfer-encoding", "content-encoding"}

router = APIRouter(prefix="/api", tags=["agenti"])


def agents_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.agents_client


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], include_in_schema=False)
async def forward(path: str, request: Request) -> Response:
    client = agents_client(request)
    headers = {k: v for k, v in request.headers.items() if k.lower() not in HOP_HEADERS}
    try:
        upstream = await client.request(
            request.method,
            f"/api/{path}",
            params=request.query_params,
            content=await request.body(),
            headers=headers,
        )
    except httpx.HTTPError:
        return Response(
            content='{"detail": "API degli agenti non raggiungibile (porta 8001)"}',
            status_code=503,
            media_type="application/json",
        )

    if request.method == "POST" and APPROVE_PATH.match(path) and upstream.status_code == 200:
        bus.publish("avvisi", {"piano": path.split("/")[1], "avvisi": upstream.json()})

    out_headers = {k: v for k, v in upstream.headers.items() if k.lower() not in HOP_HEADERS}
    return Response(content=upstream.content, status_code=upstream.status_code, headers=out_headers)
