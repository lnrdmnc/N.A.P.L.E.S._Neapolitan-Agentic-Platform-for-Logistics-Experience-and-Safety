"""Runtime configuration for the browser: the Maps JavaScript key.

That key is public by design (it ends up in the page) and must be restricted to the web
app's domains in the Google console. The server-side Routes key never leaves the agents.
"""

import os

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["config"])


@router.get("/config")
def config() -> dict:
    return {"maps_js_api_key": os.environ.get("MAPS_JS_API_KEY") or None}
