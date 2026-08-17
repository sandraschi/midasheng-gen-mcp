"""Background job manager for the REST webapp.

MCP tools generate synchronously (hosts wait for the result); the webapp
uses async jobs so long generations survive browser timeouts. Jobs persist
in SQLite and survive restarts (running jobs are marked interrupted).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from .audio import wav_metadata, write_wav
from .config import settings
from .db import SceneStore
from .model_manager import ModelError, manager
from .utils import ok_response

logger = logging.getLogger("midasheng_gen_mcp.jobs")

_PROMPT_TOKENS = {
    "caption": "<|caption|>",
    "asr": "<|asr|>",
    "speech": "<|speech|>",
    "sfx": "<|sfx|>",
    "music": "<|music|>",
    "env": "<|env|>",
}


def build_prompt(caption: dict[str, Any]) -> str:
    """Compose the structured multi-view caption used by MiDashengLM-Gen.

    Absent views become <|unknown|>. At minimum the caption view must be
    non-empty.
    """
    parts: list[str] = []
    for key in ("caption", "asr", "speech", "sfx", "music", "env"):
        value = str(caption.get(key) or "").strip()
        token = _PROMPT_TOKENS[key]
        if value:
            parts.append(f"{token} {value}")
        elif key == "caption":
            raise ValueError("caption view is required")
        else:
            parts.append(f"{token} <|unknown|>")
    return " ".join(parts) + " "


class JobRunner:
    """Submits and tracks generation jobs."""

    def __init__(self, store: SceneStore) -> None:
        self.store = store
        self._generate_lock = asyncio.Lock()
        self._running: dict[str, asyncio.Task[Any]] = {}

    async def submit(self, caption: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        prompt = build_prompt(caption)
        job_id = self.store.create_job(kind="generate")
        self.store.update_job(job_id, status="queued", message="queued", progress=0.0)
        task = asyncio.create_task(self._run(job_id, prompt, caption, params))
        self._running[job_id] = task
        return {"job_id": job_id, "status": "queued"}

    async def _run(
        self,
        job_id: str,
        prompt: str,
        caption: dict[str, Any],
        params: dict[str, Any],
    ) -> None:
        try:
            async with self._generate_lock:
                self.store.update_job(
                    job_id, status="running", message="loading model", progress=0.1
                )
                await manager.load_model()
                self.store.update_job(job_id, status="running", message="generating", progress=0.4)
                result = await manager.generate(
                    prompt,
                    eval_cfg=float(params.get("eval_cfg", settings.default_cfg)),
                    stop_threshold=float(
                        params.get("stop_threshold", settings.default_stop_threshold)
                    ),
                    min_stop_step=int(params.get("min_stop_step", 5)),
                    seed=params.get("seed") or settings.default_seed,
                )
                self.store.update_job(job_id, message="saving audio", progress=0.9)
                scene_id = f"scene_{job_id.split('_', 1)[1]}"
                wav_path = settings.scenes_dir / f"{scene_id}.wav"
                write_wav(result["audio"], result["sample_rate"], wav_path)
                meta = wav_metadata(wav_path) or {}
                self.store.insert_scene(
                    scene_id=scene_id,
                    caption=caption,
                    params=params,
                    file_path=str(wav_path),
                    duration_seconds=meta.get("duration_seconds"),
                    sample_rate=meta.get("sample_rate") or result["sample_rate"],
                    size_bytes=wav_path.stat().st_size if wav_path.exists() else None,
                    job_id=job_id,
                )
                self.store.update_job(
                    job_id,
                    status="done",
                    message="done",
                    progress=1.0,
                    scene_id=scene_id,
                )
        except ModelError as exc:
            logger.error("Job %s failed: %s", job_id, exc)
            self.store.update_job(job_id, status="failed", error=str(exc), progress=1.0)
        except Exception as exc:
            logger.exception("Job %s crashed", job_id)
            self.store.update_job(job_id, status="failed", error=str(exc), progress=1.0)
        finally:
            self._running.pop(job_id, None)

    def job(self, job_id: str) -> dict[str, Any] | None:
        row = self.store.get_job(job_id)
        if row is None:
            return None
        task = self._running.get(job_id)
        row["running"] = task is not None and not task.done()
        return row

    def list_jobs(self, limit: int = 20, offset: int = 0) -> dict[str, Any]:
        return self.store.list_jobs(limit=limit, offset=offset)


def job_status_payload(job: dict[str, Any]) -> dict[str, Any]:
    return ok_response(f"Job {job['id']} is {job['status']}", job=job)
