"""In-memory ring-buffer log store + file logging setup.

Serves GET /api/logs and the webapp Logs page without reading files on
every request. Thread-safe via a lock.
"""

from __future__ import annotations

import logging
import threading
from collections import deque
from datetime import UTC, datetime
from typing import Any

from .config import settings


class RingBufferHandler(logging.Handler):
    """Logging handler that keeps the last N records in a deque."""

    def __init__(self, capacity: int = 500) -> None:
        super().__init__()
        self.capacity = capacity
        self._records: deque[dict[str, Any]] = deque(maxlen=capacity)
        self._lock = threading.Lock()

    def emit(self, record: logging.LogRecord) -> None:
        entry = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "source": record.name,
            "message": record.getMessage(),
        }
        with self._lock:
            self._records.append(entry)

    def query(
        self,
        source: str | None = None,
        level: str | None = None,
        search: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        with self._lock:
            rows = list(self._records)
        if source:
            rows = [r for r in rows if source.lower() in r["source"].lower()]
        if level:
            rows = [r for r in rows if r["level"].upper() == level.upper()]
        if search:
            needle = search.lower()
            rows = [
                r for r in rows if needle in r["message"].lower() or needle in r["source"].lower()
            ]
        return rows[-limit:]


_ring = RingBufferHandler()


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger: console + ring buffer + optional file."""
    root = logging.getLogger()
    root.setLevel(level)

    if not any(isinstance(h, RingBufferHandler) for h in root.handlers):
        root.addHandler(_ring)

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        root.addHandler(console)

    try:
        settings.ensure_dirs()
        file_handler = logging.FileHandler(settings.log_path, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        root.addHandler(file_handler)
    except OSError:
        # Data dir may be read-only in packaged installs; ring buffer still works.
        root.warning("midasheng: could not open log file at %s", settings.log_path)


def query_logs(
    source: str | None = None,
    level: str | None = None,
    search: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    rows = _ring.query(source=source, level=level, search=search, limit=limit)
    return {"entries": rows, "count": len(rows), "total_matching": len(rows)}
