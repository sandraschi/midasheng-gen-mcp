"""Audio file serving for generated scenes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

router = APIRouter(tags=["audio"])


@router.get("/api/audio/{scene_id}")
async def serve_audio(scene_id: str, request: Request) -> FileResponse:
    scene = request.app.state.store.get_scene(scene_id)
    if scene is None:
        raise HTTPException(status_code=404, detail=f"Scene {scene_id} not found")
    path = Path(scene["file_path"])
    if not path.exists():
        raise HTTPException(status_code=410, detail="Audio file is missing from disk")
    return FileResponse(
        path,
        media_type="audio/wav",
        filename=f"{scene_id}.wav",
    )
