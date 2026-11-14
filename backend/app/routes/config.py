"""Runtime configuration for the browser: the Maps JavaScript key and the live channel URL.

EVENTS_URL points the live channel straight at Cloud Run when the pages are served through
Firebase Hosting, which buffers streamed responses (docs/DEPLOY.md). Unset: same origin.

That key is public by design (it ends up in the page) and must be restricted to the web
app's domains in the Google console. The server-side Routes key never leaves the agents.
"""

import os

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["config"])


@router.get("/config")
def config() -> dict:
    return {
        "maps_js_api_key": os.environ.get("MAPS_JS_API_KEY") or None,
        "events_url": os.environ.get("EVENTS_URL") or None,
    }
