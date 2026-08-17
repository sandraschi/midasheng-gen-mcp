"""Lazy-loading ModelManager for the MiDashengLM-Gen model.

The heavy inference stack (torch, torchaudio, transformers, soundfile) is
imported lazily inside methods so the server boots, registers tools, and
passes lint/tests without the `model` extra installed. The manager exposes
a declared state machine:

    not_installed -> model_missing -> unloaded -> loading -> ready
                                                      |-> error (recoverable)

All generation runs on a worker thread (the transformers generate loop is
blocking) guarded by an asyncio lock so concurrent tool calls serialize on
the single GPU.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from .config import settings

logger = logging.getLogger("midasheng_gen_mcp.model")

STATE_NOT_INSTALLED = "not_installed"
STATE_MODEL_MISSING = "model_missing"
STATE_UNLOADED = "unloaded"
STATE_LOADING = "loading"
STATE_READY = "ready"
STATE_ERROR = "error"


class ModelError(RuntimeError):
    """Raised when the model cannot be used for generation."""


class ModelManager:
    """Owns the MiDashengLM-Gen model lifecycle and generation."""

    def __init__(self, model_id: str | None = None) -> None:
        self.model_id = model_id or settings.hf_model_id
        self.state = STATE_NOT_INSTALLED
        self.error_message: str | None = None
        self.loaded_at: float | None = None
        self._model: Any = None
        self._lock = asyncio.Lock()
        self._torch = None
        self._transformers = None

    # ---- dependency / availability checks (cheap, no heavy imports) ----

    def _import_inference_stack(self) -> None:
        """Import torch/transformers lazily; raises ModelError with guidance."""
        try:
            import torch  # noqa: PLC0415
            import transformers  # noqa: PLC0415

            self._torch = torch
            self._transformers = transformers
        except ImportError as exc:
            raise ModelError(
                f"Inference stack not installed. Run: uv sync --extra model (missing: {exc.name})"
            ) from exc

    def _model_in_hf_cache(self) -> bool:
        try:
            from huggingface_hub import hf_hub_download  # noqa: PLC0415

            hf_hub_download(self.model_id, "config.json", local_files_only=True)
            return True
        except Exception:
            return False

    def check_stack(self) -> dict[str, Any]:
        """Cheap availability probe used by status tools and the webapp."""
        try:
            import torch  # noqa: PLC0415
            import transformers  # noqa: PLC0415

            torch_ok, tf_ok = True, True
            torch_version = getattr(torch, "__version__", "?")
            tf_version = getattr(transformers, "__version__", "?")
            cuda = bool(getattr(torch, "cuda", lambda: False) and torch.cuda.is_available())
            device_name = torch.cuda.get_device_name(0) if cuda else None
        except ImportError as exc:
            torch_ok, tf_ok = False, False
            torch_version = tf_version = None
            cuda = False
            device_name = None
            logger.info("Inference stack missing: %s", exc.name)

        return {
            "torch_installed": torch_ok,
            "transformers_installed": tf_ok,
            "torch_version": torch_version,
            "transformers_version": tf_version,
            "cuda_available": cuda,
            "gpu_name": device_name,
            "device": settings.resolve_device(),
            "model_id": self.model_id,
        }

    # ---- lifecycle ----

    async def download_model(self) -> dict[str, Any]:
        """Download the checkpoint from Hugging Face (idempotent)."""
        async with self._lock:
            try:
                from huggingface_hub import snapshot_download  # noqa: PLC0415
            except ImportError as exc:
                raise ModelError("huggingface_hub missing - run: uv sync --extra model") from exc

            def _run() -> str:
                path = snapshot_download(self.model_id)
                logger.info("Model downloaded to %s", path)
                return path

            path = await asyncio.to_thread(_run)
            if self.state == STATE_NOT_INSTALLED:
                self.state = STATE_UNLOADED
            return {"path": path, "model_id": self.model_id}

    async def load_model(self) -> dict[str, Any]:
        """Load the model onto the resolved device. Idempotent."""
        async with self._lock:
            if self.state == STATE_READY:
                return self._status_locked()
            self._import_inference_stack()
            self.state = STATE_LOADING
            self.error_message = None
            try:

                def _load() -> Any:
                    model = self._transformers.AutoModel.from_pretrained(
                        self.model_id, trust_remote_code=True
                    )
                    device = settings.resolve_device()
                    dtype = settings.dtype
                    if dtype == "fp16" and device == "cuda":
                        # EXPERIMENTAL: fp16 hits Float/Half matmul errors in
                        # this custom model (verified 2026-08-17); fp32 is the
                        # working path. ~12 GB VRAM.
                        model = model.half().cuda()
                    else:
                        model = model.float()
                        if device == "cuda":
                            model = model.cuda()
                    return model

                self._model = await asyncio.to_thread(_load)
                self.state = STATE_READY
                self.loaded_at = time.time()
                logger.info(
                    "MiDashengLM-Gen loaded on %s",
                    settings.resolve_device(),
                )
            except Exception as exc:
                self.state = STATE_ERROR
                self.error_message = str(exc)
                logger.exception("Model load failed")
                raise ModelError(f"Model load failed: {exc}") from exc
            return self._status_locked()

    async def unload_model(self) -> dict[str, Any]:
        async with self._lock:
            self._model = None
            self.state = STATE_UNLOADED
            self.loaded_at = None
            if self._torch is not None and self._torch.cuda.is_available():
                self._torch.cuda.empty_cache()
            return self._status_locked()

    # ---- generation ----

    async def generate(
        self,
        prompt: str,
        *,
        eval_cfg: float = 2.0,
        stop_threshold: float = 0.5,
        min_stop_step: int = 5,
        seed: int | None = None,
    ) -> dict[str, Any]:
        """Generate an audio scene. Returns numpy audio + sample rate.

        Raises ModelError with recovery options when the stack or the
        checkpoint is missing.
        """
        async with self._lock:
            if self.state == STATE_NOT_INSTALLED:
                raise ModelError(
                    "Inference stack not installed. Run: uv sync --extra model",
                    error_type="model_deps_missing",
                )
            if self.state == STATE_MODEL_MISSING or not self._model_in_hf_cache():
                raise ModelError(
                    "Model checkpoint not downloaded. Use the download_model "
                    "operation or run start.ps1 (offers the download).",
                    error_type="model_missing",
                )
            if self.state != STATE_READY:
                await self.load_model()

            model = self._model
            torch = self._torch

            def _run() -> tuple[Any, int]:
                kwargs: dict[str, Any] = {
                    "eval_cfg": eval_cfg,
                    "stop_threshold": stop_threshold,
                    "min_stop_step": min_stop_step,
                }
                if seed is not None:
                    kwargs["seed"] = seed
                device = settings.resolve_device()
                if device == "cuda" and settings.dtype == "fp16":
                    # fp16 experimental: autocast resolves the Float/Half
                    # matmul mismatch the reference impl avoids by running
                    # under autocast.
                    with torch.no_grad(), torch.autocast("cuda", dtype=torch.float16):
                        result = model.generate(prompt, **kwargs)
                else:
                    # fp32 (default) on cuda or cpu: plain inference.
                    with torch.no_grad():
                        result = model.generate(prompt, **kwargs)
                return result["audio"], int(result["sample_rate"])

            try:
                audio, sample_rate = await asyncio.to_thread(_run)
            except Exception as exc:
                logger.exception("Generation failed")
                raise ModelError(f"Generation failed: {exc}") from exc
            return {"audio": audio, "sample_rate": sample_rate}

    # ---- status ----

    def status(self) -> dict[str, Any]:
        return self._status_locked()

    def _status_locked(self) -> dict[str, Any]:
        stack = self.check_stack()
        payload: dict[str, Any] = {
            "state": self.state,
            "error_message": self.error_message,
            "model_id": self.model_id,
            "loaded_at": self.loaded_at,
        }
        payload.update(stack)
        return payload


manager = ModelManager()
