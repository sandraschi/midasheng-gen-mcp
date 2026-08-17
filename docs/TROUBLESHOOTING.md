# Troubleshooting

## Server doesn't appear in Claude Desktop
**Cause**: Config JSON is malformed, or the entry point can't import.
**Fix**: Validate at jsonlint.com, check for trailing commas; run
`uv run python -m midasheng_gen_mcp` in a terminal and read the traceback.

## "command not found: uv"
**Cause**: uv not installed or not in PATH.
**Fix**: `winget install astral-sh.uv`, restart the terminal.

## Model state is "not_installed"
**Cause**: torch/transformers not installed (optional extra).
**Fix**: `uv sync --extra model` (or re-run start.ps1 which does it).

## Model state is "model_missing"
**Cause**: The ~6 GB checkpoint is not in the Hugging Face cache.
**Fix**: `audio_scene(operation="download_model")`, `just model-download`,
or Settings > Download Model. Requires disk space (~10 GB free).

## Model state is "error"
**Cause**: Load failed (often CUDA OOM or bad GPU state).
**Fix**: Read `error_message` from status; unload other models, then
`load_model` again. Restart the server if the GPU is wedged.

## Generation is very slow
**Cause**: Running on CPU instead of CUDA.
**Fix**: Check `device` in status. Set `MIDASHENG_DEVICE=cuda` with a
CUDA-capable GPU and at least 6 GB free VRAM. CPU is 10-50x slower.

## CUDA out of memory during load
**Cause**: Other models (Ollama, LM Studio) hold VRAM.
**Fix**: Unload them, or unload this model when idle
(`audio_scene(operation="unload_model")`).

## POST /mcp returns 500 "StreamableHTTPSessionManager not initialized"
**Cause**: FastMCP lifespan not propagated to the parent ASGI app.
**Fix**: Already handled in this repo (`lifespan=mcp_http.lifespan` in
`build_web_app`); if you changed the server code, keep that line.

## Webapp shows "Offline" / no backend
**Cause**: Backend not running or port conflict.
**Fix**: `just serve` (start.ps1 clears zombies first). Check
`http://127.0.0.1:11159/api/health` returns 200.

## Chat page: "No local LLM detected"
**Cause**: Ollama not running or not on 11434.
**Fix**: Start Ollama; set `MIDASHENG_OLLAMA_URL` if customized. The Chat
page uses your local Ollama, not the scene model.

## Hugging Face download is slow or blocked
**Cause**: Network path to huggingface.co.
**Fix**: Set `HF_ENDPOINT=https://hf-mirror.com` for a China mirror, or
download the repo manually and place it in the HF cache.

## Generated audio is silent or truncated
**Cause**: Stop threshold too low/high for the scene.
**Fix**: Lower `stop_threshold` (0.3-0.4) for longer scenes; raise it for
tighter ones. Try a different `seed`.

## Port 11159/11160 already in use
**Cause**: A zombie process from a previous run.
**Fix**: start.ps1 kills port zombies automatically; or
`Get-NetTCPConnection -LocalPort 11159 | ForEach-Object { Stop-Process $_.OwningProcess -Force }`.
