"""audio_scene - the MiDashengLM-Gen portmanteau.

[RATIONALE] One entry point for the entire audio scene surface. A dozen
atomic tools (generate_scene, list_scenes, delete_scene, ...) would bloat
the host context; the operation enum acts as a built-in catalog and keeps
generation parameters grouped in a single schema.
"""

from __future__ import annotations

import shutil
from typing import Annotated, Any, Literal

from fastmcp import Context
from pydantic import Field

from ...config import settings
from ...db import SceneStore
from ...jobs import build_prompt
from ...model_manager import ModelError, manager
from ...samples import SAMPLES
from ...server import mcp
from ...utils import _error_response, ok_response

_READONLY = {"readonly": True}
_MUTATING = {}
_DESTRUCTIVE = {"readonly": False, "destructive": True}


def _store() -> SceneStore:
    return SceneStore(settings.db_path)


@mcp.tool(annotations=_READONLY, version="0.1.0")
async def audio_scene(
    operation: Annotated[
        Literal[
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
        ],
        Field(description="The operation to perform."),
    ],
    caption: Annotated[
        str | None,
        Field(description="Overall scene description (required for generate)."),
    ] = None,
    asr: Annotated[
        str | None,
        Field(description="Speech transcript to be spoken in the scene."),
    ] = None,
    speech: Annotated[
        str | None,
        Field(description="Speaker characteristics - voice, emotion, style."),
    ] = None,
    sfx: Annotated[
        str | None,
        Field(description="Sound effects description."),
    ] = None,
    music: Annotated[
        str | None,
        Field(description="Music description."),
    ] = None,
    env: Annotated[
        str | None,
        Field(description="Environment / ambience description."),
    ] = None,
    eval_cfg: Annotated[
        float,
        Field(description="Classifier-free guidance scale (default 2.0)."),
    ] = 2.0,
    stop_threshold: Annotated[
        float,
        Field(description="Stop prediction threshold for audio truncation."),
    ] = 0.5,
    min_stop_step: Annotated[
        int,
        Field(description="Minimum generation steps before stopping."),
    ] = 5,
    seed: Annotated[
        int | None,
        Field(description="Random seed for reproducible generation."),
    ] = None,
    limit: Annotated[
        int,
        Field(description="Max results for list (1-100).", ge=1, le=100),
    ] = 20,
    offset: Annotated[
        int,
        Field(description="Pagination offset for list.", ge=0),
    ] = 0,
    scene_id: Annotated[
        str | None,
        Field(description="Scene id for get / delete / export."),
    ] = None,
    destination: Annotated[
        str | None,
        Field(description="Output path for export (file or directory)."),
    ] = None,
    confirm: Annotated[
        bool,
        Field(description="Must be True for delete (destructive)."),
    ] = False,
    ctx: Context = None,
) -> dict[str, Any]:
    """Generate and manage 16 kHz mixed audio scenes from text.

    [RATIONALE] Consolidates scene lifecycle (generate, browse, export,
    model management) into one catalog-style tool so agents discover the
    full surface from the operation enum.

    ## Return Format
    {"success": bool, "message": str, "scene"?: {...}, "items"?: [...],
     "total"?: int, "has_more"?: bool, "state"?: {...}}

    ## Examples
    audio_scene(operation="status")
    audio_scene(operation="generate", caption="Rain and thunder in a forest",
                sfx="thunder rumbles", env="forest at night", seed=42)
    audio_scene(operation="list", limit=10)
    audio_scene(operation="delete", scene_id="scene_abc", confirm=True)

    Notes
     - Generate is synchronous: allow up to ~3 minutes on a 4090.
     - Model loads on first generate (state: not_installed / model_missing
       returns recovery options, never a fake success).
    """
    try:
        if operation == "status":
            return ok_response("Model status", state=manager.status())

        if operation == "samples":
            return ok_response(
                f"Found {len(SAMPLES)} example scenes",
                samples=SAMPLES,
                count=len(SAMPLES),
            )

        if operation == "download_model":
            result = await manager.download_model()
            return ok_response("Model checkpoint ready", **result)

        if operation == "load_model":
            result = await manager.load_model()
            return ok_response("Model loaded", state=result)

        if operation == "unload_model":
            result = await manager.unload_model()
            return ok_response("Model unloaded", state=result)

        if operation == "generate":
            caption_dict = {
                "caption": caption,
                "asr": asr,
                "speech": speech,
                "sfx": sfx,
                "music": music,
                "env": env,
            }
            prompt = build_prompt(caption_dict)
            params = {
                "eval_cfg": eval_cfg,
                "stop_threshold": stop_threshold,
                "min_stop_step": min_stop_step,
                "seed": seed,
            }
            result = await manager.generate(
                prompt,
                eval_cfg=eval_cfg,
                stop_threshold=stop_threshold,
                min_stop_step=min_stop_step,
                seed=seed,
            )
            from ...audio import wav_metadata, write_wav  # noqa: PLC0415

            scene_id_new = f"scene_{abs(hash(prompt + str(seed))) % (10**12):012d}"
            wav_path = settings.scenes_dir / f"{scene_id_new}.wav"
            write_wav(result["audio"], result["sample_rate"], wav_path)
            meta = wav_metadata(wav_path) or {}
            store = _store()
            store.insert_scene(
                scene_id=scene_id_new,
                caption=caption_dict,
                params=params,
                file_path=str(wav_path),
                duration_seconds=meta.get("duration_seconds"),
                sample_rate=result["sample_rate"],
                size_bytes=wav_path.stat().st_size if wav_path.exists() else None,
            )
            scene = store.get_scene(scene_id_new)
            return ok_response(
                f"Scene {scene_id_new} generated ({meta.get('duration_seconds', 0)}s)",
                scene=scene,
            )

        if operation == "list":
            store = _store()
            return ok_response(
                "Scenes listed",
                **store.list_scenes(limit=limit, offset=offset),
            )

        if operation == "get":
            if not scene_id:
                return _error_response("scene_id is required for get", "validation")
            scene = _store().get_scene(scene_id)
            if scene is None:
                return _error_response(f"Scene {scene_id} not found", "not_found")
            return ok_response(f"Scene {scene_id}", scene=scene)

        if operation == "delete":
            if not scene_id:
                return _error_response("scene_id is required for delete", "validation")
            if not confirm:
                return _error_response(
                    "delete requires confirm=True (destructive)",
                    "confirmation_required",
                    suggestions=["Re-run with confirm=True to delete the scene and its WAV file."],
                )
            scene = _store().get_scene(scene_id)
            if scene is None:
                return _error_response(f"Scene {scene_id} not found", "not_found")
            deleted = _store().delete_scene(scene_id)
            try:
                shutil.rmtree(str(scene["file_path"]), ignore_errors=True)
            except OSError:
                pass
            return ok_response(
                f"Deleted scene {scene_id}" if deleted else f"Scene {scene_id} already gone",
                deleted=deleted,
            )

        if operation == "export":
            if not scene_id:
                return _error_response("scene_id is required for export", "validation")
            if not destination:
                return _error_response("destination is required for export", "validation")
            scene = _store().get_scene(scene_id)
            if scene is None:
                return _error_response(f"Scene {scene_id} not found", "not_found")
            src = scene["file_path"]
            target = str(destination)
            if target.lower().endswith(".wav"):
                shutil.copyfile(src, target)
            else:
                import os  # noqa: PLC0415

                os.makedirs(target, exist_ok=True)
                target = os.path.join(target, f"{scene_id}.wav")
                shutil.copyfile(src, target)
            return ok_response(f"Exported scene {scene_id} to {target}", path=target)

        return _error_response(f"Unknown operation: {operation}", "validation")
    except ModelError as exc:
        return _error_response(
            str(exc),
            error_type=getattr(exc, "error_type", "model_error"),
            suggestions=[
                "Run: uv sync --extra model",
                "Run the download_model operation or start.ps1 to fetch the checkpoint",
                "Check GPU/VRAM availability (status operation)",
            ],
            recovery_options=["download_model", "load_model", "status"],
        )
    except Exception as exc:
        return _error_response(str(exc), "general")
