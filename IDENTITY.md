# PusingCuk Identity — Three Parts, One Ecosystem

This document is the reference for distinguishing the three main parts of the PusingCuk ecosystem.

## 1. The .cuk language

An experimental programming language using the `.cuk` extension, Indonesian-language keywords, a written specification, a reference interpreter, a native C runtime, and a JavaScript backend.

**Goal:** a language people can learn from a phone, run locally, and eventually use to build native executables.

Principles:
- The specification is authoritative; implementations must follow it.
- Vocabulary is controlled. New aliases require an explicit project decision.
- No production-readiness claim without conformance evidence.

Key locations: `SPEC.md`, `lexer.py`, `parser.py`, `evaluator.py`, `ast_nodes.py`, `pusingcuk_new.py`, `library/`, `native/`, `compiler/`, `tests/`, `examples/`, and `site/`.

## 2. PusingCuk AI

An assistant grounded in the language specification, vocabulary, built-in contract, and .cuk fixtures. It is not a foundation model trained from scratch and is not the authority on language semantics; `SPEC.md` remains authoritative.

Its purpose is to answer .cuk questions, produce examples, and explain diagnostics using project context. Providers may vary; capability claims must match the implementation that is actually available.

Related locations include `library/assistant.py`, `library/ai_tools.py`, `library/knowledge_grounding.py`, `library/knowledge_index.json`, `library/local_memory.py`, available AI providers, and `examples/ai/`.

## 3. Cuk Reality Engine

Conformance tooling for checking behavior across targets: run fixtures, compare outputs, record differences, and generate reproducible reports. Reports must come from real executions; static files or badges alone do not prove a generator works.

Related locations include `tests/conformance/`, `tools/`, `reports/`, `docs/COMPATIBILITY.md`, and the relevant CI workflows.

## How they relate

The .cuk language defines the semantics. PusingCuk AI helps people use and develop the language with relevant context. Cuk Reality Engine checks whether compatibility claims are supported by evidence.

Neither AI nor the Reality Engine may silently change the language specification. Target status must be limited to the conformance evidence actually available.
