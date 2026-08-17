"""FastMCP server instance + FastAPI web app (dual transport).

FastMCP 3.4.4: the streamable-HTTP lifespan MUST be passed to the parent
ASGI app or POST /mcp/ crashes (StreamableHTTPSessionManager not
initialized). CORS follows the fleet standard - explicit localhost origins
plus an unconditional Tailscale/LAN origin regex.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP

from . import __version__
from .config import settings

logger = logging.getLogger("midasheng_gen_mcp.server")

# Single shared FastMCP instance - tool modules import `mcp` from here so
# decorators register on the same surface (registration happens at import).
mcp = FastMCP(
    "midasheng-gen",
    instructions=(
        "MiDashengLM-Gen MCP: unified audio scene generation. "
        "Generate coherent 16 kHz audio scenes blending speech, music, "
        "sound effects, and environment from structured text captions. "
        "Use audio_scene(operation='status') first to check model state, "
        "then generate scenes with audio_scene(operation='generate'). "
        "Call midasheng_help() for the full guide."
    ),
    version=__version__,
)


@mcp.lifespan()
async def lifespan(server: FastMCP) -> dict[str, Any]:
    """Startup: prepare data dirs, log model state. Never crashes boot."""
    try:
        settings.ensure_dirs()
        logger.info("Data dir ready: %s", settings.data_dir)
    except OSError as exc:
        logger.error("Data dir unavailable: %s", exc)
    state = manager_status()
    logger.info("Model state at startup: %s", state["state"])
    return {"settings": settings}


def create_mcp() -> FastMCP:
    """Return the shared FastMCP instance, ensuring tools are registered.

    Portmanteau imports register tools at import time (no import = no tool).
    Idempotent: repeated calls return the same instance.
    """
    from .mcp.tools import (  # noqa: F401, PLC0415
        audio_scene,
        prefab_cards,
    )
    from .mcp.tools import help as help_tool  # noqa: F401, PLC0415

    return mcp


def manager_status() -> dict[str, Any]:
    """Import helper: model status without importing manager at module top."""
    from .model_manager import manager  # noqa: PLC0415

    return manager.status()


def build_web_app() -> FastAPI:
    """FastAPI surface: REST routes + mounted MCP streamable HTTP app."""
    from .db import SceneStore  # noqa: PLC0415
    from .jobs import JobRunner  # noqa: PLC0415
    from .model_manager import manager  # noqa: PLC0415

    store = SceneStore(settings.db_path)
    runner = JobRunner(store)

    mcp = create_mcp()
    mcp_http = mcp.http_app(path="/")
    web = FastAPI(
        title="MiDashengLM-Gen MCP API",
        version=__version__,
        # 3.4.4 pitfall: streamable-HTTP lifespan must propagate
        lifespan=mcp_http.lifespan,
    )

    web.state.fastmcp = mcp
    web.state.mcp = mcp_http
    web.state.store = store
    web.state.runner = runner
    web.state.manager = manager

    web.add_middleware(
        CORSMiddleware,
        allow_origins=[
            f"http://localhost:{settings.frontend_port}",
            f"http://127.0.0.1:{settings.frontend_port}",
            "http://tauri.localhost",
            "https://tauri.localhost",
            "tauri://localhost",
        ],
        allow_origin_regex=(
            r"https?://(?:[a-zA-Z0-9-]+\.ts\.net|.*?\.tail-[a-f0-9]+\.ts\.net|"
            r"tauri\.localhost|localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|"
            r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}|100\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?$"
            r"|^tauri://localhost$"
        ),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # REST routes (registered via import for lint cleanliness)
    from .api.routes import audio as audio_routes  # noqa: PLC0415
    from .api.routes import capabilities as cap_routes  # noqa: PLC0415
    from .api.routes import dashboard as dash_routes  # noqa: PLC0415
    from .api.routes import health as health_routes  # noqa: PLC0415
    from .api.routes import jobs as jobs_routes  # noqa: PLC0415
    from .api.routes import llm as llm_routes  # noqa: PLC0415
    from .api.routes import logs as logs_routes  # noqa: PLC0415
    from .api.routes import model as model_routes  # noqa: PLC0415
    from .api.routes import samples as samples_routes  # noqa: PLC0415
    from .api.routes import scenes as scenes_routes  # noqa: PLC0415
    from .api.routes import skills as skills_routes  # noqa: PLC0415
    from .api.routes import tools as tools_routes  # noqa: PLC0415

    for router in (
        health_routes.router,
        dash_routes.router,
        scenes_routes.router,
        jobs_routes.router,
        audio_routes.router,
        skills_routes.router,
        tools_routes.router,
        samples_routes.router,
        logs_routes.router,
        llm_routes.router,
        model_routes.router,
        cap_routes.router,
    ):
        web.include_router(router)

    web.mount("/mcp", mcp_http)
    return web
