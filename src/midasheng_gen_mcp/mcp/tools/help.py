"""midasheng_help - multi-level help for the audio scene surface."""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from ...server import mcp
from ...utils import ok_response

_INDEX = """# MiDashengLM-Gen MCP - help index

Generate coherent 16 kHz audio scenes that blend speech, music, sound
effects, and environment from structured text captions. The model is
MiDashengLM-Gen (Xiaomi Research): an LLM backbone (Qwen3-1.7B) driving
per-token autoregressive flow matching. Apache-2.0, runs locally on CUDA.

Topics: overview | generate | prompt_format | model_state | examples

## Overview
- One tool surface: audio_scene(operation=...)
- Scenes are stored as WAV files indexed in SQLite (data/ directory)
- Generate is synchronous for agents; the webapp uses async jobs

## Quick start
1. audio_scene(operation="status") - check stack + model state
2. audio_scene(operation="download_model") - fetch checkpoint (~6 GB)
3. audio_scene(operation="load_model") - load onto GPU
4. audio_scene(operation="generate", caption="...", sfx="...", ...)
5. audio_scene(operation="list") - browse generated scenes
"""

_TOPICS: dict[str, str] = {
    "overview": _INDEX,
    "generate": """## generate

Synchronous generation of one mixed audio scene. Returns the scene id,
duration, and the audio URL. Blocking up to ~3 minutes on a 4090.

Parameters (all views optional except caption):
- caption: overall scene description (required)
- asr: speech transcript to synthesize
- speech: voice, emotion, style of the speaker
- sfx: sound effects
- music: music description
- env: environment / ambience
- eval_cfg: classifier-free guidance (default 2.0)
- stop_threshold: stop-head threshold (default 0.5)
- min_stop_step: minimum autoregressive steps (default 5)
- seed: reproducibility

Example:
audio_scene(operation="generate",
    caption="Rain and thunder in a forest",
    sfx="distant thunder and heavy rain",
    env="forest at night",
    seed=42)
""",
    "prompt_format": """## Structured caption format

The model consumes a single prompt built from tagged views. Absent views
become <|unknown|>. The tool assembles this automatically.

<|caption|> overall scene
<|asr|> transcript to be spoken
<|speech|> speaker characteristics
<|sfx|> sound effects
<|music|> music description
<|env|> environment / ambience

Best results come from concrete, contrasting descriptions per view. For
speech intelligibility, keep the asr view clean prose.
""",
    "model_state": """## Model state machine

- not_installed: run `uv sync --extra model` (torch + transformers)
- model_missing: checkpoint not downloaded - run download_model
- unloaded: checkpoint present, not in GPU memory
- loading: load in progress (idempotent)
- ready: ready to generate
- error: load failed - check error_message, retry load_model

The status operation returns GPU info, VRAM device, and versions.
""",
    "examples": """## Example scenes

Use audio_scene(operation="samples") to fetch the built-in gallery:
comedy club, rainy cafe, thunderstorm, jazz lounge, news report,
forest dawn. Each is a ready-made caption dict.
""",
}


@mcp.tool(annotations={"readonly": True}, version="0.1.0")
async def midasheng_help(
    topic: Annotated[
        str | None,
        Field(
            description="Help topic: overview | generate | prompt_format | model_state | examples"
        ),
    ] = None,
    ctx: Context = None,
) -> dict[str, Any]:
    """Multi-level help and documentation for MiDashengLM-Gen MCP.

    ## Return Format
    {"success": bool, "help": str, "topics": list[str]}

    ## Examples
    midasheng_help()
    midasheng_help(topic="generate")
    """
    if topic is None:
        return ok_response("Help index", help=_INDEX, topics=sorted(_TOPICS.keys()))
    body = _TOPICS.get(topic)
    if body is None:
        return ok_response(
            "Unknown topic",
            help=f"Unknown topic '{topic}'. Available: {', '.join(sorted(_TOPICS))}",
            topics=sorted(_TOPICS.keys()),
        )
    return ok_response(f"Help: {topic}", help=body, topics=sorted(_TOPICS.keys()))
