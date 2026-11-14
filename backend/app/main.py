"""FastAPI app for the N.A.P.L.E.S. web app.

Serves the API under /api and, once the frontend is built (frontend/dist), the
PWA itself: one process and one link for the demo, offline included.
"""

from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routes.agents_proxy import AGENTS_URL
from app.routes.index import ROUTERS

FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
DEV_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]


def create_app(
    frontend_dist: Path = FRONTEND_DIST,
    agents_transport: httpx.AsyncBaseTransport | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with httpx.AsyncClient(base_url=AGENTS_URL, transport=agents_transport, timeout=10) as client:
            app.state.agents_client = client
            yield

    app = FastAPI(title="N.A.P.L.E.S. API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=DEV_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    for router in ROUTERS:
        app.include_router(router)

    if (frontend_dist / "index.html").is_file():
        app.mount(
            "/assets",
            StaticFiles(directory=frontend_dist / "assets", check_dir=False),
            name="assets",
        )

        @app.get("/{path:path}", include_in_schema=False)
        def spa(path: str) -> FileResponse:
            file = (frontend_dist / path).resolve()
            if path and file.is_file() and file.is_relative_to(frontend_dist):
                return FileResponse(file)
            return FileResponse(frontend_dist / "index.html")

    return app


app = create_app()
