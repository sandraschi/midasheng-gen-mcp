# Installing midasheng-gen-mcp

Generate coherent mixed audio scenes (speech + music + SFX + ambience) from
text with the MiDashengLM-Gen model, running locally on your GPU.

## Prerequisites

Install these if you don't have them already:

| Tool | Purpose | Install |
|------|---------|---------|
| Claude Desktop | Required host for the MCP bundle | [download](https://claude.ai/download) |
| Git | Clone repo (Option C/D only) | `winget install Git.Git` |
| Python + uv | Run server (Option C/D only) | `winget install astral-sh.uv` |
| Node.js | mcpb CLI (Option B only) | `winget install OpenJS.NodeJS` |
| CUDA GPU | Model inference (RTX 4090 class, ~6 GB VRAM) | NVIDIA driver only |

> Windows: all installs via [winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/)
> macOS/Linux: use your package manager (brew/apt). CPU inference works but is slow.

First run downloads the ~6 GB model checkpoint from Hugging Face (one
time). Keep ~10 GB free disk.

## Option A - Drag and Drop (Recommended)

1. Go to [Releases](https://github.com/sandraschi/midasheng-gen-mcp/releases/latest)
2. Download `midasheng-gen-mcp-v0.1.0.mcpb`
3. Open Claude Desktop -> drag the file onto the window
   *Or*: Settings -> MCP Servers -> Install from file

## Option B - mcpb CLI

```bash
# Requires Node.js (see Prerequisites)
npx @anthropic-ai/mcpb install https://github.com/sandraschi/midasheng-gen-mcp
```

## Option C - Manual Configuration

1. Clone: `git clone https://github.com/sandraschi/midasheng-gen-mcp`
2. Install deps: `cd midasheng-gen-mcp && uv sync --extra model`
3. Add to Claude Desktop config:

```json
{
  "mcpServers": {
    "midasheng-gen": {
      "command": "uv",
      "args": ["--directory", "C:\\path\\to\\midasheng-gen-mcp", "run", "python", "-m", "midasheng_gen_mcp"],
      "env": { "PYTHONUNBUFFERED": "1" }
    }
  }
}
```

Config file location:
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

4. Restart Claude Desktop

## Option D - Full Stack (Webapp + Backend)

Double-click `start.bat` (Windows) or run `pwsh ./start.ps1`. The script
auto-installs uv/Node/bun, installs the inference stack, offers to download
the model checkpoint, clears the ports, starts backend (11159) + webapp
(11160), and opens your browser.

See [docs/ONBOARDING.md](docs/ONBOARDING.md) for the first-run model
download flow and GPU checks.

## Verify Installation

After installing, open Claude Desktop and type:

> "What is the state of the audio scene model?"

You should see: a status dict with `"state"` (not_installed / model_missing
/ unloaded / ready) and GPU/device info. Then run
`audio_scene(operation="download_model")` for the checkpoint, or:

> "Generate a thunderstorm at night in a forest"

You should see: a generated scene id with duration, and a WAV saved to
`data/scenes/`.

## Troubleshooting

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues
(no CUDA, model missing, slow generation, port conflicts).
