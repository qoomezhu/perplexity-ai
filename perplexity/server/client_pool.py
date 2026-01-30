"""
Client pool for managing multiple Perplexity API tokens with load balancing.

Provides round-robin client selection with exponential backoff retry on failures.
Supports heartbeat testing to automatically verify token health.

Notes on "token keepalive":
- A Perplexity cookie-based "session_token" may have an absolute expiry (e.g. ~48h).
  No keepalive can guarantee indefinite validity.
- This module's heartbeat is primarily used to (1) detect login status and
  (2) perform a lightweight request to keep the session warm when possible.
"""

import asyncio
import json
import logging
import pathlib
import os
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from ..client import Client

logger = logging.getLogger(__name__)


class ClientWrapper:
    """Wrapper for Client with failure tracking, weight, and availability status."""

    # Weight constants
    DEFAULT_WEIGHT = 100
    MIN_WEIGHT = 10
    WEIGHT_DECAY = 10  # Amount to decrease on pro failure
    WEIGHT_RECOVERY = 5  # Amount to recover on success

    # Backoff constants
    INITIAL_BACKOFF = 60  # First failure: 60 seconds cooldown
    MAX_BACKOFF = 3600  # Maximum backoff: 1 hour

    def __init__(self, client: Client, client_id: str):
        self.client = client
        self.id = client_id
        self.fail_count = 0
        self.available_after: float = 0
        self.request_count = 0
        self.weight = self.DEFAULT_WEIGHT  # Higher weight = higher priority
        self.pro_fail_count = 0  # Track pro-specific failures
        self.enabled = True  # Whether this client is enabled for use
        self.state = "unknown"  # Token state: "normal", "offline", "unknown", "anonymous"
        self.last_heartbeat: Optional[float] = None  # Last heartbeat check timestamp

    def is_available(self) -> bool:
        """Check if the client is currently available (enabled and not in backoff)."""
        return self.enabled and time.time() >= self.available_after

    def mark_failure(self) -> None:
        """Mark the client as failed, applying exponential backoff.

        First failure: 60s cooldown
        Consecutive failures: 60s * 2^(fail_count-1), max 1 hour
        """
        self.fail_count += 1
        backoff = min(self.MAX_BACKOFF, self.INITIAL_BACKOFF * (2 ** (self.fail_count - 1)))
        self.available_after = time.time() + backoff

    def mark_success(self) -> None:
        """Mark the client as successful, resetting failure state and recovering weight."""
        self.fail_count = 0
        self.available_after = 0
        self.request_count += 1
        if self.weight < self.DEFAULT_WEIGHT:
            self.weight = min(self.DEFAULT_WEIGHT, self.weight + self.WEIGHT_RECOVERY)

    def mark_pro_failure(self) -> None:
        """Mark that a pro request failed for this client, reducing its weight."""
        self.pro_fail_count += 1
        self.weight = max(self.MIN_WEIGHT, self.weight - self.WEIGHT_DECAY)

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of this client."""
        available = self.is_available()
        next_available_at = None
        if not available:
            next_available_at = datetime.fromtimestamp(
                self.available_after, tz=timezone.utc
            ).isoformat()

        last_heartbeat_at = None
        if self.last_heartbeat:
            last_heartbeat_at = datetime.fromtimestamp(
                self.last_heartbeat, tz=timezone.utc
            ).isoformat()

        return {
            "id": self.id,
            "available": self.is_available(),
            "enabled": self.enabled,
            "state": self.state,
            "fail_count": self.fail_count,
            "next_available_at": next_available_at,
            "last_heartbeat_at": last_heartbeat_at,
            "request_count": self.request_count,
            "weight": self.weight,
            "pro_fail_count": self.pro_fail_count,
        }

    def get_user_info(self) -> Dict[str, Any]:
        """Get user session information for this client."""
        return self.client.get_user_info()


class ClientPool:
    """Pool of Client instances with load balancing and token health checks."""

    def __init__(self, config_path: Optional[str] = None):
        self.clients: Dict[str, ClientWrapper] = {}
        self._rotation_order: List[str] = []
        self._index = 0
        self._lock = threading.Lock()
        self._mode = "anonymous"

        # Heartbeat configuration
        self._heartbeat_config: Dict[str, Any] = {
            "enable": False,
            "question": "现在是农历几月几号？",
            "interval": 6,  # hours
            "tg_bot_token": None,
            "tg_chat_id": None,
        }
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._config_path: Optional[str] = None

        # Load initial clients from config or environment
        self._initialize(config_path)

    def _initialize(self, config_path: Optional[str] = None) -> None:
        """Initialize the pool from config file or environment variables."""
        # Priority 1: Explicit config file path
        if config_path and os.path.exists(config_path):
            self._load_from_config(config_path)
            return

        # Priority 2: Environment variable pointing to config
        env_config_path = os.getenv("PPLX_TOKEN_POOL_CONFIG")
        if env_config_path and os.path.exists(env_config_path):
            self._load_from_config(env_config_path)
            return

        # Priority 3: Default token_pool_config.json in project root
        default_config_paths = [
            pathlib.Path.cwd() / "token_pool_config.json",
            pathlib.Path(__file__).parent.parent / "token_pool_config.json",
        ]
        for default_path in default_config_paths:
            if default_path.exists():
                self._load_from_config(str(default_path))
                return

        # Priority 4: Single token from environment variables
        # Backward/forward compatible env names:
        # - PPLX_CSRF_TOKEN (preferred)
        # - PPLX_NEXT_AUTH_CSRF_TOKEN (legacy)
        # - PPLX_SESSION_TOKEN
        csrf_token = os.getenv("PPLX_CSRF_TOKEN") or os.getenv("PPLX_NEXT_AUTH_CSRF_TOKEN")
        session_token = os.getenv("PPLX_SESSION_TOKEN")
        if csrf_token and session_token:
            self._add_client_internal(
                "default",
                {
                    "next-auth.csrf-token": csrf_token,
                    "__Secure-next-auth.session-token": session_token,
                },
            )
            self._mode = "single"
            return

        # Priority 5: Anonymous client (no cookies)
        self._add_client_internal("anonymous", {})
        self._mode = "anonymous"

    def _load_from_config(self, config_path: str) -> None:
        """Load clients from a JSON configuration file."""
        self._config_path = config_path
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        heart_beat = config.get("heart_beat")
        if heart_beat and isinstance(heart_beat, dict):
            self._heartbeat_config = {
                "enable": heart_beat.get("enable", False),
                "question": heart_beat.get("question", "现在是农历几月几号？"),
                "interval": heart_beat.get("interval", 6),
                "tg_bot_token": heart_beat.get("tg_bot_token"),
                "tg_chat_id": heart_beat.get("tg_chat_id"),
            }

        tokens = config.get("tokens", [])
        if not tokens:
            raise ValueError(f"No tokens found in config file: {config_path}")

        for token_entry in tokens:
            client_id = token_entry.get("id")
            csrf_token = token_entry.get("csrf_token")
            session_token = token_entry.get("session_token")

            if not all([client_id, csrf_token, session_token]):
                raise ValueError(f"Invalid token entry in config: {token_entry}")

            cookies = {
                "next-auth.csrf-token": csrf_token,
                "__Secure-next-auth.session-token": session_token,
            }
            self._add_client_internal(client_id, cookies)

        self._mode = "pool"

    def _add_client_internal(self, client_id: str, cookies: Dict[str, str]) -> None:
        """Internal method to add a client without locking."""
        client = Client(cookies)
        wrapper = ClientWrapper(client, client_id)
        self.clients[client_id] = wrapper
        self._rotation_order.append(client_id)

    # (Other pool management methods unchanged...)

    async def test_client(self, client_id: str) -> Dict[str, Any]:
        """Test a single client (token) by checking login status and performing a lightweight request."""
        with self._lock:
            wrapper = self.clients.get(client_id)
            if not wrapper:
                return {"status": "error", "message": f"Client '{client_id}' not found"}
            client = wrapper.client

        prev_state = wrapper.state
        now = time.time()

        # If it's an anonymous client (no cookies), we can't evaluate login.
        if not client.own:
            with self._lock:
                wrapper.state = "anonymous"
                wrapper.last_heartbeat = now
            return {"status": "ok", "state": "anonymous", "client_id": client_id}

        # 1) Check login status via /api/auth/session
        user_info: Dict[str, Any] = await asyncio.to_thread(client.get_user_info)
        logged_in = isinstance(user_info, dict) and bool(user_info.get("user"))
        expires = user_info.get("expires") if isinstance(user_info, dict) else None

        if not logged_in:
            with self._lock:
                wrapper.state = "offline"
                wrapper.last_heartbeat = now

            if prev_state != "offline":
                await self._send_telegram_notification(
                    f"⚠️ perplexity mcp: <b>{client_id}</b> not logged in (session expired?)."
                )

            return {
                "status": "error",
                "state": "offline",
                "client_id": client_id,
                "reason": "not_logged_in",
                "expires": expires,
            }

        # 2) Perform a lightweight query (best-effort)
        question = self._heartbeat_config.get("question", "ping")
        try:
            response = await asyncio.to_thread(
                client.search,
                question,
                # Keep it cheap and fast:
                mode="auto",
                model=None,
                sources=["web"],
                files={},
                stream=False,
                language="zh-CN",
                # IMPORTANT: do NOT use incognito here; we want real account activity if possible.
                incognito=False,
            )

            ok = bool(response) and ("answer" in response)
            with self._lock:
                wrapper.state = "normal" if ok else "offline"
                wrapper.last_heartbeat = now

            if ok:
                return {
                    "status": "ok",
                    "state": "normal",
                    "client_id": client_id,
                    "expires": expires,
                }

            # No answer: treat as offline
            if prev_state != "offline":
                await self._send_telegram_notification(
                    f"⚠️ perplexity mcp: <b>{client_id}</b> heartbeat query failed (no answer)."
                )

            return {
                "status": "error",
                "state": "offline",
                "client_id": client_id,
                "reason": "no_answer",
                "expires": expires,
            }

        except Exception as e:
            with self._lock:
                wrapper.state = "offline"
                wrapper.last_heartbeat = now

            if prev_state != "offline":
                await self._send_telegram_notification(
                    f"⚠️ perplexity mcp: <b>{client_id}</b> heartbeat exception: {str(e)}"
                )

            return {
                "status": "error",
                "state": "offline",
                "client_id": client_id,
                "reason": "exception",
                "error": str(e),
                "expires": expires,
            }
