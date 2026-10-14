# PusingCuk AI knowledge grounding contract

**Status:** independent initial implementation; not a production AI assistant yet.  
**Owner:** PusingCuk.

## Purpose

This module provides deterministic lexical retrieval and provenance-checked citations without importing runtime code from CORE or copying the Founder OS index. The index is explicit and curated; it does not crawl repositories, train a model, or implement vector search.

## Index and source policy

library/knowledge_index.json contains 16 independently authored summaries sourced only from the PusingCuk repository. Each entry binds this repository, commit SHA, and path; the reader rejects mismatches, duplicate IDs, private visibility, malformed URLs, and indexes above 100 records. Founder-OS and CORE are not runtime or knowledge-index dependencies.

Only a small, reviewed subset of primary documents should be added. The summaries are local to PusingCuk; source URLs preserve provenance and are not a runtime dependency. Do not automatically index any repository; keep the index limited to reviewed PusingCuk sources.

## Retrieval and citations

rank_knowledge() applies deterministic lexical weights to title, topics, keywords, summary, and excerpt. It normalizes case and diacritics, returns matched terms and immutable provenance, and caps results. This is lexical search, not semantic/vector search; real Indonesian query relevance still needs evaluation.

format_citations() and append_citations() accept only validated source records. Citation URLs come from the index, never from URLs invented by a model. A citation establishes provenance, not that every answer claim is true.

## Local model adapter

library/local_ai_provider.py provides a no-paid-key Ollama-compatible chat adapter for a model running on the same device. It defaults to loopback-only HTTP, disables environment-configured proxies, bounds conversation length and response size, applies a timeout, and emits stable errors without returning endpoint details. The provider adapter itself performs bounded model I/O only. Tool authorization and orchestration live in `library/assistant.py` and `library/ai_tools.py`; optional user-initiated project notes live in `library/local_memory.py`. Chat transcripts are not automatically persisted. A local model and Ollama runtime must be installed separately.

## Tool calling boundary

The Ollama adapter parses a bounded set of structured tool calls. The assistant executes only names in its registry, validates each argument object, and accepts at most two tool calls per model turn with a bounded number of follow-up rounds. Knowledge search is read-only. The budget rule requires a locally configured bearer token and the existing Docker-isolated runner; if the runner is unavailable, the tool fails closed. The model never receives the token and cannot submit source code, commands, paths, or arbitrary capabilities.

## Security boundaries

- Retrieved text is untrusted data, not system instructions or executable code.
- Do not store credentials, private user data, service-role keys, or operational secrets in the index.
- Never execute model-generated .cuk, Python, shell, or other source as part of retrieval.
- Provider calls, conversation memory, tool authorization, and execution isolation remain separate capabilities that must be implemented and tested before production use.

## Regression coverage

The grounding suite covers 14 synthetic records plus the actual 16-entry curated index, Indonesian query ranking, normalization, unrelated-query rejection, commit/path matching, URL validation, visibility, duplicate IDs, index size, citation filtering/deduplication, and bounded results. AI tool-contract tests also reject booleans, floats, strings, nulls, negative and over-limit rule inputs, missing/extra fields, and unregistered shell, filesystem, network, database, provider, or process capabilities before dispatch; accepted boundary integers are forwarded without coercion, and the fixed rule request declares no ambient capabilities. The local provider suite covers request shape, system prompt placement, loopback-only enforcement, bounded inputs and outputs, malformed responses, and network failure.


## Local assistant CLI

The local-first assistant entry point is `pusingcuk-ai`. It combines the pinned curated index, bounded in-process conversation history, the loopback-only Ollama adapter, and citations derived from validated index entries. It keeps the active conversation in memory, supports registered tool calls through the assistant orchestrator, and only saves project notes when the user explicitly opts in. The CLI is not a production web service. An experimental loopback-only HTTP adapter exists at `library/ai_service.py`; it has no public deployment or per-user identity. See `AI_LOCAL_SERVICE.md` for its exact boundary.

Run after installing the project and a compatible local Ollama model with:

```sh
pusingcuk-ai --model qwen3:4b
```

Type `/reset` to clear session memory or `/keluar` to exit. The local model runtime must already be running. The adapter rejects remote endpoints by default.


## Retrieval evaluation

The 16-case Indonesian retrieval benchmark is stored in tests/fixtures/knowledge_retrieval_cases.json and asserted by the test suite. It currently targets top-1 exact source IDs for a small curated query set over PusingCuk sources; it is a regression baseline, not evidence of general semantic-search quality.


## Local project memory

The assistant can load a small local project-memory file at the user's home directory under .pusingcuk/memory.json (or the path explicitly configured by PUSINGCUK_AI_MEMORY_PATH). Chat transcripts are never persisted automatically. Users must explicitly run /ingat to save a project decision, constraint, fact, or recovery note; /memori searches/list notes and /hapus-memori deletes a selected ID. The store has a 200-record and 2,000-character-per-record cap, rejects common credential patterns, writes atomically, and uses restrictive POSIX permissions when available. This is local continuity memory, not an external citation source.


## Optional Gemini API provider

`library/gemini_ai_provider.py` implements the public Gemini GenerateContent REST contract independently of external application backends. The default remains local Ollama; Gemini is an explicit opt-in via `pusingcuk-ai --provider gemini` and `GEMINI_API_KEY`. The key is sent in the HTTPS `x-goog-api-key` header, never embedded in the URL or stored in the repository. Request/response sizes, model identifiers, tool declarations, tool-call count, timeout, and error messages are bounded. API availability and quota depend on the user's Google AI account.

The adapter follows the public [Gemini GenerateContent API](https://ai.google.dev/api/generate-content) and [function-calling contract](https://ai.google.dev/gemini-api/docs/function-calling). It is an optional inference provider, not a runtime dependency and not evidence of production deployment.


## Source migration

The PusingCuk-only index is intentional. Reviewed ideas from Founder-OS and CORE are rewritten and tracked in [AI_ENGINE_MIGRATION_LEDGER.md](AI_ENGINE_MIGRATION_LEDGER.md); their immutable external links provide provenance for the decisions, not runtime retrieval sources. Do not copy external knowledge indexes or operational records wholesale.
