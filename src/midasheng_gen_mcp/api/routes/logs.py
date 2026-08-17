"""Log query endpoint (webapp Logs page)."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Query

from ...logs import query_logs

router = APIRouter(tags=["logs"])


@router.get("/api/logs")
async def logs(
    source: str | None = None,
    level: str | None = None,
    search: str | None = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> dict[str, Any]:
    return query_logs(source=source, level=level, search=search, limit=limit)
