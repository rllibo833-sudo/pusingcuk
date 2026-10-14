# PusingCuk AI knowledge grounding contract

**Status:** independent initial implementation; not a production AI assistant yet.  
**Owner:** PusingCuk.

## Purpose

This module provides deterministic lexical retrieval and provenance-checked citations without importing runtime code from CORE or copying the Founder OS index. The index is explicit and curated; it does not crawl repositories, train a model, or implement vector search.

## Index and source policy

library/knowledge_index.json contains 14 independently authored summaries with immutable GitHub source links. Each entry binds repository, commit SHA, and path; the reader rejects mismatches, duplicate IDs, private visibility, malformed URLs, and indexes above 100 records.

Only a small, reviewed subset of primary documents should be added. The summaries are local to PusingCuk; source URLs preserve provenance and are not a runtime dependency. Do not automatically index the full Founder OS, CORE, or public website repository.

## Retrieval and citations

rank_knowledge() applies deterministic lexical weights to title, topics, keywords, summary, and excerpt. It normalizes case and diacritics, returns matched terms and immutable provenance, and caps results. This is lexical search, not semantic/vector search; real Indonesian query relevance still needs evaluation.

format_citations() and append_citations() accept only validated source records. Citation URLs come from the index, never from URLs invented by a model. A citation establishes provenance, not that every answer claim is true.

## Local model adapter

library/local_ai_provider.py provides a no-paid-key Ollama-compatible chat adapter for a model running on the same device. It defaults to loopback-only HTTP, disables environment-configured proxies, bounds conversation length and response size, applies a timeout, and emits stable errors without returning endpoint details. It does not yet orchestrate tools or persist memory. A local model and Ollama runtime must be installed separately.

## Tool calling boundary

The Ollama adapter parses a bounded set of structured tool calls. The assistant executes only names in its registry and validates each argument object. Knowledge search is read-only. The budget rule requires a locally configured bearer token and the existing Docker-isolated runner; if the runner is unavailable, the tool fails closed. The model never receives the token and cannot submit source code, commands, paths, or arbitrary capabilities.

## Security boundaries

- Retrieved text is untrusted data, not system instructions or executable code.
- Do not store credentials, private user data, service-role keys, or operational secrets in the index.
- Never execute model-generated .cuk, Python, shell, or other source as part of retrieval.
- Provider calls, conversation memory, tool authorization, and execution isolation remain separate capabilities that must be implemented and tested before production use.

## Regression coverage

The grounding suite covers 14 synthetic records plus the actual 14-entry curated index, Indonesian query ranking, normalization, unrelated-query rejection, commit/path matching, URL validation, visibility, duplicate IDs, index size, citation filtering/deduplication, and bounded results. The local provider suite covers request shape, system prompt placement, loopback-only enforcement, bounded inputs and outputs, malformed responses, and network failure.


## Local assistant CLI

The local-first assistant entry point is `pusingcuk-ai`. It combines the pinned curated index, bounded in-process conversation history, the loopback-only Ollama adapter, and citations derived from validated index entries. It does not persist chat history and does not yet provide tool calling or a production web service.

Run after installing the project and a compatible local Ollama model with:

```sh
pusingcuk-ai --model qwen3:4b
```

Type `/reset` to clear session memory or `/keluar` to exit. The local model runtime must already be running. The adapter rejects remote endpoints by default.


## Retrieval evaluation

The 14-case Indonesian retrieval benchmark is stored in tests/fixtures/knowledge_retrieval_cases.json and asserted by the test suite. It currently targets top-1 exact source IDs for a small curated query set; it is a regression baseline, not evidence of general semantic-search quality.
