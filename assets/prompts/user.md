# MiDashengLM-Gen MCP - User Guide and Tutorials

Welcome to MiDashengLM-Gen MCP. This guide teaches you, in plain
language, how to generate mixed audio scenes - speech, music, sound
effects, and ambient sound in one 16 kHz mix - using text. You do not
need a background in audio engineering or machine learning to follow
along. Every chapter builds on the previous one, and each ends with
something you can try immediately.

## Chapter 1 - What you just installed

You have connected to a server that runs a 2.9-billion-parameter neural
model on your own computer. The model, MiDashengLM-Gen from Xiaomi
Research, reads a short structured description of a scene and writes a
WAV file that sounds like that scene: a comedian's punchline over crowd
laughter and a jazz sting, rain on a window with guitar in the
background, a news anchor reading headlines in a quiet studio. It is
open source (Apache-2.0), it works offline after a one-time download,
and it does not send your prompts anywhere.

The server offers four tools. audio_scene is the workhorse: one tool,
ten operations, covering everything from checking the model to
generating scenes to managing your library. midasheng_help is the manual
you are reading now, in compact form. show_scene_status_card and
show_scene_card render pretty summaries of the model and your scenes in
the chat interface.

## Chapter 2 - The three-step start

Before you can generate anything, the server needs the model available.
There are exactly three conditions, and the server tells you which one
you are in.

1. The inference stack must be installed. If `status` reports
   not_installed, run `uv sync --extra model` in the repository (or
   re-run start.ps1, which does it for you). This installs torch,
   transformers, and the audio libraries - about 3 GB, one time.
2. The checkpoint must be downloaded. If `status` reports model_missing,
   run audio_scene(operation="download_model"). This fetches the
   weights from Hugging Face - about 6 GB, one time. It is safe to run
   again; it simply skips what you already have.
3. The model must be loaded into the GPU. If `status` reports unloaded,
   you are already fine: the first generate will load it automatically.
   You can pre-load with audio_scene(operation="load_model") to surface
   any GPU problem early.

Check where you are at any time with:

audio_scene(operation="status")

The response tells you the state, the device (cuda or cpu), your GPU
name if one is present, and the library versions. Read the state field.
That is your compass for the whole session.

## Chapter 3 - Your first scene

Let us generate something immediately. Use the built-in example that is
the most fun to hear - the comedy club:

audio_scene(operation="generate",
    caption="A comedian delivering a punchline followed by uproarious
crowd laughter and an upbeat jazz band hit",
    asr="And that is why I never buy cheap luggage anymore!",
    speech="expressive comedic male voice",
    music="sudden upbeat jazz band sting",
    sfx="uproarious crowd laughter",
    env="intimate comedy club",
    seed=42)

Generation is synchronous: the tool waits until the audio is rendered,
which on a modern GPU takes under a minute for a scene this size. The
response contains a scene id, the duration in seconds, and an audio URL.
Listen to it. What you hear is the model planning the scene token by
token and then painting audio with flow matching - a single pass, not a
pipeline that glues speech onto a separate sound-effects track. That is
why the laughter and the spoken line interact the way they do: the model
heard them together and made them coexist.

Try the other samples too:

audio_scene(operation="samples")

This lists six ready-made captions: the comedy club, a rainy cafe, a
thunderstorm, a jazz lounge, a news report, and a forest dawn. Take any
of them, change one view, and generate. You have now seen the entire
happy path.

## Chapter 4 - Understanding the caption views

Every scene is described by six views, like labeled fields on a form.
The server combines them into the exact prompt the model was trained on.

- caption: the overall scene. What happens, what it sounds like. This
  is the only required field.
- asr: the spoken transcript. Exactly what should be said.
- speech: how the voice sounds - timbre, emotion, delivery.
- sfx: the sound effects.
- music: the music.
- env: the environment - place and acoustic character.

Views you leave empty are replaced by the special token <|unknown|>,
which tells the model "do not spend effort here". A caption-only prompt
is perfectly valid and often produces lovely ambience.

The art is in the specificity. Compare these two captions:

- "A forest with birds"
- "A dense forest at first light: wood pigeons calling, a distant
  stream, and the soft rustle of a breeze through birch leaves"

The second gives the model distinct acoustic anchors and a time of day,
which shapes the energy of the whole scene. You do not need to write
poetry; you need to name sounds the way a foley artist would: verbs and
materials, distances, and levels.

For the asr view, write the way people speak, not the way people write.
Short sentences. Real punctuation. "And that is why I never buy cheap
luggage anymore!" lands differently from "I refuse to purchase low
quality suitcases." The model pronounces text; it thrives on natural
prosody. For the speech view, stack descriptors: voice quality, emotion,
delivery. "calm professional female voice" and "deep narrator voice,
slow and grave" are both excellent; "female voice" alone leaves the
emotion to chance.

## Chapter 5 - Four recipes you will use constantly

### Recipe A - Ambient background

Fill caption, env, and sfx only. Leave speech and asr empty. Example:

audio_scene(operation="generate",
    caption="A rainy cafe in the late afternoon",
    sfx="steady rain against the window, muffled city traffic",
    music="a quiet acoustic guitar in the corner",
    env="warm cafe interior, wooden tables")

### Recipe B - A voiceover over ambience

Fill asr, speech, caption, and env; keep music subtle so the voice
carries. Example:

audio_scene(operation="generate",
    caption="A calm narration over a quiet newsroom",
    asr="Local markets rallied for a third consecutive day as
investors shrugged off the morning sell-off.",
    speech="calm professional female voice, steady pace",
    music="subtle news bed music",
    env="quiet radio studio")

This recipe is where MiDashengLM-Gen shines: the paper reports word
error rates near dedicated text-to-speech systems, so the narration is
actually understandable, not buried under the music.

### Recipe C - One-shot sound design

Ask for a complete mini-soundscape with events in it. Use the caption to
sequence events and the sfx view to name them:

audio_scene(operation="generate",
    caption="A door slams, footsteps cross a wooden hall, then a clock
chimes midnight",
    sfx="a heavy door slam, steady footsteps on wood, a clock chime",
    env="an old empty house")

### Recipe D - Deterministic iteration

Fix the seed and change exactly one view between attempts:

audio_scene(operation="generate", caption="Jazz quartet in a lounge",
    music="smooth jazz quartet with saxophone lead", seed=7)
audio_scene(operation="generate", caption="Jazz quartet in a lounge",
    music="smooth jazz quartet with piano lead", seed=7)

The seed pins the random base, so the difference between the two
renders is attributable to the music view. Use this when you are
fine-tuning one scene rather than exploring wildly.

## Chapter 6 - Making the output behave

Three parameters control the render. They are all optional; the
defaults are sane.

eval_cfg is the guidance strength. At the default of 2.0 the model
follows the prompt faithfully. Raise toward 3.0 when the output drifts
from your caption; lower toward 1.5 when you want the model to take
liberties and produce something more inventive. Very high values can
make the audio feel over-processed.

stop_threshold controls how long the scene is. The model has a learned
"stop head" that decides when the scene is finished. The threshold is
the probability at which it stops. If your scenes keep ending too early,
lower the threshold to 0.3 or 0.35 and raise min_stop_step to 8 or 10.
If scenes drag on with dead air, raise the threshold toward 0.7.

seed makes generation reproducible. The same caption plus the same seed
gives the same scene. Leave it empty for a fresh surprise every time.

Example with all three tuned:

audio_scene(operation="generate",
    caption="Slow building ambient piece with a distant storm",
    env="open plain under a gathering storm",
    music="sparse ambient pads",
    eval_cfg=1.8,
    stop_threshold=0.35,
    min_stop_step=10,
    seed=99)

## Chapter 7 - Your library

Every generated scene is stored as a 16 kHz mono WAV file and indexed in
a small database. You will quickly collect more scenes than you can
keep straight, so learn the library operations.

List your scenes, newest first:

audio_scene(operation="list", limit=10)

The response includes total, has_more, and the page of scenes. Page
through large libraries by passing offset:

audio_scene(operation="list", limit=10, offset=10)

Inspect one scene in full - the exact views that produced it, its
duration, its parameters:

audio_scene(operation="get", scene_id="scene_abc123")

Take a scene out of the library to a path you control:

audio_scene(operation="export", scene_id="scene_abc123",
    destination="D:/audio/my-podcast-intro.wav")

Delete a scene you do not want (this removes the WAV permanently, so
the tool demands an explicit confirmation):

audio_scene(operation="delete", scene_id="scene_abc123", confirm=True)

The web dashboard has the same capabilities with a play button for
every scene - a nice way to audition a batch.

## Chapter 8 - Model management

The model is a guest in your GPU memory, not a permanent resident.
Understanding its lifecycle prevents half of all problems you will
encounter.

unloaded means the weights are on disk but not loaded. Generation loads
them on demand. If you have a long session of many generations, load
once at the start:

audio_scene(operation="load_model")

If your GPU is busy with other work (say Ollama is serving a chat model
at the same time), free the memory when you are done:

audio_scene(operation="unload_model")

If you moved machines or the cache was cleared, re-download:

audio_scene(operation="download_model")

The status operation always tells you which state you are in, and it
reports the GPU name and device so you can confirm the model is actually
running on your GPU and not secretly falling back to a slow CPU path.

## Chapter 9 - Multilingual and emotional scenes

The checkpoint speaks nine languages. Write the asr view in the target
language. Optionally name the language in the caption for consistency:

audio_scene(operation="generate",
    caption="Eine Nachrichtensprecherin liest die Schlagzeilen",
    asr="Die Börse schloss heute mit deutlichen Gewinnen.",
    speech="ruhige professionelle Frauenstimme",
    env="leises Radiostudio")

Emotion lives in the speech view. Name it explicitly:

audio_scene(operation="generate",
    caption="A goalkeeper celebrates after the final whistle",
    asr="YES! We did it!",
    speech="young excited male voice, triumphant and breathless",
    sfx="roaring stadium crowd",
    env="full stadium, loud")

You can also sketch an emotional arc in the caption ("starts calm, ends
triumphant") and let the model pace it across the spoken line.

## Chapter 10 - Common problems and their fixes

The model reports not_installed. The inference libraries are missing.
Run `uv sync --extra model` in the repository, or re-run start.ps1.
Then check status again.

The model reports model_missing. The checkpoint is not on disk. Run
audio_scene(operation="download_model"). If the download stalls, check
your network and disk space (about 10 GB free is comfortable), then try
again - the download resumes.

The model reports error. Something failed while loading, usually the
GPU. Read error_message in the status response. If it mentions memory,
unload other models (unload_model, or Ollama's own tools) and retry. If
the error persists, restart the server and try load_model once more.

Generation is slow. Check the device field in status. If it says cpu,
the model is running on your processor, which is 10 to 50 times slower
than a GPU. Install a CUDA driver and set MIDASHENG_DEVICE=cuda, or
accept the wait.

Scenes end too early or too late. Tune stop_threshold and min_stop_step
as described in Chapter 6.

The scene ignores part of your caption. The caption view is the
strongest signal; the model weights it highest. If music is missing,
name it in the caption too, not only in the music view. Consider
raising eval_cfg toward 3.0.

The chat page in the web dashboard says no local LLM. The chat page
uses your own Ollama installation, not the scene model. Start Ollama,
or set MIDASHENG_OLLAMA_URL if it runs elsewhere.

## Chapter 11 - Using the web dashboard

Alongside the chat tools, the repository ships a browser dashboard. It
runs on port 11160 with the backend on 11159; start.bat or
just serve brings both up and opens the browser.

The Generate page is the same caption form as the tools, plus sliders
for eval_cfg and stop_threshold and a seed field, with the six built-in
samples one click away. Generation runs as a background job: you see
progress in the Inbox page, and the finished scene appears with a play
button. The Scenes page is your library with audio players and delete
buttons. The Skills page renders the server's SKILL.md. The Chat page
talks to your local Ollama with an audio-engineer persona. Settings
shows model state with download/load/unload buttons and probes your
local LLM providers. The API Docs page embeds the Swagger UI for the
backend. Logs streams the server log ring buffer.

## Chapter 12 - The whole journey in ten minutes

1. audio_scene(operation="status") - confirm you are unloaded or ready.
2. If model_missing: audio_scene(operation="download_model").
3. audio_scene(operation="samples") - pick a starting point.
4. Generate the comedy club with seed 42.
5. Generate the same scene again with a different seed and compare.
6. Build your own scene: two sentences of caption, one sfx line, one
   env line. Generate it.
7. If it is too short: stop_threshold=0.35, min_stop_step=10, retry.
8. Fix a seed and swap one view to hear its effect.
9. Export your favorite to a real file path.
10. Delete the failures. You now know the whole surface.

## Chapter 13 - Sound design principles

A few principles from audio production will improve every scene you
generate.

Layers and balance. A scene is a foreground, a middle, and a bed. In
the comedy club, the spoken line is the foreground, the laughter is the
middle, and the club ambience is the bed. Describe them in that order
of importance in your caption, and keep the bed modest - a single
adjective ("intimate", "spacious", "distant") is usually enough, while
the foreground deserves the detail.

Transients give life. Sounds that begin sharply - a door slam, a
thunderclap, a glass clink - anchor the listener's attention. If a
scene feels flat, add one transient to the sfx view. If a scene feels
chaotic, remove the transients and keep only steady-state sounds.

Contrast makes memory. A scene that is all rain is pleasant; a scene
that is rain, then a lull, then a thunderclap is memorable. You can
sequence events in the caption ("a lull, then a distant rumble") and
the model will usually respect the order.

Space is a sound. The env view is not decoration: it sets reverb and
distance. "Large empty hall with echo" and "closet-sized booth" produce
wildly different mixes from the same sfx line. When a scene sounds
wrong, suspect the env view before the effects.

Direction and motion. The model can express movement ("footsteps
approaching", "a car passing and fading"). Put the motion in the sfx
view and the space in the env view and the model will combine them
naturally.

## Chapter 14 - Characters and dialogue

Because the asr view is rendered with TTS-grade intelligibility, you
can build small radio plays. Two characters in one scene is possible;
describe the exchange in the asr view and give the speech view a single
dominant character, letting the caption set the dynamic:

audio_scene(operation="generate",
    caption="A short exchange at a market stall in the morning",
    asr="How much for the apples? Three euros a kilo. I will take two.",
    speech="cheerful market vendor voice, warm and quick",
    sfx="crates being stacked, morning bustle",
    env="open-air market, bright morning")

For a monologue with emotional range, write the arc into the caption
and keep the asr prose plain - the emotion lives in the speech view and
the delivery:

audio_scene(operation="generate",
    caption="A soldier reads a letter home, starting steady and ending
moved",
    asr="Dear Mom. The days are long but the nights are quiet. I met a
dog yesterday. I miss you both.",
    speech="young male voice, steady at first, breaking slightly",
    env="quiet tent at night, distant rain")

Accents and character voices are best described in the speech view with
concrete reference points ("warm midwestern drawl", "crisp received
pronunciation") rather than abstract adjectives.

## Chapter 15 - Music-forward workflows

When music is the point of the scene, put the musical description in
both the caption and the music view - the caption carries the strongest
signal. Name instruments, tempo, and energy:

audio_scene(operation="generate",
    caption="A solo piano piece that builds from sparse to full,
melancholic",
    music="solo piano, slow arpeggios growing louder and fuller",
    env="small recital hall")

To use generated music as a placeholder bed in a video edit, generate
a music-forward scene and then export the WAV:

audio_scene(operation="export", scene_id="scene_xyz",
    destination="D:/video-edits/bed-track.wav")

Remember the output is mono 16 kHz - fine for voiceovers, ambience, and
bed tracks, not for final musical masters. Treat it as a scratch
instrument, then re-record or upscale if the project needs studio
quality.

## Chapter 16 - Performance and hardware

The model needs about 6 GB of VRAM in half precision. On an RTX 4090,
a five-second scene renders in tens of seconds. On a laptop GPU with
less memory you may need to close other graphics-hungry apps; on
integrated graphics you will fall back to CPU, which is 10 to 50 times
slower - a five-second scene can take minutes.

Two environment variables matter here. MIDASHENG_DEVICE forces the
device (auto, cuda, cpu). MIDASHENG_PRELOAD_MODEL=1 loads the model at
server startup instead of on first generate - useful if you want the
GPU work to happen once, before your interactive session starts, rather
than mid-conversation.

If you share the machine with Ollama or LM Studio, remember that every
loaded model occupies VRAM. Unload the scene model when you are done
generating and it is not needed:

audio_scene(operation="unload_model")

## Chapter 17 - Automation with the REST API

Everything the tools do is also available over HTTP for scripts and
the web dashboard. The job API is the right pattern for automation
because it does not block: submit, poll, collect.

1. Submit: POST /api/generate with the caption views and parameters as
   JSON. The response is a job id.
2. Poll: GET /api/jobs/{job_id} until status is done or failed. The job
   carries progress, a message, and on completion the scene id.
3. Collect: GET /api/audio/{scene_id} streams the WAV; DELETE
   /api/scenes/{scene_id} removes it.

Health and introspection: GET /api/health, GET /api/v1/diagnostics,
GET /api/tools, GET /api/capabilities. Library: GET /api/scenes with
limit and offset. Model control: POST /api/model/download, /load,
/unload. Logs: GET /api/logs. Local LLM for chat: GET /api/llm/discover
and POST /api/llm/chat.

A minimal Python automation sketch:

import httpx, time
r = httpx.post("http://127.0.0.1:11159/api/generate",
    json={"caption": "Rain on a tin roof at night", "seed": 3})
job_id = r.json()["job_id"]
while True:
    job = httpx.get(f"http://127.0.0.1:11159/api/jobs/{job_id}").json()["job"]
    if job["status"] in ("done", "failed"):
        break
    time.sleep(2)
print(job)

## Chapter 18 - Security, safety, and etiquette

The model is a speech-capable generator. That is powerful and it needs
guardrails. Do not use it to clone real people's voices without their
consent, to impersonate public figures, or to produce deceptive audio -
those uses are harmful, and in many jurisdictions unlawful. The
upstream license (Apache-2.0 with stated restrictions) forbids
unlawful, fraudulent, and military use, and exploitation or harm of
individuals or groups including minors. If a request falls into those
categories, decline and suggest a lawful alternative.

Everything else is fair game and, because generation is local, private:
your captions and scenes never leave your machine except for the
one-time checkpoint download.

## Chapter 19 - Ten-minute project: a podcast intro

Put the chapters together into one real project - a 10-second podcast
intro with a spoken hook, a music sting, and a whoosh.

1. Generate the music bed:
   audio_scene(operation="generate",
       caption="A short upbeat podcast intro sting",
       music="bright ukulele riff with a handclap beat",
       env="dry studio", seed=5)
2. Generate the voice hook:
   audio_scene(operation="generate",
       caption="A cheerful host greeting listeners over quiet music",
       asr="Welcome back to the show, everybody!",
       speech="warm energetic female voice",
       env="small studio")
3. Generate a whoosh/transition:
   audio_scene(operation="generate",
       caption="A quick whoosh and a soft thump",
       sfx="a rising whoosh ending in a soft impact",
       env="neutral room")
4. Export all three to a project folder:
   audio_scene(operation="export", scene_id="scene_a",
       destination="D:/podcast/into-music.wav")
   audio_scene(operation="export", scene_id="scene_b",
       destination="D:/podcast/into-voice.wav")
   audio_scene(operation="export", scene_id="scene_c",
       destination="D:/podcast/into-whoosh.wav")

You now have three raw elements. In any editor you can layer the voice
over the music, duck the music under the voice, and place the whoosh at
the cut. That is a complete podcast intro generated entirely from text
in a single session.

## Chapter 20 - A parameter tuning matrix

When a scene is close but not right, change one knob at a time. This
matrix maps symptoms to fixes.

Symptom: output ignores the prompt details. Fix: raise eval_cfg toward
3.0, and move the key detail into the caption view - it is the
strongest signal.

Symptom: output is too short. Fix: stop_threshold 0.3, min_stop_step
10, and add a second sentence to the caption so the model has more to
say.

Symptom: output drags with dead air at the end. Fix: stop_threshold
0.7.

Symptom: speech is muffled or buried. Fix: shorten the asr view to the
essential line, name the emotion in the speech view, drop music to a
single adjective, and move background content into env.

Symptom: everything sounds samey. Fix: vary the seed, change the env
view (space changes everything), and lower eval_cfg to 1.5-1.8 to let
the model improvise.

Symptom: sound effects are generic. Fix: use concrete verbs and
materials in the sfx view - "paper crumpling", not "noises".

Symptom: music is overpowering. Fix: qualify it in the music view with
level words ("quiet", "distant", "in the background") and mirror that
in the caption.

Symptom: scene feels dry or flat. Fix: add a transient event to sfx
and reverb hints to env ("echo", "large room", "outdoor").

Keep a seed notebook: for any scene you plan to iterate on, record the
seed from the first run. Then every change is a controlled experiment.

## Chapter 21 - When to use the web dashboard vs the tools

The chat tools are for in-conversation generation and for agents: you
can generate, inspect, export, and manage the model without leaving the
conversation, and the structured responses are machine-readable. The
web dashboard is for browsing and auditioning: it has play buttons,
pagination, a job history with progress bars, sliders instead of
parameters, and the Swagger API explorer. Use the tools for work that
needs to be reproducible and scripted; use the dashboard for
exploration and for checking a batch of scenes by ear. Both write to
the same library, so a scene generated in chat appears in the dashboard
and vice versa.

## Chapter 22 - Practice prompts to grow your skills

Try these in order. Each one exercises a different part of the model.

1. Ambience focus: "A quiet library in the evening, page turns and a
   distant clock" with only caption and env.
2. Speech focus: a news bulletin asr of three sentences, speech
   "neutral broadcaster voice", env "dead studio".
3. SFX focus: "A kitchen preparing breakfast: sizzling pan, eggs
   cracking, kettle boiling" with sfx and env, no speech.
4. Music focus: a jazz quartet with saxophone lead, env "small smoky
   club", seed 11, then the same with piano lead, seed 11 - compare.
5. Emotion: the same asr line with three different speech views
   (triumphant, worried, exhausted) and three different seeds, and
   listen to how delivery changes meaning.
6. Reproducibility: the same full scene twice with the same seed - the
   outputs should match closely.
7. Space: the same sfx line with env "large empty hall" and then
   "closet-sized booth" - hear the reverb change.
8. Sequence: a caption describing a three-beat scene - quiet, alarm,
   chaos - and hear the model pace it.

By the end of the list you will have internalized which views do what,
which knob fixes which symptom, and how to iterate deterministically.
That is the whole skill of working with MiDashengLM-Gen: treat the
model as a very fast foley artist with strong opinions, learn its
language, and steer with the views and the seed.

## Glossary

- caption views: the six labeled text fields (caption, asr, speech,
  sfx, music, env) that describe a scene.
- checkpoint: the trained model weights on disk, about 6 GB.
- eval_cfg: classifier-free guidance strength.
- flow matching: the generative technique that paints audio tokens -
  here driven autoregressively by an LLM.
- inference stack: the Python libraries (torch, transformers, ...) that
  execute the model.
- seed: the random base that makes generation reproducible.
- stop head: a learned predictor that decides when a scene is finished.
- stop_threshold: the probability at which the stop head fires.
- WAV: the audio file format the model writes (16 kHz mono).

## Where to go next

You have the complete tool surface: ten operations on one portmanteau,
a help index, and two card renderers. For the underlying science, read
the paper at arxiv.org/abs/2608.11804. For the model files, see
huggingface.co/mispeech/midashenglm-gen. For the demo audio, see
xingws.github.io/midashenglm-gen-demo. For the full server manual,
call midasheng_help with no topic. Happy scene crafting.
