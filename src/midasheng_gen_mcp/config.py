"""Configuration for midasheng-gen-mcp.

All settings come from environment variables (MIDASHENG_*) or defaults.
One .env file at the repo root is the source of truth; no fallback chain.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, "").strip() or default)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, "").strip() or default)
    except ValueError:
        return default


@dataclass
class Settings:
    """Server-wide configuration loaded once at startup."""

    repo_name: str = "midasheng-gen-mcp"
    version: str = "0.1.0"

    # Fleet port registry (WEBAPP_PORTS.md): backend 11159, frontend 11160
    backend_port: int = field(default_factory=lambda: _env_int("MIDASHENG_BACKEND_PORT", 11159))
    frontend_port: int = field(default_factory=lambda: _env_int("MIDASHENG_FRONTEND_PORT", 11160))

    hf_model_id: str = os.environ.get("MIDASHENG_HF_MODEL_ID", "mispeech/midashenglm-gen")
    device: str = os.environ.get("MIDASHENG_DEVICE", "auto").strip().lower()
    # fp32 (default, works) | fp16 (experimental - custom model raises
    # Float/Half matmul errors under fp16 as of 2026-08-17)
    dtype: str = os.environ.get("MIDASHENG_DTYPE", "fp32").strip().lower()
    preload_model: bool = os.environ.get("MIDASHENG_PRELOAD_MODEL", "0").strip() in (
        "1",
        "true",
        "yes",
    )

    default_cfg: float = field(default_factory=lambda: _env_float("MIDASHENG_DEFAULT_CFG", 2.0))
    default_stop_threshold: float = field(
        default_factory=lambda: _env_float("MIDASHENG_DEFAULT_STOP_THRESHOLD", 0.5)
    )
    default_seed: int | None = field(
        default_factory=lambda: _env_int("MIDASHENG_DEFAULT_SEED", 0) or None
    )

    ollama_url: str = os.environ.get("MIDASHENG_OLLAMA_URL", "http://127.0.0.1:11434")
    ollama_model: str = os.environ.get("MIDASHENG_OLLAMA_MODEL", "").strip()

    # Data location: repo-local data/ by default; override for installed bundles.
    data_dir: Path = field(
        default_factory=lambda: Path(os.environ.get("MIDASHENG_DATA_DIR", str(Path.cwd() / "data")))
    )

    def __post_init__(self) -> None:
        self.data_dir = Path(self.data_dir)
        self.scenes_dir = self.data_dir / "scenes"
        self.db_path = self.data_dir / "midasheng.db"
        self.log_path = self.data_dir / "midasheng.log"

    def ensure_dirs(self) -> None:
        """Create data directories; call at startup. Raises on failure."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.scenes_dir.mkdir(parents=True, exist_ok=True)

    def resolve_device(self) -> str:
        """Map the configured device string to a torch device name."""
        if self.device == "cuda":
            return "cuda"
        if self.device == "cpu":
            return "cpu"
        return "cuda" if self._cuda_available() else "cpu"

    @staticmethod
    def _cuda_available() -> bool:
        try:
            import torch  # noqa: PLC0415 - lazy import keeps CI light

            return bool(torch.cuda.is_available())
        except ImportError:
            return False


settings = Settings()
