"""SSRF mitigation tests for rescuetime-mcp (MYC-101).

Two fetch sites:
  - server.py::_get (FastMCP tool path)
  - src/rescuetime_mcp/client.py::RescueTimeClient._request

Both wired with sanitize_or_raise + assert_public_ip + follow_redirects=False.

These tests exercise the safety check by passing a malformed endpoint that
forces the URL chars/scheme path to trigger.
"""
from __future__ import annotations

import os
import socket
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def _env():
    os.environ.setdefault("RESCUETIME_API_KEY", "dummy-key")
    yield


# ---------- server.py::_get ----------

class TestServerGet:
    @pytest.mark.asyncio
    async def test_rejects_endpoint_with_backslash(self):
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from server import _get
        with pytest.raises(RuntimeError, match="SSRF"):
            await _get("\\evil")

    @pytest.mark.asyncio
    async def test_rejects_endpoint_with_crlf(self):
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from server import _get
        with pytest.raises(RuntimeError, match="SSRF"):
            await _get("data\r\nHost: evil")


# ---------- src/rescuetime_mcp/client.py::_request ----------

class TestSDKClientRequest:
    @pytest.mark.asyncio
    async def test_rejects_endpoint_with_backslash(self):
        from rescuetime_mcp.client import RescueTimeAPIError, RescueTimeClient
        c = RescueTimeClient()
        with pytest.raises(RescueTimeAPIError, match="SSRF"):
            await c._request("\\evil")

    @pytest.mark.asyncio
    async def test_dns_rebind_blocked(self):
        from rescuetime_mcp.client import RescueTimeAPIError, RescueTimeClient
        c = RescueTimeClient()
        # Monkeypatch BASE_URL to a host that "resolves" to 10.0.0.1
        c.BASE_URL = "http://attacker.example.com"
        with patch("mycelium_security.url.socket.getaddrinfo") as mock_resolver:
            mock_resolver.return_value = [
                (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("10.0.0.1", 0))
            ]
            with pytest.raises(RescueTimeAPIError, match="SSRF"):
                await c._request("daily_summary_feed")

    @pytest.mark.asyncio
    async def test_aws_metadata_blocked(self):
        from rescuetime_mcp.client import RescueTimeAPIError, RescueTimeClient
        c = RescueTimeClient()
        c.BASE_URL = "http://169.254.169.254"
        with pytest.raises(RescueTimeAPIError, match="SSRF"):
            await c._request("latest/meta-data/iam")

    @pytest.mark.asyncio
    async def test_follow_redirects_false(self):
        import httpx
        captured = {}

        class _Spy(httpx.AsyncClient):
            def __init__(self, *args, **kwargs):
                captured.update(kwargs)
                super().__init__(*args, **kwargs)

        from rescuetime_mcp.client import RescueTimeClient
        c = RescueTimeClient()
        with patch("rescuetime_mcp.client.httpx.AsyncClient", _Spy):
            try:
                await c._request("daily_summary_feed")
            except Exception:
                pass
        assert captured.get("follow_redirects") is False
