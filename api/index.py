import os

from starlette.requests import Request
from starlette.responses import JSONResponse

# --- Optional: materialize token pool config from env into a writable path (Vercel supports /tmp) ---
# If you set TOKEN_POOL_JSON, we will write it to /tmp/token_pool_config.json and point
# PPLX_TOKEN_POOL_CONFIG to it.
_token_pool_json = os.getenv("TOKEN_POOL_JSON")
if _token_pool_json:
    _path = "/tmp/token_pool_config.json"
    try:
        with open(_path, "w", encoding="utf-8") as f:
            f.write(_token_pool_json)
        os.environ["PPLX_TOKEN_POOL_CONFIG"] = _path
    except Exception:
        # If writing fails, we just fall back to env-based single-token mode
        pass

# Import mcp + pool singleton
from perplexity.server.app import mcp, get_pool  # noqa: E402

# Register MCP tools and OpenAI-compatible routes
from perplexity.server import mcp as _mcp_tools  # noqa: F401,E402
from perplexity.server import oai as _oai_routes  # noqa: F401,E402

# -------------------- Minimal unauthenticated health check --------------------

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    # Keep health checks minimal and non-sensitive for public probing.
    return JSONResponse({"status": "ok"})


# Initialize pool once per cold-start
get_pool()

# Export an ASGI app for Vercel Python runtime
# MCP endpoint should be /mcp (README/client expectations)
app = mcp.http_app(path="/mcp")
