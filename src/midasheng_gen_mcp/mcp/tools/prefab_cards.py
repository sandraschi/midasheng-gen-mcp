"""Prefab UI cards for in-chat status and scene browsing."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from fastmcp.tools import ToolResult
from prefab_ui import PrefabApp
from prefab_ui.components import Div, Heading, Row, Text
from pydantic import Field

from ...config import settings
from ...db import SceneStore
from ...model_manager import manager
from ...server import mcp


@mcp.tool(app=True, annotations={"readonly": True}, version="0.1.0")
async def show_scene_status_card(ctx: Context = None) -> ToolResult:
    """Show MiDashengLM-Gen model and library status as a rich card.

    ## Return Format
    ToolResult with content dict: {"success": bool, "state": {...}}

    ## Examples
    await show_scene_status_card()
    """
    state = manager.status()
    store = SceneStore(settings.db_path)
    stats = store.stats()

    with PrefabApp(title="MiDashengLM-Gen Status") as app:
        Heading(f"Model: {state.get('state', 'unknown')}")
        Row(label="Model ID", value=state.get("model_id", "-"))
        Row(label="Device", value=state.get("device", "-"))
        Row(label="GPU", value=state.get("gpu_name") or "CPU only")
        Row(label="CUDA", value="yes" if state.get("cuda_available") else "no")
        Row(label="torch", value=state.get("torch_version") or "not installed")
        Row(label="transformers", value=state.get("transformers_version") or "not installed")
        Div()
        Heading(f"Library: {stats.get('scene_count', 0)} scenes")
        Row(
            label="Total audio",
            value=f"{stats.get('total_seconds', 0.0):.1f} s",
        )
        if state.get("error_message"):
            Text(f"Error: {state['error_message']}")

    summary = (
        f"Model state: {state.get('state')} on {state.get('device')}; "
        f"{stats.get('scene_count', 0)} scenes in library."
    )
    return ToolResult(
        content=summary,
        structured_content=PrefabApp(view=app, title="MiDashengLM-Gen Status"),
    )


@mcp.tool(app=True, annotations={"readonly": True}, version="0.1.0")
async def show_scene_card(
    scene_id: Annotated[str, Field(description="Scene id to display.")],
    ctx: Context = None,
) -> ToolResult:
    """Show one generated scene as a rich in-chat card.

    ## Return Format
    ToolResult with content dict: {"success": bool, "scene": {...}}

    ## Examples
    await show_scene_card(scene_id="scene_abc")
    """
    store = SceneStore(settings.db_path)
    scene = store.get_scene(scene_id)
    if scene is None:
        summary = f"Scene {scene_id} not found."
        with PrefabApp(title="Scene Not Found") as app:
            Text(summary)
        return ToolResult(
            content=summary,
            structured_content=PrefabApp(view=app, title="Scene Not Found"),
            is_error=True,
        )

    caption = scene.get("caption") or {}
    with PrefabApp(title=f"Scene {scene_id}") as app:
        Heading(caption.get("caption") or "(no caption)")
        Row(label="Duration", value=f"{scene.get('duration_seconds') or 0:.2f} s")
        Row(label="Sample rate", value=str(scene.get("sample_rate") or "-"))
        Row(label="Created", value=str(scene.get("created_at") or "-"))
        for key in ("asr", "speech", "sfx", "music", "env"):
            value = (caption.get(key) or "").strip()
            if value and value != "<|unknown|>":
                Row(label=key, value=value)

    summary = (
        f"Scene {scene_id}: {scene.get('duration_seconds') or 0:.2f}s - "
        f"{caption.get('caption') or 'no caption'}"
    )
    return ToolResult(
        content=summary,
        structured_content=PrefabApp(view=app, title=f"Scene {scene_id}"),
    )
