import os

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

# Important: importing these modules registers MCP tools and custom HTTP routes
from perplexity.server.app import mcp, get_pool  # noqa: E402
from perplexity.server import mcp as _mcp_tools  # noqa: F401,E402
from perplexity.server import oai as _oai_routes  # noqa: F401,E402
from perplexity.server import admin as _admin_routes  # noqa: F401,E402

# Initialize pool once per cold-start
get_pool()

# Export an ASGI app for Vercel Python runtime
# Ensure the MCP endpoint remains at /mcp
app = mcp.http_app(path="/mcp")
