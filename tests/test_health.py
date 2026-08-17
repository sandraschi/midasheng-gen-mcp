"""Health and capability endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from midasheng_gen_mcp.server import build_web_app


def test_health_ok() -> None:
    with TestClient(build_web_app()) as client:
        resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["tool_count"] >= 4


def test_diagnostics_ok() -> None:
    with TestClient(build_web_app()) as client:
        resp = client.get("/api/v1/diagnostics")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    names = {t["name"] for t in body["tools"]}
    assert "audio_scene" in names
    assert "midasheng_help" in names


def test_capabilities_endpoint() -> None:
    with TestClient(build_web_app()) as client:
        resp = client.get("/api/capabilities")
    assert resp.status_code == 200
    assert resp.json()["count"] >= 4


def test_dashboard_kpis() -> None:
    with TestClient(build_web_app()) as client:
        resp = client.get("/api/dashboard")
    assert resp.status_code == 200
    body = resp.json()
    assert "scene_count" in body
    assert "model_state" in body


def test_mcp_streamable_http_initialize() -> None:
    """FastMCP 3.4.4 regression: lifespan must propagate or POST /mcp 500s."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1"},
        },
    }
    with TestClient(build_web_app()) as client:
        resp = client.post(
            "/mcp/",
            json=payload,
            headers={"Accept": "application/json, text/event-stream"},
        )
    assert resp.status_code == 200
    assert '"serverInfo"' in resp.text or "serverInfo" in resp.text
