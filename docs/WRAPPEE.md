# WRAPPEE - MiDashengLM-Gen

This repo wraps the **MiDashengLM-Gen** open-weights model (Xiaomi
Research), not a desktop application. The model generates coherent 16 kHz
mixed audio scenes from text: speech, music, sound effects, and
environmental acoustics in a single autoregressive pass.

## The model

- **Paper**: "MiDashengLM-Gen: Unified Audio Scene Generation via
  LLM-Driven Autoregressive Flow Matching" - [arXiv 2608.11804](https://arxiv.org/abs/2608.11804)
- **Architecture**: pre-trained LLM backbone (Qwen3-1.7B, fully
  fine-tuned) + per-token conditional flow matching (16-layer DiT, hidden
  2048). Generates 768-dim semantic-acoustic latents (25 Hz) - no
  quantization artifacts. Variable-length output via a learned stop head.
- **Size**: 2.9B params total (~6 GB fp16 VRAM; runs on RTX 4090 class).
- **Quality (per paper)**: Seed-TTS English WER 12.15% -> 2.79% vs 1.24%
  for dedicated TTS (approaching TTS-level speech intelligibility);
  competitive mixed-audio quality on MECAT; multilingual (9 languages)
  with emotion control.
- **Output**: 16 kHz mono WAV.

## Where to find things

| Link | URL |
|------|-----|
| GitHub (code, infer.py, license) | https://github.com/xiaomi-research/midashenglm-gen |
| Hugging Face (weights, transformers wrapper) | https://huggingface.co/mispeech/midashenglm-gen |
| Demo page (audio samples) | https://xingws.github.io/midashenglm-gen-demo/ |
| Paper | https://arxiv.org/abs/2608.11804 |
| HF Space (try it online) | https://hf.co/spaces/hugging-apps/midashenglm-gen |

## License and restrictions

Apache-2.0. The upstream README lists use restrictions: no unlawful,
fraudulent, or malicious purposes; no IP/privacy/publicity infringement;
no exploitation or harm of individuals or groups (including minors); no
military use. These restrictions apply to your use of the model outputs.

## Relationship to other Xiaomi audio models

"MiDasheng" is the family name of Xiaomi's audio tokenizer (Dasheng,
768-dim latents). MiDashengLM-Gen is the generation model built on top of
it - this repo wraps the generation model only. Do not confuse it with
MiDashengLLM (speech LLM) or standalone Dasheng tokenizer releases.
