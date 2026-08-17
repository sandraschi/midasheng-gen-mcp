# Changelog

## [0.1.1] - 2026-08-18

### Fixed

- CUDA torch: PyPI default wheel is CPU-only (torch 2.13+); pinned the CUDA
  build via [tool.uv.sources]/[[tool.uv.index]] (pytorch-cu126)
- Generation dtype: fp16 raises Float/Half matmul errors in the custom model;
  fp32 is now the default (verified: 10 s thunderstorm in 34 s, comedy club
  scene in ~2.5 min on the 4090). Added MIDASHENG_DTYPE toggle.
- Added scripts/download-model.ps1 (reliable background download)

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

