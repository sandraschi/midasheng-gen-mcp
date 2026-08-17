"""Tool registration surface (FastMCP import-time registration)."""

from __future__ import annotations

import pytest

from midasheng_gen_mcp.server import create_mcp


@pytest.mark.asyncio
async def test_tool_surface() -> None:
    mcp = create_mcp()
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    assert "audio_scene" in names
    assert "midasheng_help" in names
    assert "show_scene_status_card" in names
    assert "show_scene_card" in names


@pytest.mark.asyncio
async def test_audio_scene_operations() -> None:
    mcp = create_mcp()
    tool = await mcp.get_tool("audio_scene")
    schema = tool.parameters if hasattr(tool, "parameters") else {}
    properties = (schema or {}).get("properties", {})
    op = properties.get("operation", {}).get("enum", [])
    for expected in (
        "status",
        "generate",
        "list",
        "get",
        "delete",
        "samples",
        "download_model",
        "load_model",
        "unload_model",
        "export",
    ):
        assert expected in op
