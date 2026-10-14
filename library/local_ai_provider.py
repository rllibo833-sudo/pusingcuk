"""Bounded local Ollama chat adapter for PusingCuk AI.

No paid API key is required. The default endpoint is loopback-only to avoid
silently sending conversation content to an arbitrary remote host.
"""
from __future__ import annotations

import ipaddress
import json
import re
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import ProxyHandler, Request, build_opener

_DEFAULT_ENDPOINT = "http://127.0.0.1:11434/api/chat"
_MODEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
_ALLOWED_ROLES = {"system", "user", "assistant"}


class LocalAIProviderError(RuntimeError):
    """Stable, non-sensitive provider error code."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _is_loopback_endpoint(endpoint: str) -> bool:
    try:
        parsed = urlparse(endpoint)
        if parsed.scheme != "http" or parsed.username or parsed.password:
            return False
        if parsed.path not in ("", "/", "/api/chat") or parsed.query or parsed.fragment:
            return False
        if parsed.port is not None and not 1 <= parsed.port <= 65535:
            return False
        host = parsed.hostname
        if not host:
            return False
        if host.casefold() == "localhost":
            return True
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def validate_messages(messages: Iterable[dict[str, Any]]) -> list[dict[str, str]]:
    """Validate and bound a chat history before it leaves the process."""
    if isinstance(messages, (str, bytes, dict)):
        raise LocalAIProviderError("AI_MESSAGES_INVALID")
    try:
        incoming = list(messages)
    except TypeError as exc:
        raise LocalAIProviderError("AI_MESSAGES_INVALID") from exc
    if not incoming or len(incoming) > 20:
        raise LocalAIProviderError("AI_MESSAGE_COUNT_INVALID")
    clean: list[dict[str, str]] = []
    total = 0
    for message in incoming:
        if not isinstance(message, dict) or set(message) - {"role", "content"}:
            raise LocalAIProviderError("AI_MESSAGE_INVALID")
        role, content = message.get("role"), message.get("content")
        if role not in _ALLOWED_ROLES or not isinstance(content, str) or not content.strip():
            raise LocalAIProviderError("AI_MESSAGE_INVALID")
        if len(content) > 12_000:
            raise LocalAIProviderError("AI_MESSAGE_TOO_LARGE")
        total += len(content)
        clean.append({"role": role, "content": content})
    if total > 24_000:
        raise LocalAIProviderError("AI_CONTEXT_TOO_LARGE")
    if not any(item["role"] == "user" for item in clean):
        raise LocalAIProviderError("AI_USER_MESSAGE_REQUIRED")
    return clean


class OllamaChatProvider:
    """Call a local Ollama-compatible /api/chat endpoint with bounded I/O."""

    def __init__(
        self, model: str = "qwen3:4b", endpoint: str = _DEFAULT_ENDPOINT,
        *, timeout_seconds: float = 30.0, max_response_bytes: int = 1_000_000,
    ) -> None:
        if not isinstance(model, str) or not _MODEL_RE.fullmatch(model):
            raise LocalAIProviderError("AI_MODEL_INVALID")
        if not isinstance(endpoint, str) or not _is_loopback_endpoint(endpoint):
            raise LocalAIProviderError("AI_ENDPOINT_NOT_LOOPBACK")
        if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)) or not 0.1 <= timeout_seconds <= 120:
            raise LocalAIProviderError("AI_TIMEOUT_INVALID")
        if isinstance(max_response_bytes, bool) or not isinstance(max_response_bytes, int) or not 1024 <= max_response_bytes <= 4_000_000:
            raise LocalAIProviderError("AI_RESPONSE_LIMIT_INVALID")
        self.model = model
        parsed = urlparse(endpoint)
        self.endpoint = endpoint if parsed.path == "/api/chat" else endpoint.rstrip("/") + "/api/chat"
        self.timeout_seconds = float(timeout_seconds)
        self.max_response_bytes = max_response_bytes

    def generate(self, messages: Iterable[dict[str, Any]], *, system_prompt: str | None = None) -> str:
        clean = validate_messages(messages)
        if system_prompt is not None:
            if not isinstance(system_prompt, str) or len(system_prompt) > 8_000:
                raise LocalAIProviderError("AI_SYSTEM_PROMPT_INVALID")
            if system_prompt.strip():
                if clean[0]["role"] == "system":
                    clean[0] = {"role": "system", "content": system_prompt.strip()}
                else:
                    clean.insert(0, {"role": "system", "content": system_prompt.strip()})
        if len(clean) > 20 or sum(len(item["content"]) for item in clean) > 24_000:
            raise LocalAIProviderError("AI_CONTEXT_TOO_LARGE")
        payload = json.dumps(
            {"model": self.model, "messages": clean, "stream": False},
            ensure_ascii=False,
        ).encode("utf-8")
        request = Request(
            self.endpoint, data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        try:
            # Disable environment-configured HTTP proxies: this adapter is local-only.
            opener = build_opener(ProxyHandler({}))
            with opener.open(request, timeout=self.timeout_seconds) as response:
                raw = response.read(self.max_response_bytes + 1)
                if len(raw) > self.max_response_bytes:
                    raise LocalAIProviderError("AI_RESPONSE_TOO_LARGE")
                if not 200 <= response.status < 300:
                    raise LocalAIProviderError(f"AI_HTTP_{response.status}")
        except LocalAIProviderError:
            raise
        except HTTPError as exc:
            raise LocalAIProviderError(f"AI_HTTP_{exc.code}") from None
        except (URLError, TimeoutError, OSError) as exc:
            if isinstance(exc, TimeoutError) or "timed out" in str(exc).casefold():
                raise LocalAIProviderError("AI_TIMEOUT") from None
            raise LocalAIProviderError("AI_PROVIDER_UNAVAILABLE") from None
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            raise LocalAIProviderError("AI_RESPONSE_INVALID_JSON") from None
        message = data.get("message") if isinstance(data, dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str) or not content.strip():
            raise LocalAIProviderError("AI_RESPONSE_CONTENT_MISSING")
        return content.strip()
