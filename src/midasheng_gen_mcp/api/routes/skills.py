"""Skill discovery over REST (webapp Skills page)."""

from __future__ import annotations

import importlib.resources
from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["skills"])

_SKILLS = [
    {
        "name": "midasheng-gen",
        "uri": "skill://midasheng-gen/SKILL.md",
        "description": "Unified audio scene generation - speech, music, SFX, and ambience",
    }
]


def _read_skill(name: str) -> str:
    try:
        resource = importlib.resources.files("midasheng_gen_mcp.skills").joinpath(name, "SKILL.md")
        return resource.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError, ModuleNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=f"Skill {name} not found") from exc


@router.get("/api/skills")
async def list_skills() -> dict[str, Any]:
    return {"skills": _SKILLS, "count": len(_SKILLS)}


@router.get("/api/skills/{skill_name}")
async def get_skill(skill_name: str) -> dict[str, Any]:
    content = _read_skill(skill_name)
    return {"name": skill_name, "content": content}
