# MiDashengLM-Gen MCP - fleet justfile
# Naked-PC: powershell.exe (PS 5.1) ships with Windows; pwsh does not.
set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

# Start the full dev stack (backend + frontend), no browser
serve:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File start.ps1 -Headless

# Run the pytest suite (light: no torch required)
test:
    uv run pytest

# Lint + format check (ruff)
lint:
    uv run ruff check src/ tests/
    uv run ruff format --check src/ tests/

# Auto-fix lint + format
fmt:
    uv run ruff check --fix src/ tests/
    uv run ruff format src/ tests/

# Type-check + lint the webapp
web-check:
    bun --prefix webapp run check

# Playwright e2e smoke (needs running stack)
e2e:
    bun --prefix webapp run e2e

# Bundle for Claude Desktop (MCPB) - wipes and recopies src first
mcpb-pack:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/mcpb-pack.ps1

# Download the model checkpoint (idempotent)
model-download:
    uv sync --extra model
    uv run python -c "from huggingface_hub import snapshot_download; print(snapshot_download('mispeech/midashenglm-gen'))"

# Full local CI: lint + test (+ webapp check when webapp deps installed)
ci: lint test
