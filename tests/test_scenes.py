"""Scene store CRUD + pagination."""

from __future__ import annotations

import pytest

from midasheng_gen_mcp.db import SceneStore


@pytest.fixture()
def store(tmp_path) -> SceneStore:
    return SceneStore(tmp_path / "test.db")


def test_insert_and_get(store: SceneStore) -> None:
    sid = store.insert_scene(
        caption={"caption": "rain"},
        params={"eval_cfg": 2.0},
        file_path="C:/tmp/rain.wav",
        duration_seconds=3.5,
        sample_rate=16000,
    )
    scene = store.get_scene(sid)
    assert scene is not None
    assert scene["caption"]["caption"] == "rain"
    assert scene["duration_seconds"] == 3.5
    assert scene["audio_url"] == f"/api/audio/{sid}"


def test_pagination_has_more(store: SceneStore) -> None:
    for i in range(5):
        store.insert_scene(caption={"caption": f"scene {i}"}, file_path=f"C:/tmp/{i}.wav")
    page1 = store.list_scenes(limit=2, offset=0)
    assert len(page1["items"]) == 2
    assert page1["has_more"] is True
    page3 = store.list_scenes(limit=2, offset=4)
    assert len(page3["items"]) == 1
    assert page3["has_more"] is False
    assert page1["total"] == 5


def test_delete(store: SceneStore) -> None:
    sid = store.insert_scene(caption={"caption": "x"}, file_path="C:/tmp/x.wav")
    assert store.delete_scene(sid) is True
    assert store.delete_scene(sid) is False
    assert store.get_scene(sid) is None


def test_stats(store: SceneStore) -> None:
    for i in range(3):
        store.insert_scene(
            caption={"caption": f"scene {i}"},
            file_path=f"C:/tmp/{i}.wav",
            duration_seconds=2.0,
        )
    stats = store.stats()
    assert stats["scene_count"] == 3
    assert stats["total_seconds"] == 6.0


def test_job_lifecycle(store: SceneStore) -> None:
    jid = store.create_job()
    store.update_job(jid, status="running", progress=0.5, message="generating")
    job = store.get_job(jid)
    assert job is not None
    assert job["status"] == "running"
    assert job["progress"] == 0.5
    store.update_job(jid, status="done", scene_id="scene_x")
    job = store.get_job(jid)
    assert job["status"] == "done"
    assert job["scene_id"] == "scene_x"
    assert job["finished_at"] is not None
