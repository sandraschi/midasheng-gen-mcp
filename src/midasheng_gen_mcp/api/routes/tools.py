"""Dynamic tool discovery for the webapp Tools page."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

router = APIRouter(tags=["tools"])


@router.get("/api/tools")
async def list_tools(request: Request) -> dict[str, Any]:
    tools = await request.app.state.fastmcp.list_tools()
    items = []
    for tool in tools:
        schema = getattr(tool, "parameters", None) or {}
        items.append(
            {
                "name": tool.name,
                "description": tool.description or "",
                "schema": schema,
                "is_app": bool(getattr(tool, "is_app", False)),
            }
        )
    return {"tools": items, "count": len(items)}
