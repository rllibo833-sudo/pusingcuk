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
_ALLOWED_ROLES = {"system", "user", "assistant", "tool"}


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


def validate_messages(messages: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate and bound a chat history before it leaves the process."""
    if isinstance(messages, (str, bytes, dict)):
        raise LocalAIProviderError("AI_MESSAGES_INVALID")
    try:
        incoming = list(messages)
    except TypeError as exc:
        raise LocalAIProviderError("AI_MESSAGES_INVALID") from exc
    if not incoming or len(incoming) > 20:
        raise LocalAIProviderError("AI_MESSAGE_COUNT_INVALID")
    clean: list[dict[str, Any]] = []
    total = 0
    for message in incoming:
        if not isinstance(message, dict):
            raise LocalAIProviderError("AI_MESSAGE_INVALID")
        role = message.get("role")
        allowed_fields = {"role", "content", "tool_calls"} if role == "assistant" else ({"role", "content", "tool_name"} if role == "tool" else {"role", "content"})
        if set(message) - allowed_fields:
            raise LocalAIProviderError("AI_MESSAGE_INVALID")
        content = message.get("content")
        if role not in _ALLOWED_ROLES or not isinstance(content, str):
            raise LocalAIProviderError("AI_MESSAGE_INVALID")
        if role != "assistant" and not content.strip():
            raise LocalAIProviderError("AI_MESSAGE_INVALID")
        if len(content) > 12_000:
            raise LocalAIProviderError("AI_MESSAGE_TOO_LARGE")
        item: dict[str, Any] = {"role": role, "content": content}
        if role == "tool":
            tool_name = message.get("tool_name")
            if not isinstance(tool_name, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", tool_name):
                raise LocalAIProviderError("AI_TOOL_MESSAGE_INVALID")
            item["tool_name"] = tool_name
        if role == "assistant" and "tool_calls" in message:
            calls = message["tool_calls"]
            if not isinstance(calls, list) or len(calls) > 2:
                raise LocalAIProviderError("AI_TOOL_CALLS_INVALID")
            for call in calls:
                if not isinstance(call, dict) or set(call) - {"id", "type", "function", "thought_signature"}:
                    raise LocalAIProviderError("AI_TOOL_CALLS_INVALID")
                function = call.get("function")
                if not isinstance(function, dict) or set(function) - {"name", "arguments"}:
                    raise LocalAIProviderError("AI_TOOL_CALLS_INVALID")
                if not isinstance(function.get("name"), str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", function["name"]):
                    raise LocalAIProviderError("AI_TOOL_CALLS_INVALID")
                if not isinstance(function.get("arguments"), dict):
                    raise LocalAIProviderError("AI_TOOL_CALLS_INVALID")
                signature = call.get("thought_signature")
                if signature is not None and (not isinstance(signature, str) or not signature or len(signature) > 16_000):
                    raise LocalAIProviderError("AI_TOOL_CALLS_INVALID")
                bounded_call = {key: value for key, value in call.items() if key != "thought_signature"}
                if len(json.dumps(bounded_call, ensure_ascii=False)) > 4_000:
                    raise LocalAIProviderError("AI_TOOL_CALLS_INVALID")
            item["tool_calls"] = calls
        total += len(content)
        clean.append(item)
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

    def generate_turn(
        self, messages: Iterable[dict[str, Any]], *, system_prompt: str | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
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
        if tools is not None and (not isinstance(tools, list) or len(tools) > 8):
            raise LocalAIProviderError("AI_TOOLS_INVALID")
        # Gemini-specific thought signatures are internal history metadata, not Ollama API fields.
        # Keep the original history intact for orchestration but strip provider-foreign keys on egress.
        provider_messages = []
        for item in clean:
            if "tool_calls" not in item:
                provider_messages.append(item)
                continue
            outbound = dict(item)
            outbound["tool_calls"] = [
                {key: value for key, value in call.items() if key != "thought_signature"}
                for call in item["tool_calls"]
            ]
            provider_messages.append(outbound)
        payload_data: dict[str, Any] = {"model": self.model, "messages": provider_messages, "stream": False}
        if tools:
            payload_data["tools"] = tools
        payload = json.dumps(payload_data, ensure_ascii=False).encode("utf-8")
        request = Request(
            self.endpoint, data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        try:
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
        raw_calls = message.get("tool_calls", []) if isinstance(message, dict) else []
        if not isinstance(raw_calls, list) or len(raw_calls) > 2:
            raise LocalAIProviderError("AI_TOOL_CALLS_INVALID")
        calls = []
        for index, call in enumerate(raw_calls):
            function = call.get("function") if isinstance(call, dict) else None
            name = function.get("name") if isinstance(function, dict) else None
            arguments = function.get("arguments", {}) if isinstance(function, dict) else None
            if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", name):
                raise LocalAIProviderError("AI_TOOL_CALL_INVALID")
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    raise LocalAIProviderError("AI_TOOL_ARGUMENTS_INVALID") from None
            if not isinstance(arguments, dict):
                raise LocalAIProviderError("AI_TOOL_ARGUMENTS_INVALID")
            call_id = call.get("id", f"tool-call-{index + 1}")
            if not isinstance(call_id, str) or not call_id or len(call_id) > 100:
                call_id = f"tool-call-{index + 1}"
            calls.append({"id": call_id, "name": name, "arguments": arguments})
        if not isinstance(content, str):
            content = ""
        if not content.strip() and not calls:
            raise LocalAIProviderError("AI_RESPONSE_CONTENT_MISSING")
        return {"content": content.strip(), "tool_calls": calls}

    def generate(self, messages: Iterable[dict[str, Any]], *, system_prompt: str | None = None) -> str:
        turn = self.generate_turn(messages, system_prompt=system_prompt)
        if turn["tool_calls"]:
            raise LocalAIProviderError("AI_TOOL_CALL_UNEXPECTED")
        return turn["content"]
