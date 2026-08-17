"""Built-in example scene captions for the webapp."""

from __future__ import annotations

from fastapi import APIRouter

from ...samples import SAMPLES

router = APIRouter(tags=["samples"])


@router.get("/api/samples")
async def list_samples() -> dict[str, object]:
    return {"samples": SAMPLES, "count": len(SAMPLES)}
