"""Prompt composition and job submission helpers."""

from __future__ import annotations

import pytest

from midasheng_gen_mcp.jobs import build_prompt


def test_build_prompt_full() -> None:
    prompt = build_prompt(
        {
            "caption": "rain and thunder",
            "asr": "hello world",
            "speech": "calm female voice",
            "sfx": "thunder",
            "music": "",
            "env": "forest",
        }
    )
    assert "<|caption|> rain and thunder" in prompt
    assert "<|asr|> hello world" in prompt
    assert "<|speech|> calm female voice" in prompt
    assert "<|sfx|> thunder" in prompt
    assert "<|music|> <|unknown|>" in prompt
    assert "<|env|> forest" in prompt
    assert prompt.endswith(" ")


def test_build_prompt_requires_caption() -> None:
    with pytest.raises(ValueError):
        build_prompt({"asr": "no caption here"})


def test_build_prompt_empty_views_unknown() -> None:
    prompt = build_prompt({"caption": "c"})
    assert prompt.count("<|unknown|>") == 5
