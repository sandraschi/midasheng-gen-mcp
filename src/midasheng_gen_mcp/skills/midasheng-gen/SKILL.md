---
name: midasheng-gen
description: Unified audio scene generation - speech, music, SFX, and ambience in one 16 kHz mix from structured text captions
---

# MiDashengLM-Gen - Audio Scene Generation

## What this server does

MiDashengLM-Gen MCP generates coherent 16 kHz mixed audio scenes from
text: speech, music, sound effects, and environmental acoustics in a
single autoregressive pass (LLM backbone + per-token flow matching).
Apache-2.0, fully local on CUDA (RTX 4090 class: ~12 GB VRAM (fp32)).

## Tool surface

### audio_scene (portmanteau)

Operations:

- status: model state, GPU info, torch/transformers versions
- generate: synchronous scene generation from structured views
- list: paginated scene browser (limit/offset, has_more)
- get: single scene metadata
- delete: remove scene + WAV (requires confirm=True)
- export: copy a scene WAV to a destination path
- samples: built-in example captions
- download_model: fetch the checkpoint from Hugging Face (idempotent)
- load_model / unload_model: GPU memory management

### midasheng_help

Multi-level help: topics overview | generate | prompt_format |
model_state | examples.

### Prefab cards

- show_scene_status_card: model + library status
- show_scene_card: one scene's metadata

## Structured caption format

The model consumes tagged views; absent views become <|unknown|>.

<|caption|> overall scene
<|asr|> transcript to be spoken
<|speech|> speaker characteristics (voice, emotion, style)
<|sfx|> sound effects
<|music|> music description
<|env|> environment / ambience

## Best practices

1. Check audio_scene(operation="status") before generating - the state
   machine tells you what is missing (not_installed / model_missing /
   ready) and never fakes success.
2. Keep the caption view concrete and the asr view clean prose for
   maximum speech intelligibility.
3. Use seed for reproducible scenes; raise eval_cfg toward 3.0 for more
   assertive adherence, lower toward 1.5 for softer interpretation.
4. List is paginated: pass offset from the previous response.
5. delete is destructive: confirm=True is required.

## Notes

- Generation blocks up to ~3 minutes on a 4090; the webapp uses the REST
  job API for async progress.
- Output: 16 kHz mono WAV, variable length via the learned stop head.
- 9 languages supported by the checkpoint; emotion control via the
  speech view.

