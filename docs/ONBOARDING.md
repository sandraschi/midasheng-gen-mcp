# Onboarding - First Run

MiDashengLM-Gen MCP generates audio with a local neural model. Before the
first scene can be generated, two things must be in place: the inference
stack and the ~6 GB model checkpoint.

## What you need

- A CUDA GPU (RTX 4090 class recommended; ~6 GB VRAM free). CPU works but
  generation is 10-50x slower.
- ~10 GB free disk (checkpoint ~6 GB + torch stack ~3 GB).

## Step 1 - Install the stack (one time)

The server detects a missing inference stack and reports
`state: not_installed`. Fix with:

```bash
uv sync --extra model
```

`start.ps1` does this automatically and asks before anything else.

## Step 2 - Download the model (one time)

The checkpoint is `mispeech/midashenglm-gen` on Hugging Face
([page](https://huggingface.co/mispeech/midashenglm-gen), Apache-2.0).
Three ways to fetch it:

1. **start.ps1** prompts "Download now from Hugging Face? [y/N]"
2. **Settings > Download Model** in the webapp
3. MCP: `audio_scene(operation="download_model")`

or CLI: `just model-download`

The download is ~6 GB and can take a few minutes. It is idempotent -
re-running resumes/skips.

## Step 3 - Verify

Run `audio_scene(operation="status")` or open the webapp Dashboard. You
want `state: ready` (or at least `unloaded` - generation auto-loads).

Generate a quick test:

```
audio_scene(operation="generate",
    caption="A rolling thunderstorm in a forest at night",
    sfx="distant thunder and heavy rain",
    env="dense forest at night",
    seed=42)
```

## Pitfalls

- **CUDA out of memory**: unload other models first
  (`unload_model`, or Ollama) - the model needs ~6 GB fp16.
- **Hugging Face blocked/slow**: set HF_ENDPOINT=https://hf-mirror.com for
  a China mirror, or download via the browser and place files in the HF
  cache directory.
- **No GPU**: CPU inference works but a 10 s scene can take minutes. Set
  MIDASHENG_DEVICE=cpu if you prefer no CUDA attempts.

## Money / network

No accounts, no subscriptions, no API keys. The only network traffic is
the one-time Hugging Face download. Generation is fully local.
