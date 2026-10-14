# PusingCuk AI local HTTP service

**Status:** authenticated local integration adapter / experimental. It is not a public hosted service, does not include TLS or per-user identity, and is not a foundation model trained by PusingCuk.

## Start

Ensure Ollama and the selected model are available locally, then set a strong token:

```sh
export PUSINGCUK_AI_SERVICE_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export PUSINGCUK_AI_SERVICE_BIND=127.0.0.1
export PUSINGCUK_AI_SERVICE_PORT=8765
export PUSINGCUK_AI_PROVIDER=ollama
export PUSINGCUK_AI_MODEL=qwen3:4b
python -m library.ai_service
```

The service fails closed if the token is missing/short or the bind address is not an IPv4 loopback IP. The Ollama adapter separately restricts its endpoint to loopback by default. Choosing `PUSINGCUK_AI_PROVIDER=gemini` opts into a third-party service and requires its key/quota; request data then leaves the local machine.

## Contract

- `GET /healthz`: minimal process liveness only; it does not verify provider readiness.
- `POST /v1/chat`: authenticated JSON request with exactly `session_id` (16–64 ASCII letters/digits/underscore/hyphen) and `query` (1–300 characters). The response includes a generated request ID and the assistant's grounded answer/citations.
- Bearer token must contain at least 32 UTF-8 bytes; every chat request needs exactly one Authorization header.
- Request body is capped at 4 KiB, duplicate JSON keys and unknown fields are rejected, content length is required, and compressed/chunked bodies are rejected.
- At most four model operations execute concurrently and at most 64 session histories stay in memory. Parallel turns in the same session fail with HTTP 503 rather than racing context; when full, only an idle session may be evicted.
- Chat history is scoped per session and process-memory-only. It is never persisted to disk; restart clears active conversations.
- Error responses are generic and do not include exception details. Default request logging does not write query text, session IDs, bearer credentials or client addresses.
- The server binds to loopback only, with no CORS allowance. Do not port-forward it, put it on a public IP, or treat the shared token as production per-user authorization.

## Example request

```sh
curl --fail-with-body http://127.0.0.1:8765/v1/chat -H "Authorization: Bearer $PUSINGCUK_AI_SERVICE_TOKEN" -H "Content-Type: application/json" --data '{"session_id":"session_0123456789","query":"Apa itu aturan .cuk yang deterministik?"}'
```

Generate a random session ID per conversation; never put the service token in browser JavaScript or public source.

## Not a production deployment

This adapter establishes an authenticated local HTTP contract for integration tests and local clients. A hosted deployment still needs TLS through a trusted gateway, authenticated user identity, per-user authorization and quotas, monitoring, secret rotation, abuse defense, deployment rollback and an independently reviewed execution-isolation boundary for registered rules. The current PusingCuk runtime is not an OS sandbox and must not run arbitrary model-generated code.
