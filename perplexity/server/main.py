"""
Main entry point for Perplexity MCP server.
Imports all route modules to register them with the FastMCP app.
"""

import argparse
import base64
import json
import logging
import os
from pathlib import Path

# Initialize logging before importing other modules
from ..logger import setup_logger
setup_logger()

logger = logging.getLogger("server.main")


def _prepare_token_pool_config_env() -> None:
    """
    Normalize PPLX_TOKEN_POOL_CONFIG for environments like Hugging Face Spaces.

    Supported formats:
    1) File path to JSON config
    2) Raw JSON string (recommended for HF Secrets)
    3) Base64-encoded JSON string

    If raw/base64 JSON is provided, it will be written to /tmp and env var
    will be rewritten to the generated file path so existing ClientPool logic
    keeps working without persistence requirements.
    """
    env_value = os.getenv("PPLX_TOKEN_POOL_CONFIG")
    if not env_value:
        return

    raw = env_value.strip()
    if not raw:
        return

    # Case 1: already a valid file path
    if os.path.exists(raw):
        return

    candidates = [raw]

    # Case 2: optional base64 fallback
    if not raw.startswith("{"):
        try:
            padded = raw + "=" * (-len(raw) % 4)
            decoded = base64.b64decode(padded).decode("utf-8").strip()
            if decoded:
                candidates.append(decoded)
        except Exception:
            pass

    for candidate in candidates:
        try:
            config_obj = json.loads(candidate)
            if not isinstance(config_obj, dict):
                continue

            target = Path("/tmp/pplx_token_pool_config.json")
            target.write_text(
                json.dumps(config_obj, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            os.environ["PPLX_TOKEN_POOL_CONFIG"] = str(target)
            logger.info("PPLX_TOKEN_POOL_CONFIG loaded from inline secret into %s", target)
            return
        except Exception:
            continue

    logger.warning(
        "PPLX_TOKEN_POOL_CONFIG is neither an existing file path nor valid JSON/base64 JSON. "
        "Falling back to default initialization behavior."
    )


# Normalize env BEFORE importing app/client pool modules
_prepare_token_pool_config_env()

from .app import mcp, get_pool

# Import route modules to register tools and endpoints with the mcp instance
# Must import the actual decorated functions to trigger registration
from .mcp import list_models, search, research  # noqa: F401
from . import oai  # noqa: F401
from . import admin  # noqa: F401


def run_server(
    transport: str = "http",
    host: str = "0.0.0.0",
    port: int = 8000,
) -> None:
    """Start the MCP server with the requested transport."""
    # Initialize the pool on startup
    get_pool()

    if transport == "http":
        mcp.run(transport="http", host=host, port=port)
    else:
        mcp.run()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Perplexity MCP server (fastmcp).")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="http",
        help="Transport to use for MCP server.",
    )
    parser.add_argument("--host", default="0.0.0.0", help="HTTP host (when transport=http).")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "8000")),
        help="HTTP port (when transport=http)."
    )
    args = parser.parse_args()
    run_server(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
