"""Generate assets/prompts/examples.json (100 tool-call examples).

Deterministic generator: covers all ten audio_scene operations plus the
help and prefab tools with varied, realistic arguments.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "prompts" / "examples.json"

SCENES: list[dict[str, str]] = [
    {"caption": "A comedian delivering a punchline followed by uproarious crowd laughter and an upbeat jazz band hit", "asr": "And that is why I never buy cheap luggage anymore!", "speech": "expressive comedic male voice", "music": "sudden upbeat jazz band sting", "sfx": "uproarious crowd laughter", "env": "intimate comedy club"},
    {"caption": "Rain pattering on windows with soft background chatter and a gentle acoustic guitar", "music": "gentle acoustic guitar strumming", "sfx": "steady rain against glass", "env": "cozy cafe interior"},
    {"caption": "A rolling thunderstorm with distant rumbles and heavy rain", "sfx": "distant thunder rumbles and heavy rain", "env": "open field at night"},
    {"caption": "Smooth jazz quartet playing in a smoky lounge with gentle applause", "music": "smooth jazz quartet with saxophone, piano, and upright bass", "sfx": "polite applause after the piece", "env": "smoky lounge with low lights"},
    {"caption": "A calm news anchor reading headlines with subtle studio ambience", "asr": "Breaking news: local markets rallied for a third consecutive day today.", "speech": "calm professional female voice", "music": "subtle news bed music", "env": "quiet radio studio"},
    {"caption": "A peaceful forest at dawn with birdsong and a gentle breeze", "sfx": "birdsong and rustling leaves", "env": "dense forest at sunrise"},
    {"caption": "A door slams, footsteps cross a wooden hall, then a clock chimes midnight", "sfx": "a heavy door slam, steady footsteps on wood, a clock chime", "env": "an old empty house"},
    {"caption": "A short exchange at a market stall in the morning", "asr": "How much for the apples? Three euros a kilo. I will take two.", "speech": "cheerful market vendor voice, warm and quick", "sfx": "crates being stacked, morning bustle", "env": "open-air market, bright morning"},
    {"caption": "A soldier reads a letter home, starting steady and ending moved", "asr": "Dear Mom. The days are long but the nights are quiet. I met a dog yesterday. I miss you both.", "speech": "young male voice, steady at first, breaking slightly", "env": "quiet tent at night, distant rain"},
    {"caption": "A solo piano piece that builds from sparse to full, melancholic", "music": "solo piano, slow arpeggios growing louder and fuller", "env": "small recital hall"},
    {"caption": "Slow building ambient piece with a distant storm", "music": "sparse ambient pads", "env": "open plain under a gathering storm"},
    {"caption": "A goalkeeper celebrates after the final whistle", "asr": "YES! We did it!", "speech": "young excited male voice, triumphant and breathless", "sfx": "roaring stadium crowd", "env": "full stadium, loud"},
    {"caption": "A cheerful host greeting listeners over quiet music", "asr": "Welcome back to the show, everybody!", "speech": "warm energetic female voice", "env": "small studio"},
    {"caption": "A quick whoosh and a soft thump", "sfx": "a rising whoosh ending in a soft impact", "env": "neutral room"},
    {"caption": "Eine Nachrichtensprecherin liest die Schlagzeilen", "asr": "Die Börse schloss heute mit deutlichen Gewinnen.", "speech": "ruhige professionelle Frauenstimme", "env": "leises Radiostudio"},
    {"caption": "Kitchen breakfast preparation sounds", "sfx": "sizzling pan, eggs cracking, kettle boiling", "env": "small kitchen"},
    {"caption": "A quiet library in the evening", "sfx": "page turns and a distant clock", "env": "quiet library, wooden shelves"},
    {"caption": "Night city street with distant traffic and footsteps", "sfx": "footsteps on wet asphalt, distant cars", "env": "city street at night, light drizzle"},
    {"caption": "A spaceship cockpit with beeping instruments and low hum", "sfx": "periodic console beeps, soft machinery hum", "env": "small cockpit, metal walls"},
    {"caption": "A beach at midday with waves and seagulls", "sfx": "rolling waves, seagull calls", "env": "wide sandy beach, bright sun"},
]

TUNES = [
    {"eval_cfg": 1.5},
    {"eval_cfg": 2.0},
    {"eval_cfg": 2.5},
    {"eval_cfg": 3.0},
    {"stop_threshold": 0.3, "min_stop_step": 10},
    {"stop_threshold": 0.5},
    {"stop_threshold": 0.7},
    {"seed": 7},
    {"seed": 42},
    {"seed": 99, "eval_cfg": 1.8},
]

examples: list[dict[str, object]] = []


def add(name: str, desc: str, prompt: str, tool: str, arguments: dict[str, object]) -> None:
    examples.append({"name": name, "description": desc, "prompt": prompt, "tool": tool, "arguments": arguments})


# generate: scene x parameter sweep, first 40
for i, scene in enumerate(SCENES[:4]):
    for j, tune in enumerate(TUNES):
        args = {"operation": "generate", **{k: v for k, v in scene.items()}, **tune}
        add(
            f"generate-scene-{i}-tune-{j}",
            f"Generate '{scene['caption'][:40]}...' with tuning {list(tune.keys())}",
            f"Generate a scene: {scene['caption']}",
            "audio_scene",
            args,
        )

# generate: more scenes with varied views (next 15)
for i, scene in enumerate(SCENES[4:14]):
    args = {"operation": "generate", **scene}
    add(
        f"generate-{scene['caption'][:30].lower().replace(' ', '-')}-{i}",
        f"Generate: {scene['caption'][:60]}",
        f"Make an audio scene: {scene['caption']}",
        "audio_scene",
        args,
    )

# generate: seed reproducibility pairs (next 8)
for _i, scene in enumerate(SCENES[14:18]):
    for seed in (1, 2):
        add(
            f"generate-repro-{i}-seed-{seed}",
            f"Reproducible generation (seed {seed}) of {scene['caption'][:40]}",
            f"Generate with a fixed seed {seed}: {scene['caption']}",
            "audio_scene",
            {"operation": "generate", **scene, "seed": seed},
        )

# generate: caption-only ambience (next 5)
for _i, scene in enumerate(SCENES[18:20]):
    add(
        f"generate-ambience-{i}",
        f"Ambience-only generation: {scene['caption'][:40]}",
        f"Generate ambience only: {scene['caption']}",
        "audio_scene",
        {"operation": "generate", "caption": scene["caption"], "sfx": scene.get("sfx", ""), "env": scene.get("env", "")},
    )

# generate: multilingual (next 3)
add("generate-german-news", "German news read", "Generate a German news read", "audio_scene",
    {"operation": "generate", "caption": "Eine Nachrichtensprecherin liest die Schlagzeilen", "asr": "Die Börse schloss heute mit deutlichen Gewinnen.", "speech": "ruhige professionelle Frauenstimme", "env": "leises Radiostudio", "seed": 3})
add("generate-french-cafe", "French cafe ambience", "Generate a French cafe scene", "audio_scene",
    {"operation": "generate", "caption": "Un café parisien animé le matin", "sfx": "tasses qui cliquent, murmures", "env": "café parisien, matin ensoleillé", "seed": 4})
add("generate-spanish-market", "Spanish market ambience", "Generate a Spanish market scene", "audio_scene",
    {"operation": "generate", "caption": "Un mercado español lleno de vida", "sfx": "vendedores llamando, fruta cayendo", "env": "mercado al aire libre", "seed": 5})

# status (6)
for _i, note in enumerate(["check", "before-generating", "diagnose", "hardware", "after-error", "session-start"]):
    add(f"status-{note}", f"Check model status ({note})", f"Check the model status ({note})", "audio_scene", {"operation": "status"})

# samples (3)
for _i, note in enumerate(["show", "pick-a-start", "gallery"]):
    add(f"samples-{note}", f"Show built-in example captions ({note})", f"Show example captions ({note})", "audio_scene", {"operation": "samples"})

# list / get (10)
for page, (limit, offset) in enumerate([(10, 0), (20, 0), (10, 10), (5, 0), (50, 0), (10, 20), (100, 0), (20, 40), (10, 30), (25, 50)]):
    add(f"list-page-{page}", f"Browse scenes page {page} (limit {limit}, offset {offset})", f"List my scenes, page {page}", "audio_scene", {"operation": "list", "limit": limit, "offset": offset})
add("get-latest", "Inspect the newest scene", "Show me the newest scene's details", "audio_scene", {"operation": "get", "scene_id": "scene_latest"})
add("get-specific", "Inspect one scene by id", "Show scene scene_abc123", "audio_scene", {"operation": "get", "scene_id": "scene_abc123"})

# delete (4)
add("delete-confirm", "Delete a scene with confirmation", "Delete scene scene_abc123 (I confirm)", "audio_scene", {"operation": "delete", "scene_id": "scene_abc123", "confirm": True})
add("delete-no-confirm", "Delete attempt without confirmation (should refuse)", "Delete scene scene_abc123", "audio_scene", {"operation": "delete", "scene_id": "scene_abc123"})
add("delete-missing", "Delete a nonexistent scene", "Delete scene scene_does_not_exist (I confirm)", "audio_scene", {"operation": "delete", "scene_id": "scene_does_not_exist", "confirm": True})
add("delete-cleanup", "Delete an unwanted scene after export", "Remove the exported scene scene_xyz (I confirm)", "audio_scene", {"operation": "delete", "scene_id": "scene_xyz", "confirm": True})

# export (5)
add("export-file", "Export a scene to a named WAV file", "Export scene scene_abc123 to D:/audio/intro.wav", "audio_scene", {"operation": "export", "scene_id": "scene_abc123", "destination": "D:/audio/intro.wav"})
add("export-dir", "Export a scene into a directory", "Export scene scene_abc123 into D:/podcast/", "audio_scene", {"operation": "export", "scene_id": "scene_abc123", "destination": "D:/podcast/"})
add("export-bed", "Export a music bed for editing", "Export the piano scene to my video project", "audio_scene", {"operation": "export", "scene_id": "scene_piano", "destination": "D:/video-edits/bed-track.wav"})
add("export-voice", "Export the voice hook", "Export the welcome hook to the podcast folder", "audio_scene", {"operation": "export", "scene_id": "scene_voice", "destination": "D:/podcast/into-voice.wav"})
add("export-missing", "Export attempt for unknown scene", "Export scene nope to D:/audio/out.wav", "audio_scene", {"operation": "export", "scene_id": "nope", "destination": "D:/audio/out.wav"})

# model lifecycle (6)
add("download-model", "Download the checkpoint from Hugging Face", "Download the model checkpoint", "audio_scene", {"operation": "download_model"})
add("load-model", "Load the model onto the GPU", "Load the model into GPU memory", "audio_scene", {"operation": "load_model"})
add("unload-model", "Free GPU memory", "Unload the model to free VRAM", "audio_scene", {"operation": "unload_model"})
add("download-then-load", "Download then load", "Get the model ready to generate", "audio_scene", {"operation": "download_model"})
add("preload-for-session", "Preload for a long session", "Load the model before my session", "audio_scene", {"operation": "load_model"})
add("unload-before-other-work", "Unload before other GPU work", "Free VRAM for Ollama", "audio_scene", {"operation": "unload_model"})

# help (5)
add("help-index", "Help index", "Show the help index", "midasheng_help", {"topic": None})
add("help-generate", "Help on generate", "How do I generate a scene?", "midasheng_help", {"topic": "generate"})
add("help-prompt-format", "Help on the caption format", "Explain the caption views", "midasheng_help", {"topic": "prompt_format"})
add("help-model-state", "Help on model states", "What does model_missing mean?", "midasheng_help", {"topic": "model_state"})
add("help-examples", "Help on examples", "Show me usage examples", "midasheng_help", {"topic": "examples"})

# prefab cards (4)
add("status-card", "Model status as a card", "Show the status card", "show_scene_status_card", {})
add("scene-card", "One scene as a card", "Show scene scene_abc123 as a card", "show_scene_card", {"scene_id": "scene_abc123"})
add("scene-card-missing", "Missing scene card (error state)", "Show a card for an unknown scene", "show_scene_card", {"scene_id": "scene_unknown"})
add("scene-card-duration", "Scene card with duration", "Card for the thunderstorm scene", "show_scene_card", {"scene_id": "scene_thunder"})

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(examples, indent=2), encoding="utf-8")
print(f"Wrote {len(examples)} examples to {OUT}")


