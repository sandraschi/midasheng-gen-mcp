"""Entry point - dual transport (stdio default, HTTP when MCP_PORT set).

Follows the fleet run_server pattern: stdio for Claude Desktop, uvicorn
HTTP for the webapp and streamable MCP clients. Use uvicorn.Server (not
run_http_async) so CORS middleware survives.
"""

from __future__ import annotations

import argparse
import os
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="MiDashengLM-Gen MCP server")
    parser.add_argument("--mode", choices=["stdio", "http"], default=None)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=None)
    args, _ = parser.parse_known_args()

    from .config import settings
    from .logs import setup_logging

    setup_logging()

    port_env = os.environ.get("MCP_PORT") or os.environ.get("PORT")
    mode = args.mode or ("http" if port_env else "stdio")
    port = args.port or (int(port_env) if port_env else settings.backend_port)

    if mode == "http":
        import uvicorn  # noqa: PLC0415

        from .server import build_web_app  # noqa: PLC0415

        app = build_web_app()
        uvicorn.run(app, host=args.host, port=port, log_level="info")
        return

    import asyncio  # noqa: PLC0415

    from .server import create_mcp  # noqa: PLC0415

    asyncio.run(create_mcp().run_stdio_async(show_banner=False))


if __name__ == "__main__":
    sys.exit(main())
