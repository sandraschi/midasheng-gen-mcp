<p align="center">
  <img src="assets/icon.png" alt="MiDashengLM-Gen" width="128" />
</p>

<h1 align="center">midasheng-gen-mcp</h1>

<p align="center"><b>Type a scene. Get the whole soundscape.</b><br />
An MCP server and dark-theme webapp that generate coherent 16 kHz mixed audio
scenes - speech, music, sound effects and ambience - in one pass from text,
powered by <a href="https://arxiv.org/abs/2608.11804">MiDashengLM-Gen</a>
(Xiaomi Research). Runs entirely on your GPU.</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="License: Apache-2.0" /></a>
  <a href="#requirements"><img src="https://img.shields.io/badge/python-3.12%2B-3776AB.svg" alt="Python 3.12+" /></a>
  <a href="docs/ARCHITECTURE.md"><img src="https://img.shields.io/badge/FastMCP-3.4.4-brightgreen.svg" alt="FastMCP 3.4.4" /></a>
  <a href="docs/CONFIGURATION.md"><img src="https://img.shields.io/badge/inference-local%20CUDA-important.svg" alt="Local CUDA inference" /></a>
  <a href="docs/WRAPPEE.md"><img src="https://img.shields.io/badge/languages-9-blue.svg" alt="9 languages" /></a>
  <a href="INSTALL.md"><img src="https://img.shields.io/badge/works%20with-Claude%20Desktop%20%C2%B7%20Cursor%20%C2%B7%20opencode-lightgrey.svg" alt="MCP hosts" /></a>
  <a href="docs/ARCHITECTURE.md"><img src="https://img.shields.io/badge/webapp-React%20%2B%20Vite%20(dark)-informational.svg" alt="Webapp" /></a>
</p>

<p align="center">
  <a href="#quick-install"><b>Quick install</b></a> ·
  <a href="#example-prompts">Example prompts</a> ·
  <a href="#documentation">Documentation</a>
</p>

---

One call in Claude, Cursor or opencode - "a comedy club scene with a
punchline, crowd laughter and a jazz sting" - and you get a single 16 kHz WAV
with all of it. Speech lands close to dedicated TTS quality in 9 languages
with emotion control, and the whole ~6 GB model stays on your GPU until you
unload it.

## What this wraps

**MiDashengLM-Gen** - the first end-to-end trained general text-to-audio
model (per the paper): an LLM drives per-token flow matching to generate
variable-length audio scenes with speech intelligibility approaching
dedicated TTS (Seed-TTS WER 12.15% -> 2.79% vs 1.24% for dedicated TTS).
Supports **9 languages** and emotion control. Checkpoint auto-downloads
from [Hugging Face](https://huggingface.co/mispeech/midashenglm-gen)
(~6 GB). Model weights are never bundled - see [docs/WRAPPEE.md](docs/WRAPPEE.md).

## Features

**How it runs**: a local FastMCP 3.4 server (stdio for Claude Desktop, HTTP
`/mcp` for Cursor/webapp) with a React dashboard. The model loads lazily on
first generate and stays on the GPU until unloaded.

| Direction | Artifacts | Notes |
|-----------|-----------|-------|
| **Hands-in** | structured caption (caption/asr/speech/sfx/music/env views), guidance + seed params | Via MCP tool, REST, or webapp |
| **Hands-out** | 16 kHz mono WAV scenes, indexed in SQLite, browsable/exportable | `audio_scene(operation="export")` or webapp |

- Generate whole soundscapes in one call - crowd laughter + jazz sting +
  comedy speech, or rain + thunder + forest ambience
- Speech intelligibility near dedicated TTS quality, 9 languages, emotion
  control through the `speech` view
- Scene library with pagination, audio playback, and export in the webapp
- Async job API for long generations; Prefab UI cards in chat
- Variable-length output via the learned stop head - no fixed-duration cuts

## Quick Install

The fastest path is the .mcpb bundle for Claude Desktop (see
[INSTALL.md](INSTALL.md) for all options):

1. Download `midasheng-gen-mcp-v0.1.0.mcpb` from
   [Releases](https://github.com/sandraschi/midasheng-gen-mcp/releases/latest)
2. Drag it onto Claude Desktop
3. First use will download the ~6 GB checkpoint automatically

Or clone and double-click `start.bat` for the full stack (backend + webapp).

## Example Prompts

- "Generate a comedy club scene: a punchline, crowd laughter, and a jazz
  band sting" -> `audio_scene(operation="generate", caption="A comedian
  delivering a punchline followed by uproarious crowd laughter", asr="And
  that is why I never buy cheap luggage anymore!", speech="expressive
  comedic male voice", music="sudden upbeat jazz band sting", sfx="crowd
  laughter", env="intimate comedy club")`
- "Make a thunderstorm at night in a forest" -> `audio_scene(operation="generate",
  caption="A rolling thunderstorm in a forest at night", sfx="distant thunder
  and heavy rain", env="dense forest", seed=42)`
- "What's the model state?" -> `audio_scene(operation="status")`

## Documentation

| Doc | Contents |
|-----|----------|
| [Installation](INSTALL.md) | All install methods, prerequisites |
| [Onboarding](docs/ONBOARDING.md) | First-run model download, GPU checks, pitfalls |
| [Wrapped app](docs/WRAPPEE.md) | MiDashengLM-Gen paper, weights, license, demo |
| [Architecture](docs/ARCHITECTURE.md) | System architecture, ports, data flow |
| [Configuration](docs/CONFIGURATION.md) | Env vars, config options |
| [Tool Reference](docs/TOOLS.md) | All available tools |
| [Development](docs/DEVELOPMENT.md) | Contributing, local setup |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues |

## Requirements

- Windows/Linux/macOS with a CUDA GPU (RTX 4090 class: ~12 GB VRAM (fp32); CPU
  inference works but is slow)
- Python 3.12+ via [uv](https://docs.astral.sh/uv/), Node.js 20+, bun
  (auto-installed by `start.ps1` on naked PCs)
- ~10 GB free disk (checkpoint ~6 GB + torch stack)

## License

Apache-2.0 (model and this wrapper). See the use-restrictions section in
the upstream repo: no unlawful/military use, no harm to minors or groups.

