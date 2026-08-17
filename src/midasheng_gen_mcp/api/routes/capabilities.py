"""Capability introspection (WEBAPP_STANDARDS section 1.4)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

router = APIRouter(tags=["capabilities"])

_CAPABILITIES = [
    {"id": "generate", "name": "Audio scene generation", "available": True},
    {"id": "model_management", "name": "Model download/load/unload", "available": True},
    {"id": "scene_library", "name": "Scene browsing and export", "available": True},
    {"id": "chat", "name": "Local LLM chat (Ollama)", "available": True},
]


@router.get("/api/capabilities")
async def capabilities() -> dict[str, Any]:
    return {"capabilities": _CAPABILITIES, "count": len(_CAPABILITIES)}
