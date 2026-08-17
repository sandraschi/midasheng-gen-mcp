# Development Setup

## Tools Required

Install all of these before continuing:

```bash
# Windows (winget)
winget install astral-sh.uv
winget install Git.Git
winget install OpenJS.NodeJS
winget install Oven-sh.Bun
winget install Casey.Just

# Verify
uv --version
git --version
node --version
bun --version
just --version
```

## Setup

```bash
git clone https://github.com/sandraschi/midasheng-gen-mcp
cd midasheng-gen-mcp
uv sync --extra model --extra dev
cd webapp && bun install && cd ..
```

## Common Tasks

```bash
just lint          # ruff check + format --check
just test          # pytest (light, no torch required)
just web-check     # tsc --noEmit + biome check (webapp)
just ci            # lint + test
just e2e           # Playwright smoke (backend + Vite must be running)
just mcpb-pack     # fresh-stage MCPB bundle to dist/
just model-download  # install model extra + download checkpoint
```

## Running locally

```bash
just serve         # start.ps1 -Headless: backend 11159 + frontend 11160
```

Or run pieces separately:

```bash
# backend only (REST + MCP HTTP)
uv run python -m midasheng_gen_mcp --mode http --port 11159

# stdio (Claude Desktop style)
uv run python -m midasheng_gen_mcp

# frontend only (expects backend on 11159)
cd webapp && bun run dev
```

## Testing without the GPU model

The pytest suite is designed to run without torch: `ModelManager` imports
the inference stack lazily and tools return declared `not_installed` /
`model_missing` states. Generation integration tests would require the
model extra + checkpoint; they are intentionally not part of the default
suite (documented declared gap - no undeclared mocks).

## Code Standards

- Fleet standards: `mcp-central-docs/standards/` (SOTA, TOOL_DESIGN,
  WEBAPP_SOTA, PACKAGING)
- Ruff with the repo's `pyproject.toml` config; Biome for the webapp
- ASCII only in all files (no em dashes); PowerShell scripts target
  Windows PowerShell 5.1 (`powershell.exe`, no `&&`)
- Dialogic returns: `{success, message, ...}` + `_error_response` helper
- MCP tools register at import time on the shared instance in `server.py`

## Onboarding note

The wrappee here is the MiDashengLM-Gen model itself (not a host app):
`docs/ONBOARDING.md` covers the stack + checkpoint install. The webapp
shows a model-missing state until onboarding succeeds (declared MOCK-free -
the state is real and actionable).
