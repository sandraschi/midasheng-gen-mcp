"""Audio helpers: WAV metadata (stdlib-only) and file persistence.

Persistence of generated audio uses soundfile when the model extra is
installed; metadata readback uses the stdlib `wave` module so the webapp
and REST API work without torch.
"""

from __future__ import annotations

import wave
from pathlib import Path


def wav_metadata(path: str | Path) -> dict[str, float | int] | None:
    """Read sample rate, channels, and duration from a PCM WAV file."""
    try:
        with wave.open(str(path), "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            channels = wf.getnchannels()
            duration = frames / rate if rate else 0.0
            return {
                "sample_rate": rate,
                "channels": channels,
                "duration_seconds": round(duration, 3),
            }
    except (wave.Error, OSError, FileNotFoundError):
        return None


def write_wav(audio: object, sample_rate: int, path: str | Path) -> Path:
    """Persist numpy audio to a WAV file (soundfile; requires model extra)."""
    try:
        import soundfile as sf  # noqa: PLC0415
    except ImportError as exc:
        raise RuntimeError("soundfile not installed - run: uv sync --extra model") from exc
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), audio, sample_rate)
    return path
