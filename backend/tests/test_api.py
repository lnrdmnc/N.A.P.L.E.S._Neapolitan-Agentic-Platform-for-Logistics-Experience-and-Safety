import asyncio
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from app.bus import EventBus, bus
from app.main import create_app
from app.routes.events import format_sse


def test_health():
    client = TestClient(create_app())
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_bus_delivers_to_every_subscriber():
    local = EventBus()

    async def scenario():
        async with local.subscribe() as first, local.subscribe() as second:
            assert local.subscriber_count == 2
            sent = local.publish("alert", {"x": 1})
            assert await first.get() == sent
            assert await second.get() == sent
        assert local.subscriber_count == 0

    asyncio.run(scenario())


def test_sse_format():
    event = bus.publish("test", {"a": 1})
    text = format_sse(event)
    assert text.startswith(f"id: {event['id']}\nevent: test\ndata: ")
    assert text.endswith("\n\n")


def fake_agents(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/api/stato":
        return httpx.Response(200, json={"t_min": 72, "q": request.url.params.get("q")})
    if request.url.path == "/api/piano/p1/approva":
        return httpx.Response(200, json=[{"id": "a1", "simulato": True}])
    return httpx.Response(404, json={"detail": "Not Found"})


def test_proxy_forwards_to_agents():
    with TestClient(create_app(agents_transport=httpx.MockTransport(fake_agents))) as client:
        response = client.get("/api/stato?q=x")
        assert response.status_code == 200
        assert response.json() == {"t_min": 72, "q": "x"}
        assert client.get("/api/inesistente").status_code == 404
        assert client.get("/api/health").json()["status"] == "ok"


def test_approval_pushes_alerts_on_live_channel():
    async def scenario():
        async with bus.subscribe() as queue:
            with TestClient(create_app(agents_transport=httpx.MockTransport(fake_agents))) as client:
                assert client.post("/api/piano/p1/approva").status_code == 200
            event = queue.get_nowait()
            assert event["kind"] == "avvisi"
            assert event["data"] == {"piano": "p1", "avvisi": [{"id": "a1", "simulato": True}]}

    asyncio.run(scenario())


def test_proxy_reports_agents_down():
    def down(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused")

    with TestClient(create_app(agents_transport=httpx.MockTransport(down))) as client:
        response = client.get("/api/stato")
        assert response.status_code == 503
        assert "8001" in response.json()["detail"]


def test_spa_fallback_serves_index(tmp_path: Path):
    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text("<html>pwa</html>", encoding="utf-8")
    client = TestClient(create_app(frontend_dist=tmp_path))
    assert client.get("/control-room").text == "<html>pwa</html>"
    assert client.get("/api/health").json()["status"] == "ok"


def test_spa_does_not_serve_files_outside_dist(tmp_path: Path):
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<html>pwa</html>", encoding="utf-8")
    (tmp_path / "secret.txt").write_text("nope", encoding="utf-8")
    client = TestClient(create_app(frontend_dist=dist))
    assert "nope" not in client.get("/../secret.txt").text
