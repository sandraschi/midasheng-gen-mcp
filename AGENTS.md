# AGENTS.md - midasheng-gen-mcp

## Purpose

FastMCP 3.4 server wrapping MiDashengLM-Gen (Xiaomi Research): unified
16 kHz mixed audio scene generation (speech, music, SFX, ambience) from
structured text captions. LLM-driven autoregressive flow matching with a
Qwen3-1.7B backbone (2.9B params total). Apache-2.0, runs locally on CUDA.

## Layout

```
src/midasheng_gen_mcp/
  server.py          FastMCP instance (shared), lifespan, FastAPI build
  main.py            Dual transport entry (stdio default, HTTP on MCP_PORT)
  config.py          Settings from MIDASHENG_* env vars
  model_manager.py   Lazy torch/transformers load, generate, state machine
  jobs.py            Async job runner + prompt builder
  db.py              SQLite scenes + jobs store (WAL)
  samples.py         Built-in example captions
  audio.py           WAV metadata + persistence helpers
  logs.py            Ring-buffer log store
  mcp/tools/         audio_scene portmanteau, help, prefab cards
  api/routes/        REST: health, dashboard, scenes, jobs, audio, tools,
                     skills, samples, logs, llm, model, capabilities
  skills/midasheng-gen/SKILL.md
webapp/              React + Vite + Tailwind SOTA dashboard (port 11160)
tests/               15 pytest tests (no torch required)
```

## Key facts

- Ports: backend 11159 (REST + MCP /mcp), frontend 11160 (registered in
  WEBAPP_PORTS.md)
- The shared FastMCP instance lives in `server.py`; tool modules import
  `mcp` from there (registration at import time - no import = no tool)
- `uv sync --extra model` installs torch/transformers; without it the
  server runs but reports `not_installed` state (declared, not fake)
- Model checkpoint: `mispeech/midashenglm-gen` on Hugging Face (~6 GB),
  auto-download via start.ps1 or the download_model operation
- Structured caption: <|caption|> <|asr|> <|speech|> <|sfx|> <|music|>
  <|env|> views; absent views become <|unknown|>
- MCP generate is synchronous; the webapp uses the async job API
  (POST /api/generate -> job id -> GET /api/jobs/{id})

## Commands

```
just lint         ruff check + format --check
just test         pytest (light, no torch)
just web-check    tsc --noEmit + biome check (webapp)
just ci           lint + test
just mcpb-pack    fresh-stage MCPB bundle
just model-download   installs model extra + downloads checkpoint
```

## Conventions

- Fleet standards: mcp-central-docs (AGENTS.md gate, SOTA, WEBAPP_PORTS)
- No em dashes in any file; ASCII only
- Dialogic returns: {success, message, ...}; _error_response auto-logs
- Prefab cards for list/status surfaces (show_scene_status_card etc.)
