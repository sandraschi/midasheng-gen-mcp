# Configuration

All settings come from environment variables (`MIDASHENG_*`). Copy
`.env.example` to `.env` for local overrides - one source of truth, no
fallback chains.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MIDASHENG_BACKEND_PORT` | `11159` | Backend port (REST + MCP /mcp) |
| `MIDASHENG_FRONTEND_PORT` | `11160` | Vite frontend port |
| `MIDASHENG_HF_MODEL_ID` | `mispeech/midashenglm-gen` | Hugging Face model repo |
| `MIDASHENG_DEVICE` | `auto` | `auto` (CUDA when available), `cuda`, or `cpu` |
| `MIDASHENG_PRELOAD_MODEL` | `0` | `1` loads the model at server startup instead of lazily |
| `MIDASHENG_DEFAULT_CFG` | `2.0` | Default classifier-free guidance |
| `MIDASHENG_DEFAULT_STOP_THRESHOLD` | `0.5` | Default stop-head threshold |
| `MIDASHENG_DEFAULT_SEED` | (none) | Default generation seed |
| `MIDASHENG_DATA_DIR` | `./data` | SQLite index + WAV output directory |
| `MIDASHENG_OLLAMA_URL` | `http://127.0.0.1:11434` | Local LLM endpoint for the Chat page |
| `MIDASHENG_OLLAMA_MODEL` | (auto-detect) | Chat model override |

## Setting Variables

In `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "midasheng-gen": {
      "command": "uv",
      "args": ["--directory", "C:\\path\\to\\midasheng-gen-mcp", "run", "python", "-m", "midasheng_gen_mcp"],
      "env": {
        "MIDASHENG_DEVICE": "cuda",
        "MIDASHENG_DATA_DIR": "D:/data/midasheng"
      }
    }
  }
}
```

## Model extras

The inference stack is an optional dependency group:

```bash
uv sync --extra model      # torch + transformers + audio libs (~3 GB)
uv sync --extra dev        # ruff + pytest (CI, no torch)
```

## Port conflicts

Registered in `mcp-central-docs/operations/WEBAPP_PORTS.md` (11159/11160).
`start.ps1` clears zombie listeners before binding. If another machine
uses the range, change both `MIDASHENG_BACKEND_PORT` and the Vite proxy in
`webapp/vite.config.ts`.
