# Tool Reference

## audio_scene (portmanteau)

One tool, ten operations. The operation enum is the catalog.

| Operation | Description | Key params |
|-----------|-------------|------------|
| `status` | Model state, device, CUDA, versions | - |
| `generate` | Generate one scene (synchronous) | caption (required), asr, speech, sfx, music, env, eval_cfg, stop_threshold, min_stop_step, seed |
| `list` | Paginated library browse | limit (1-100, default 20), offset |
| `get` | One scene's metadata | scene_id |
| `delete` | Remove scene + WAV (destructive) | scene_id, confirm=True |
| `export` | Copy WAV to a destination | scene_id, destination |
| `samples` | Built-in example captions | - |
| `download_model` | Fetch checkpoint (idempotent) | - |
| `load_model` | Load onto GPU | - |
| `unload_model` | Free GPU memory | - |

### generate parameters

- `caption` (required): overall scene description.
- `asr`: speech transcript to synthesize (best kept as clean prose).
- `speech`: speaker characteristics - voice, emotion, style.
- `sfx`: sound effects description.
- `music`: music description.
- `env`: environment / ambience.
- `eval_cfg`: classifier-free guidance, default 2.0 (raise toward 3.0 for
  stronger adherence, 1.5 for softer interpretation).
- `stop_threshold`: stop-head threshold for variable-length truncation,
  default 0.5.
- `min_stop_step`: minimum autoregressive steps, default 5.
- `seed`: reproducibility (same seed + caption = same scene).

### Return format (generate)

```json
{
  "success": true,
  "message": "Scene scene_123 generated (4.2s)",
  "scene": {
    "id": "scene_123",
    "duration_seconds": 4.2,
    "sample_rate": 16000,
    "caption": { "caption": "...", "sfx": "...", "env": "..." },
    "audio_url": "/api/audio/scene_123"
  }
}
```

### Model state machine

`not_installed` -> `model_missing` -> `unloaded` -> `loading` -> `ready`
(-> `error` recoverable). Missing stack/checkpoint returns `success:
false` with `suggestions` and `recovery_options` - never a fake success.

## midasheng_help

Multi-level help. Topics: `overview`, `generate`, `prompt_format`,
`model_state`, `examples`. Call with no topic for the index.

## show_scene_status_card (Prefab app)

Model + library status rendered as a rich in-chat card. Falls back to a
plain-text summary on hosts without Prefab rendering.

## show_scene_card (Prefab app)

One scene's metadata (duration, views, created) as a card. 404 renders an
error card with `is_error=True`.

## REST endpoints (webapp surface)

`GET /api/health`, `GET /api/v1/diagnostics`, `GET /api/dashboard`,
`GET /api/capabilities`, `GET /api/tools`, `GET /api/skills`,
`GET /api/skills/{name}`, `GET /api/samples`, `GET /api/scenes?limit&offset`,
`GET/DELETE /api/scenes/{id}`, `POST /api/generate`, `GET /api/jobs`,
`GET /api/jobs/{id}`, `GET /api/audio/{id}`, `POST /api/model/download`,
`POST /api/model/load`, `POST /api/model/unload`, `GET /api/logs`,
`GET /api/llm/discover`, `POST /api/llm/chat`, `POST /mcp` (streamable MCP).
