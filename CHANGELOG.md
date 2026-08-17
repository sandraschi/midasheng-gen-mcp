# Changelog

## [0.1.0] - 2026-08-17

### Added

- Initial release: MiDashengLM-Gen MCP wrapper (FastMCP 3.4.4, dual transport)
- `audio_scene` portmanteau: status, generate, list, get, delete, export,
  samples, download_model, load_model, unload_model
- `midasheng_help` multi-level help + Prefab UI cards (status, scene)
- Async job API for the webapp (submit/poll/list), SQLite scene + job index
- REST surface: health, diagnostics, dashboard, capabilities, tools, skills,
  samples, scenes, jobs, audio, logs, model lifecycle, LLM chat proxy
- SOTA React/Vite webapp: Dashboard, Generate, Scenes, Inbox, Tools, Skills,
  Chat, Settings, Help, Logs, API Docs
- Lazy model loading (torch/transformers optional extra), declared
  not_installed / model_missing states with recovery options
- MCPB packaging (3-4-100 prompts), justfile, start.ps1/start.bat with
  naked-PC Require-Command + model download gate
- CI workflow (Windows), Playwright e2e smoke suite, 15 pytest tests
