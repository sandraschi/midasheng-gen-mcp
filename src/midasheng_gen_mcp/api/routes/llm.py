"""Local LLM discovery + chat proxy for the webapp Chat page.

Probes Ollama (11434), LM Studio (1234), and vLLM (8000) on mount, per
WEBAPP_SOTA_STANDARDS section VI. All requests go to the local provider -
never the cloud - unless the user configures a base URL.
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ...config import settings

router = APIRouter(tags=["llm"])

_PROVIDERS = [
    {"name": "ollama", "port": 11434, "base": "http://127.0.0.1:11434", "probe": "/api/tags"},
    {"name": "lmstudio", "port": 1234, "base": "http://127.0.0.1:1234", "probe": "/v1/models"},
    {"name": "vllm", "port": 8000, "base": "http://127.0.0.1:8000", "probe": "/v1/models"},
]


class ChatRequest(BaseModel):
    messages: list[dict[str, str]]
    model: str | None = None
    temperature: float = 0.7


async def _probe(client: httpx.AsyncClient, provider: dict[str, Any]) -> dict[str, Any]:
    try:
        resp = await client.get(f"{provider['base']}{provider['probe']}", timeout=3.0)
        if resp.status_code == 200:
            return {**provider, "detected": True}
    except httpx.HTTPError:
        pass
    return {**provider, "detected": False}


@router.get("/api/llm/discover")
async def discover_llm() -> dict[str, Any]:
    """Probe all local providers in parallel (3s timeout each)."""
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*[_probe(client, p) for p in _PROVIDERS])
    detected = [r for r in results if r["detected"]]
    return {
        "providers": detected,
        "detected": [r["name"] for r in detected],
        "default_model": settings.ollama_model,
    }


@router.get("/api/llm/providers")
async def llm_providers() -> dict[str, Any]:
    return await discover_llm()


@router.post("/api/llm/chat")
async def chat(payload: ChatRequest, request: Request) -> dict[str, Any]:
    """Forward a chat completion to the local Ollama instance."""
    base = settings.ollama_url.rstrip("/")
    model = payload.model or settings.ollama_model
    if not model:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                tags = await client.get(f"{base}/api/tags")
                tags.raise_for_status()
                model = tags.json()["models"][0]["name"]
        except (httpx.HTTPError, KeyError, IndexError) as exc:
            raise HTTPException(
                status_code=503,
                detail="No local LLM detected. Start Ollama or set MIDASHENG_OLLAMA_MODEL.",
            ) from exc

    body = {
        "model": model,
        "messages": payload.messages,
        "stream": False,
        "options": {"temperature": payload.temperature},
    }
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            resp = await client.post(f"{base}/api/chat", json=body)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Ollama error: {exc}") from exc

    content = data.get("message", {}).get("content", "")
    return {"success": True, "content": content, "model": model, "provider": "ollama"}
