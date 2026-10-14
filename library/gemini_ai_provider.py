"""Independent, bounded Gemini GenerateContent API adapter for PusingCuk."""
import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener

from library.local_ai_provider import LocalAIProviderError, validate_messages

_MODEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_TOOL = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
_ROOT = "https://generativelanguage.googleapis.com/v1beta/models/"


class GeminiGenerateContentProvider:
    def __init__(self, api_key, model="gemini-3.8-flash", timeout_seconds=30, max_response_bytes=1_000_000):
        if not isinstance(api_key, str) or not 8 <= len(api_key.strip()) <= 256 or any(c.isspace() for c in api_key):
            raise LocalAIProviderError("AI_API_KEY_INVALID")
        if not isinstance(model, str) or not _MODEL.fullmatch(model):
            raise LocalAIProviderError("AI_MODEL_INVALID")
        if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)) or not 0.1 <= timeout_seconds <= 120:
            raise LocalAIProviderError("AI_TIMEOUT_INVALID")
        if isinstance(max_response_bytes, bool) or not isinstance(max_response_bytes, int) or not 1024 <= max_response_bytes <= 4_000_000:
            raise LocalAIProviderError("AI_RESPONSE_LIMIT_INVALID")
        self._key = api_key.strip()
        self.model = model
        self.endpoint = _ROOT + model + ":generateContent"
        self.timeout = float(timeout_seconds)
        self.max_response_bytes = max_response_bytes

    @staticmethod
    def _contents(messages):
        contents = []
        def append(role, parts):
            if not parts:
                return
            if contents and contents[-1]["role"] == role:
                contents[-1]["parts"].extend(parts)
            else:
                contents.append({"role": role, "parts": parts})
        for msg in messages:
            role, content = msg["role"], msg["content"]
            if role == "system":
                continue
            if role == "tool":
                try:
                    result = json.loads(content)
                except (TypeError, json.JSONDecodeError):
                    result = {"result": content[:2500]}
                if not isinstance(result, dict):
                    result = {"result": result}
                append("user", [{"functionResponse": {"name": msg["tool_name"], "response": result}}])
                continue
            target = "user" if role == "user" else "model"
            parts = [{"text": content}] if content.strip() else []
            if role == "assistant":
                for call in msg.get("tool_calls", []):
                    fn = call["function"]
                    item = {"name": fn["name"], "args": fn["arguments"]}
                    if call.get("id"):
                        item["id"] = call["id"]
                    part = {"functionCall": item}
                    signature = call.get("thought_signature")
                    if signature is not None:
                        if not isinstance(signature, str) or not signature or len(signature) > 16_000:
                            raise LocalAIProviderError("AI_THOUGHT_SIGNATURE_INVALID")
                        part["thoughtSignature"] = signature
                    parts.append(part)
            append(target, parts)
        if not contents or not any(item["role"] == "user" for item in contents):
            raise LocalAIProviderError("AI_USER_MESSAGE_REQUIRED")
        return contents

    def generate_turn(self, messages, *, system_prompt=None, tools=None):
        clean = validate_messages(messages)
        if system_prompt is not None and (not isinstance(system_prompt, str) or len(system_prompt) > 8000):
            raise LocalAIProviderError("AI_SYSTEM_PROMPT_INVALID")
        if tools is not None and (not isinstance(tools, list) or len(tools) > 8):
            raise LocalAIProviderError("AI_TOOLS_INVALID")
        declarations = []
        for item in tools or []:
            fn = item.get("function") if isinstance(item, dict) and item.get("type") == "function" else None
            if not isinstance(fn, dict) or set(fn) - {"name", "description", "parameters"}:
                raise LocalAIProviderError("AI_TOOLS_INVALID")
            name, description, parameters = fn.get("name"), fn.get("description"), fn.get("parameters")
            if not isinstance(name, str) or not _TOOL.fullmatch(name) or not isinstance(description, str) or not description.strip() or not isinstance(parameters, dict) or parameters.get("type") != "object":
                raise LocalAIProviderError("AI_TOOLS_INVALID")
            if len(json.dumps(parameters, ensure_ascii=False)) > 8000:
                raise LocalAIProviderError("AI_TOOLS_INVALID")
            declarations.append({"name": name, "description": description[:1000], "parameters": parameters})
        systems = [m["content"].strip() for m in clean if m["role"] == "system" and m["content"].strip()]
        if isinstance(system_prompt, str) and system_prompt.strip():
            systems = [system_prompt.strip()]
        payload = {"contents": self._contents(clean), "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024}}
        if systems:
            payload["systemInstruction"] = {"parts": [{"text": "\n\n".join(systems)[:8000]}]}
        if declarations:
            payload["tools"] = [{"functionDeclarations": declarations}]
        request = Request(self.endpoint, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                          headers={"Content-Type": "application/json", "x-goog-api-key": self._key}, method="POST")
        try:
            with build_opener(ProxyHandler({})).open(request, timeout=self.timeout) as response:
                raw = response.read(self.max_response_bytes + 1)
                if len(raw) > self.max_response_bytes:
                    raise LocalAIProviderError("AI_RESPONSE_TOO_LARGE")
                if not 200 <= response.status < 300:
                    raise LocalAIProviderError("AI_PROVIDER_HTTP_ERROR")
        except LocalAIProviderError:
            raise
        except (HTTPError, URLError, TimeoutError, OSError):
            raise LocalAIProviderError("AI_PROVIDER_UNAVAILABLE") from None
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            raise LocalAIProviderError("AI_RESPONSE_INVALID_JSON") from None
        candidates = data.get("candidates") if isinstance(data, dict) else None
        candidate = candidates[0] if isinstance(candidates, list) and candidates else None
        body = candidate.get("content") if isinstance(candidate, dict) else None
        parts = body.get("parts") if isinstance(body, dict) else None
        if not isinstance(parts, list):
            raise LocalAIProviderError("AI_RESPONSE_CONTENT_MISSING")
        texts, calls = [], []
        for part in parts:
            if not isinstance(part, dict):
                continue
            if isinstance(part.get("text"), str):
                texts.append(part["text"])
            call = part.get("functionCall")
            if call is None:
                continue
            if not isinstance(call, dict) or set(call) - {"name", "args", "id"}:
                raise LocalAIProviderError("AI_TOOL_CALL_INVALID")
            name, args = call.get("name"), call.get("args", {})
            if not isinstance(name, str) or not _TOOL.fullmatch(name):
                raise LocalAIProviderError("AI_TOOL_CALL_INVALID")
            if not isinstance(args, dict) or len(json.dumps(args, ensure_ascii=False)) > 4000:
                raise LocalAIProviderError("AI_TOOL_ARGUMENTS_INVALID")
            call_id = call.get("id") or "gemini-tool-" + str(len(calls) + 1)
            if not isinstance(call_id, str) or len(call_id) > 100:
                call_id = "gemini-tool-" + str(len(calls) + 1)
            signature = part.get("thoughtSignature")
            if signature is not None and (not isinstance(signature, str) or not signature or len(signature) > 16_000):
                raise LocalAIProviderError("AI_THOUGHT_SIGNATURE_INVALID")
            parsed_call = {"id": call_id, "name": name, "arguments": args}
            if signature is not None:
                parsed_call["thought_signature"] = signature
            calls.append(parsed_call)
            if len(calls) > 2:
                raise LocalAIProviderError("AI_TOOL_CALLS_INVALID")
        answer = "\n".join(texts).strip()
        if not answer and not calls:
            raise LocalAIProviderError("AI_RESPONSE_CONTENT_MISSING")
        return {"content": answer[:8000], "tool_calls": calls}

    def generate(self, messages, *, system_prompt=None):
        turn = self.generate_turn(messages, system_prompt=system_prompt)
        if turn["tool_calls"]:
            raise LocalAIProviderError("AI_TOOL_CALL_UNEXPECTED")
        return turn["content"]
