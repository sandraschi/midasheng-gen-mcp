"""Built-in example scene captions (shared by MCP tool + REST + webapp)."""

from __future__ import annotations

SAMPLES: list[dict[str, str]] = [
    {
        "id": "comedy-club",
        "caption": "A comedian delivering a punchline followed by uproarious crowd laughter and an upbeat jazz band hit",
        "asr": "And that is why I never buy cheap luggage anymore!",
        "speech": "expressive comedic male voice",
        "sfx": "uproarious crowd laughter",
        "music": "sudden upbeat jazz band sting",
        "env": "intimate comedy club",
    },
    {
        "id": "rainy-cafe",
        "caption": "Rain pattering on windows with soft background chatter and a gentle acoustic guitar",
        "sfx": "steady rain against glass",
        "music": "gentle acoustic guitar strumming",
        "env": "cozy cafe interior",
    },
    {
        "id": "thunderstorm",
        "caption": "A rolling thunderstorm with distant rumbles and heavy rain",
        "sfx": "distant thunder rumbles and heavy rain",
        "env": "open field at night",
    },
    {
        "id": "jazz-lounge",
        "caption": "Smooth jazz quartet playing in a smoky lounge with gentle applause",
        "sfx": "polite applause after the piece",
        "music": "smooth jazz quartet with saxophone, piano, and upright bass",
        "env": "smoky lounge with low lights",
    },
    {
        "id": "news-report",
        "caption": "A calm news anchor reading headlines with subtle studio ambience",
        "asr": "Breaking news: local markets rallied for a third consecutive day today.",
        "speech": "calm professional female voice",
        "music": "subtle news bed music",
        "env": "quiet radio studio",
    },
    {
        "id": "forest-dawn",
        "caption": "A peaceful forest at dawn with birdsong and a gentle breeze",
        "sfx": "birdsong and rustling leaves",
        "env": "dense forest at sunrise",
    },
]
