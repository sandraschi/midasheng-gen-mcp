# midasheng-gen-mcp

Generate coherent 16 kHz **mixed audio scenes** from text - speech, music,
sound effects, and ambience in one pass - powered by
[MiDashengLM-Gen](https://arxiv.org/abs/2608.11804) (Xiaomi Research), an
LLM-driven autoregressive flow matching model (Qwen3-1.7B backbone, 2.9B
params total). Apache-2.0, runs entirely on your GPU.

## What this wraps

**MiDashengLM-Gen** - the first end-to-end trained general text-to-audio
model (per the paper): an LLM drives per-token flow matching to generate
variable-length audio scenes with speech intelligibility approaching
dedicated TTS (Seed-TTS WER 12.15% -> 2.79% vs 1.24% for dedicated TTS).
Supports **9 languages** and emotion control. Checkpoint auto-downloads
from [Hugging Face](https://huggingface.co/mispeech/midashenglm-gen)
(~6 GB). Model weights are never bundled - see [docs/WRAPPEE.md](docs/WRAPPEE.md).

## What You Can Do

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

