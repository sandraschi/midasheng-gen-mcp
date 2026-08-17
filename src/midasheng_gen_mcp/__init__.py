"""MiDashengLM-Gen MCP - unified audio scene generation.

Wraps the MiDashengLM-Gen model (LLM-driven autoregressive flow matching,
Xiaomi Research) as a FastMCP 3.4 server with a FastAPI REST surface and a
SOTA webapp. Generates coherent 16 kHz mixed audio scenes (speech, music,
sound effects, environment) from structured text captions.
"""

__version__ = "0.1.0"
