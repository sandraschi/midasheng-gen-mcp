"""Async generation jobs: submit, poll, list."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

router = APIRouter(tags=["jobs"])


class GenerateRequest(BaseModel):
    caption: str = Field(description="Overall scene description (required).")
    asr: str | None = None
    speech: str | None = None
    sfx: str | None = None
    music: str | None = None
    env: str | None = None
    eval_cfg: float = Field(default=2.0, ge=0.5, le=5.0)
    stop_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    min_stop_step: int = Field(default=5, ge=1, le=50)
    seed: int | None = None


@router.post("/api/generate", status_code=202)
async def submit_generation(payload: GenerateRequest, request: Request) -> dict[str, Any]:
    """Submit a generation job. Poll GET /api/jobs/{id} for progress."""
    caption = {
        "caption": payload.caption,
        "asr": payload.asr,
        "speech": payload.speech,
        "sfx": payload.sfx,
        "music": payload.music,
        "env": payload.env,
    }
    params = {
        "eval_cfg": payload.eval_cfg,
        "stop_threshold": payload.stop_threshold,
        "min_stop_step": payload.min_stop_step,
        "seed": payload.seed,
    }
    try:
        result = await request.app.state.runner.submit(caption, params)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return result


@router.get("/api/jobs/{job_id}")
async def job_status(job_id: str, request: Request) -> dict[str, Any]:
    job = request.app.state.runner.job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return {"success": True, "job": job}


@router.get("/api/jobs")
async def list_jobs(
    request: Request,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    return request.app.state.runner.list_jobs(limit=limit, offset=offset)
