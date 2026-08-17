"""Shared helpers: dialogic returns and auto-logging error responses.

Fleet pattern (TOOL_DESIGN_STANDARDS.md section 7.1): the error helper logs
the active exception traceback once, so every tool boundary produces a
breadcrumb without per-tool logging code.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

logger = logging.getLogger("midasheng_gen_mcp")


def _error_response(
    error: str,
    error_type: str = "general",
    **kwargs: Any,
) -> dict[str, Any]:
    """Auto-logging error response - traceback logged before returning.

    Call from inside an except block: sys.exc_info() carries the active
    exception and logger.exception() captures the full stack.
    """
    exc = sys.exc_info()
    if exc and exc[0] is not None:
        logger.exception("Tool error: %s [%s]", error, error_type)
    else:
        logger.error("Tool error: %s [%s]", error, error_type)
    payload: dict[str, Any] = {
        "success": False,
        "error": error,
        "error_type": error_type,
        **kwargs,
    }
    return payload


def ok_response(message: str, **data: Any) -> dict[str, Any]:
    """Standard success dict with dialogic message."""
    return {"success": True, "message": message, **data}
