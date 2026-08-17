"""Dashboard KPIs: library stats + model state."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from ... import __version__

router = APIRouter(tags=["dashboard"])


@router.get("/api/dashboard")
async def dashboard(request: Request) -> dict[str, Any]:
    store = request.app.state.store
    manager = request.app.state.manager
    stats = store.stats()
    state = manager.status()
    return {
        "scene_count": stats.get("scene_count", 0),
        "total_seconds": round(float(stats.get("total_seconds", 0.0)), 1),
        "model_state": state.get("state"),
        "model_id": state.get("model_id"),
        "device": state.get("device"),
        "gpu_name": state.get("gpu_name"),
        "cuda_available": state.get("cuda_available"),
        "torch_installed": state.get("torch_installed"),
        "transformers_installed": state.get("transformers_installed"),
        "version": __version__,
        "recent": store.list_scenes(limit=5).get("items", []),
    }
