"""Health and diagnostics endpoints (fleet standard)."""

from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, Request

from ... import __version__

router = APIRouter(tags=["health"])

_STARTED = time.time()


@router.get("/api/health")
async def health(request: Request) -> dict[str, Any]:
    """Live health probe: model state, uptime, tool count."""
    manager = request.app.state.manager
    tools = await request.app.state.fastmcp.list_tools()
    tool_count = len(tools)
    state = manager.status()
    return {
        "status": "ok",
        "server": "MiDashengLM-Gen MCP",
        "version": __version__,
        "uptime_seconds": int(time.time() - _STARTED),
        "tool_count": tool_count,
        "providers": {
            "model": {
                "state": state.get("state"),
                "device": state.get("device"),
                "gpu_name": state.get("gpu_name"),
                "cuda_available": state.get("cuda_available"),
            }
        },
    }


@router.get("/api/v1/diagnostics")
async def diagnostics(request: Request) -> dict[str, Any]:
    """CUA/Playwright diagnostics: tool list + system info."""
    import platform  # noqa: PLC0415

    tools = await request.app.state.fastmcp.list_tools()
    tool_names = sorted(t.name for t in tools)
    manager = request.app.state.manager
    state = manager.status()
    return {
        "status": "ok",
        "server": "MiDashengLM-Gen MCP",
        "version": __version__,
        "uptime_seconds": int(time.time() - _STARTED),
        "tool_count": len(tool_names),
        "tools": [{"name": n} for n in tool_names],
        "system": {
            "windows": platform.system() == "Windows",
            "platform": platform.platform(),
            "model_state": state.get("state"),
            "gpu": state.get("gpu_name"),
            "device": state.get("device"),
        },
        "errors": [],
    }
