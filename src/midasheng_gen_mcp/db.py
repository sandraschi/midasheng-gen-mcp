"""SQLite persistence for generated scenes and background jobs.

One connection per call (WAL mode) - safe under FastMCP concurrency and
the dual transport (stdio + HTTP) without cross-client lock contention.
"""

from __future__ import annotations

import sqlite3
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_SCHEMA = """
CREATE TABLE IF NOT EXISTS scenes (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    caption_json TEXT NOT NULL,
    params_json TEXT NOT NULL,
    duration_seconds REAL,
    sample_rate INTEGER,
    file_path TEXT NOT NULL,
    size_bytes INTEGER,
    status TEXT NOT NULL DEFAULT 'done',
    job_id TEXT
);
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'queued',
    progress REAL DEFAULT 0.0,
    message TEXT DEFAULT '',
    scene_id TEXT,
    created_at TEXT NOT NULL,
    finished_at TEXT,
    error TEXT
);
CREATE INDEX IF NOT EXISTS idx_scenes_created ON scenes(created_at DESC);
"""

_WRITE_LOCK = threading.Lock()


def _now() -> str:
    return datetime.now(UTC).isoformat()


class SceneStore:
    """SQLite-backed store for scenes and jobs."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    # ---- scenes ----

    def insert_scene(
        self,
        *,
        scene_id: str | None = None,
        caption: dict[str, Any],
        params: dict[str, Any] | None = None,
        file_path: str,
        duration_seconds: float | None = None,
        sample_rate: int | None = None,
        size_bytes: int | None = None,
        job_id: str | None = None,
    ) -> str:
        import json

        params = params or {}
        scene_id = scene_id or f"scene_{uuid.uuid4().hex[:12]}"
        with _WRITE_LOCK, self._connect() as conn:
            conn.execute(
                """INSERT INTO scenes
                   (id, created_at, caption_json, params_json, duration_seconds,
                    sample_rate, file_path, size_bytes, status, job_id)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    scene_id,
                    _now(),
                    json.dumps(caption),
                    json.dumps(params),
                    duration_seconds,
                    sample_rate,
                    file_path,
                    size_bytes,
                    "done",
                    job_id,
                ),
            )
        return scene_id

    def get_scene(self, scene_id: str) -> dict[str, Any] | None:

        with self._connect() as conn:
            row = conn.execute("SELECT * FROM scenes WHERE id=?", (scene_id,)).fetchone()
        if row is None:
            return None
        return self._row_to_scene(row)

    def list_scenes(self, limit: int = 20, offset: int = 0) -> dict[str, Any]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM scenes ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
            total = conn.execute("SELECT COUNT(*) FROM scenes").fetchone()[0]
        items = [self._row_to_scene(r) for r in rows]
        return {
            "items": items,
            "total": total,
            "has_more": offset + len(items) < total,
            "limit": limit,
            "offset": offset,
        }

    def delete_scene(self, scene_id: str) -> bool:
        with _WRITE_LOCK, self._connect() as conn:
            cur = conn.execute("DELETE FROM scenes WHERE id=?", (scene_id,))
            return cur.rowcount > 0

    def stats(self) -> dict[str, Any]:
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) FROM scenes").fetchone()[0]
            row = conn.execute(
                "SELECT COUNT(*), COALESCE(SUM(duration_seconds),0) FROM scenes"
            ).fetchone()
        return {
            "scene_count": total,
            "total_seconds": float(row[1] or 0.0),
        }

    @staticmethod
    def _row_to_scene(row: sqlite3.Row) -> dict[str, Any]:
        import json

        return {
            "id": row["id"],
            "created_at": row["created_at"],
            "caption": json.loads(row["caption_json"]),
            "params": json.loads(row["params_json"]),
            "duration_seconds": row["duration_seconds"],
            "sample_rate": row["sample_rate"],
            "file_path": row["file_path"],
            "size_bytes": row["size_bytes"],
            "status": row["status"],
            "job_id": row["job_id"],
            "audio_url": f"/api/audio/{row['id']}",
        }

    # ---- jobs ----

    def create_job(self, kind: str = "generate") -> str:
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        with _WRITE_LOCK, self._connect() as conn:
            conn.execute(
                "INSERT INTO jobs (id, status, created_at) VALUES (?,?,?)",
                (job_id, "queued", _now()),
            )
        return job_id

    def update_job(
        self,
        job_id: str,
        *,
        status: str | None = None,
        progress: float | None = None,
        message: str | None = None,
        scene_id: str | None = None,
        error: str | None = None,
    ) -> None:
        fields: list[str] = []
        values: list[Any] = []
        if status is not None:
            fields.append("status=?")
            values.append(status)
            if status in ("done", "failed", "cancelled"):
                fields.append("finished_at=?")
                values.append(_now())
        if progress is not None:
            fields.append("progress=?")
            values.append(progress)
        if message is not None:
            fields.append("message=?")
            values.append(message)
        if scene_id is not None:
            fields.append("scene_id=?")
            values.append(scene_id)
        if error is not None:
            fields.append("error=?")
            values.append(error)
        if not fields:
            return
        values.append(job_id)
        with _WRITE_LOCK, self._connect() as conn:
            conn.execute(f"UPDATE jobs SET {', '.join(fields)} WHERE id=?", values)

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        return dict(row) if row else None

    def list_jobs(self, limit: int = 20, offset: int = 0) -> dict[str, Any]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
            total = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        return {
            "items": [dict(r) for r in rows],
            "total": total,
            "has_more": offset + len(rows) < total,
        }
