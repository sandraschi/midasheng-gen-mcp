"""Model lifecycle over REST (download / load / unload)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from ...model_manager import ModelError

router = APIRouter(tags=["model"])


@router.post("/api/model/download")
async def download_model(request: Request) -> dict[str, Any]:
    try:
        result = await request.app.state.manager.download_model()
    except ModelError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"success": True, **result}


@router.post("/api/model/load")
async def load_model(request: Request) -> dict[str, Any]:
    try:
        result = await request.app.state.manager.load_model()
    except ModelError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"success": True, "state": result}


@router.post("/api/model/unload")
async def unload_model(request: Request) -> dict[str, Any]:
    result = await request.app.state.manager.unload_model()
    return {"success": True, "state": result}
