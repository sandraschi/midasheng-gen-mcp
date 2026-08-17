"""Scene browsing, deletion, and export over REST."""

from __future__ import annotations

import shutil
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, Request

router = APIRouter(tags=["scenes"])


@router.get("/api/scenes")
async def list_scenes(
    request: Request,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    store = request.app.state.store
    result = store.list_scenes(limit=limit, offset=offset)
    result["items"] = [_public_scene(s) for s in result["items"]]
    return result


@router.get("/api/scenes/{scene_id}")
async def get_scene(scene_id: str, request: Request) -> dict[str, Any]:
    scene = request.app.state.store.get_scene(scene_id)
    if scene is None:
        raise HTTPException(status_code=404, detail=f"Scene {scene_id} not found")
    return _public_scene(scene)


@router.delete("/api/scenes/{scene_id}")
async def delete_scene(scene_id: str, request: Request) -> dict[str, Any]:
    store = request.app.state.store
    scene = store.get_scene(scene_id)
    if scene is None:
        raise HTTPException(status_code=404, detail=f"Scene {scene_id} not found")
    deleted = store.delete_scene(scene_id)
    shutil.rmtree(scene["file_path"], ignore_errors=True)
    return {"success": True, "deleted": deleted, "scene_id": scene_id}


def _public_scene(scene: dict[str, Any]) -> dict[str, Any]:
    """Strip internal file paths; expose the audio URL only."""
    public = {k: v for k, v in scene.items() if k != "file_path"}
    return public
