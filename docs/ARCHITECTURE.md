# Architecture

## Overview

```
Claude Desktop (stdio)          Browser / Cursor (HTTP)
        |                              |
        v                              v
+----------------------------+   +-----------------------------+
|  midasheng_gen_mcp.main    |   |  FastAPI app (port 11159)   |
|  (FastMCP stdio transport) |   |  /api/* REST + /mcp MCP     |
+----------------------------+   +-----------------------------+
             |                            |
             +-------------+--------------+
                           v
                  Shared FastMCP instance
                  (server.py, module-level)
                           |
                           v
              +----------------------------+
              |   ModelManager (lazy)      |
              |   torch + transformers     |
              |   MiDashengLM-Gen 2.9B     |
              |   CUDA fp16 ~12 GB VRAM (fp32)     |
              +----------------------------+
                           |
                           v
              +----------------------------+
              |  SceneStore (SQLite WAL)   |
              |  data/scenes/*.wav         |
              +----------------------------+
```

The webapp (Vite on 11160) proxies `/api`, `/mcp`, `/docs` to the backend
in dev; in production it is served statically behind the same origin.

## Generation pipeline

1. Caption views are composed into the tagged prompt: `<|caption|> ...`
   `<|asr|> ...` `<|speech|> ...` `<|sfx|> ...` `<|music|> ...`
   `<|env|> ...` with `<|unknown|>` for absent views (`jobs.build_prompt`).
2. `ModelManager.generate` serializes on an asyncio lock, auto-loads the
   checkpoint if needed, and runs `model.generate()` (10-step Euler ODE,
   CFG 2.0, learned stop head) on a worker thread.
3. Audio is written as 16 kHz mono WAV; a scene row and a job row persist
   in SQLite. The REST path runs this through the async `JobRunner` so the
   webapp can poll progress.

## Concurrency

- Single GPU: `ModelManager._lock` serializes load + generate.
- SQLite: WAL mode, one connection per call, busy timeout 30 s, write
  lock for inserts/deletes - safe under stdio + HTTP simultaneously.
- FastMCP 3.4.4: the streamable-HTTP lifespan is passed to the FastAPI app
  (`lifespan=mcp_http.lifespan`) - without it POST /mcp 500s.

## Model state machine

`not_installed` (model extra missing) -> `model_missing` (checkpoint not
downloaded) -> `unloaded` -> `loading` -> `ready`; `error` on load failure
(recoverable via retry). `download_model` is idempotent (snapshot_download).

## Ports (fleet registry 11159/11160)

| Port | Service |
|------|---------|
| 11159 | Backend: FastAPI + FastMCP HTTP /mcp + REST /api |
| 11160 | Frontend: Vite dev server (webapp) |

## Data layout

```
data/
  midasheng.db      SQLite: scenes + jobs (WAL)
  scenes/           scene_<hex>.wav (16 kHz mono)
  midasheng.log     file log (plus ring buffer for /api/logs)
```

## Key files

| File | Role |
|------|------|
| `src/midasheng_gen_mcp/server.py` | Shared FastMCP instance, lifespan, FastAPI build, CORS |
| `src/midasheng_gen_mcp/model_manager.py` | Lazy model lifecycle + generation |
| `src/midasheng_gen_mcp/jobs.py` | Async job runner + prompt builder |
| `src/midasheng_gen_mcp/db.py` | SQLite scenes/jobs store |
| `src/midasheng_gen_mcp/main.py` | Dual transport entry point |
| `webapp/src/pages/Generate.tsx` | Caption builder + job polling |

