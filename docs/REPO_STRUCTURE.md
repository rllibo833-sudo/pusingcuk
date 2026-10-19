# Repository Structure by Responsibility

Use this map to find the right implementation before changing code. It is intentionally not an exhaustive file listing.

## .cuk language

| Path | Responsibility |
|---|---|
| `lexer.py` | Tokenization and keyword aliases |
| `parser.py`, `ast_nodes.py` | Syntax parsing and AST definitions |
| `evaluator.py` | Reference interpreter and primary runtime semantics |
| `SPEC.md` | User-visible syntax and language feature contract |
| `docs/SEMANTIC_CONTRACT.md` | Behaviors that should remain consistent across targets |
| `examples/`, `*.cuk`, `library/*.cuk` | Example programs and rules written in .cuk |

## Compiler and runtimes

| Path | Responsibility |
|---|---|
| `compiler/ir.py`, `compiler_ir.py` | Intermediate representation and validation |
| `compiler/bytecode.py`, `compiler/vm.py` | Bytecode compilation and experimental Python VM |
| `compiler/c_backend.py`, `native/` | C code generation and native runtime; check target limits before claiming parity |
| `native/bytecode_vm.c` | Native C bytecode VM for a limited tested opcode subset |
| `compiler/js_backend.py` | JavaScript backend |
| `compiler/python_backend.py`, `compiler/import_python.py` | Python transpilation and interoperability |
| `compiler/android_backend.py`, `android-studio/` | Experimental Android target work |
| `tests/conformance/`, `tools/conformance.py` | Canonical fixtures and reference/native behavior checks |

## Library and PusingCuk AI

| Path | Responsibility |
|---|---|
| `library/stdlib.py` | Built-ins for the reference execution path |
| `library/builtin_contract.json`, `builtin_contract.py` | Machine-readable built-in contract and target-support metadata |
| `library/kosakata.json` | Machine-readable keyword and alias registry |
| `library/assistant.py`, `library/ai_tools.py` | Assistant orchestration and compiler-facing tools |
| `library/knowledge_grounding.py`, `library/knowledge_index.json` | Curated project knowledge retrieval |
| `library/*_provider.py` | Model-provider adapters |
| `library/ai_service.py` | Authenticated loopback-only local integration service |

## Evidence and documentation

| Path | Responsibility |
|---|---|
| `tests/` | Unit and integration tests |
| `tests/conformance/manifest.json` | Canonical fixture identifiers, expected behavior, and target requirements |
| `tools/conformance.py` | Reference/native conformance runner |
| `tools/reality_engine.py` | Matrix, compatibility snapshot, and score generation/checking |
| `compiler/repair_loop.py` | Provider-neutral AI repair-loop core; production callbacks are not yet integrated |
| `docs/COMPATIBILITY.md` | Generated reference/native C compatibility snapshot |
| `docs/PROJECT_STATUS_AND_ROADMAP.md` | Current status summary and engineering priorities |

## Change discipline

When a language-visible behavior changes, update the relevant specification or semantic contract, implementation, canonical fixture, and target-specific test together. Update the built-in contract and user-facing library documentation when built-in behavior or support metadata changes. Do not add a second fixture catalogue when an existing manifest can represent the case.

A backend file, generated artifact, passing isolated unit test, or AI-generated program does not establish full compatibility or production readiness. Cite evidence from the same commit when making a support claim.
