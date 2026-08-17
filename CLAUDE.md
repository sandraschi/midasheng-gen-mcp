# CLAUDE.md - midasheng-gen-mcp

## Session Context (MiDashengLM-Gen Audio)

You can generate and manage mixed audio scenes (speech + music + SFX +
ambience) with a local LLM-driven flow matching model.

**Before starting work:**
1. Check model state: `audio_scene(operation="status")`
2. Check recent scenes: `audio_scene(operation="list", limit=5)`

**At end of work:**
- Keep generated scenes indexed (they persist automatically in SQLite)
- The model loads lazily on first generate - no preload needed

## Development rules

- Use `uv run python` (never naked python)
- Run `just lint` + `just test` before committing; `just web-check` after
  webapp changes
- The heavy inference stack is optional (`uv sync --extra model`) - tools
  must never fake success when it is missing (declared state machine)
- Do not edit `mcpb/src/` - it is a staging copy; fix `src/` and re-pack
- No em dashes in any file
