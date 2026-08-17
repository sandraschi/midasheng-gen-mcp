## MiDashengLM-Gen MCP - coding guidance

- Python: use `uv run python`, ruff for lint/format, FastMCP 3.4.4+
- The heavy inference stack (torch, transformers) is an optional extra -
  tools must return declared failure states when it is missing, never
  simulated success
- MCP tools register at import time on the shared instance in `server.py`
- Webapp: React + Vite + Tailwind (dark), Zustand stores in `src/store/`,
  API client in `src/lib/api.ts`
- Ports: backend 11159, frontend 11160
- Tests: `uv run pytest` (light, no torch); webapp: `bun run check`
- ASCII only in all files (no em dashes)
