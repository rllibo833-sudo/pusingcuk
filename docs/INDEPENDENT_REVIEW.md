# Independent Technical Review Guide

Thank you for taking a look at Pusingcuk. This guide is for independent compiler, runtime, testing, and security reviewers. The project is experimental; the goal is to identify concrete weaknesses and improve the evidence for its current behavior, not to claim production readiness.

## Project snapshot

- **Reference path:** modular Python interpreter and its tests.
- **Native path:** experimental C runtime supporting a documented subset.
- **Compiler paths:** versioned IR and experimental C/JavaScript/HTML targets with feature-specific limits.
- **Security posture:** not a sandbox. In particular, PVM file operations are not confined by an operating-system sandbox.
- **Network policy:** core execution is intended to work offline; reviewers should verify this from source and tests rather than infer it from documentation alone.

Start with [README.md](../README.md), [SPEC.md](../SPEC.md), [compatibility matrix](COMPATIBILITY.md), [semantic contract](SEMANTIC_CONTRACT.md), [native runtime notes](NATIVE_RUNTIME.md), and [SECURITY.md](../SECURITY.md).

## Suggested checks

Run from a clean checkout using the tools available on your platform.

### Python reference tests

~~~sh
python -m unittest discover -s tests -v
~~~

### Native C runtime and conformance

Requires a C compiler and Make:

~~~sh
make test-native
python tools/conformance.py
~~~

### PVM backend tests

Requires Bash and Node.js:

~~~sh
bash tests/test_all.sh
~~~

The CI workflow also tests Python 3.11/3.12 and native builds with GCC/Clang. These hosted jobs do not prove the program has been tested on a physical Android/Termux device. Check the latest [GitHub Actions runs](https://github.com/rllibo833-sudo/pusingcuk/actions) for the exact commit and result.

## Review priorities

1. **Semantic consistency:** operator precedence, short-circuit behavior, scope, return values, list/dictionary equality, Unicode/indexing, and numeric edge cases.
2. **Error handling:** malformed input, invalid bytecode, clear diagnostics, and nonzero exit codes on failure.
3. **Runtime parity:** verify that a feature marked supported actually passes the same fixture on each runtime that claims support. An explicit unsupported result is preferable to silent divergence.
4. **Security boundaries:** expression parser escapes, host-global access, path traversal and symlink escape, filesystem capabilities, network opcodes, resource exhaustion, and CI permissions.
5. **Documentation accuracy:** installation commands, paths, support labels, test evidence, and claims about Android or native execution.
6. **Maintainability:** duplicated implementation paths, test discoverability, module boundaries, and whether a small change can be verified without hidden setup.

## How to send useful findings

For each finding, please include:

- A short title and affected file/component.
- The exact commit SHA or branch reviewed.
- Environment details (OS, compiler/interpreter version).
- Minimal reproduction steps and actual versus expected behavior.
- Impact and severity rationale.
- A proposed test or mitigation, if known.

For security findings, do **not** publish exploit details or sensitive data in a public issue. Follow the private reporting guidance in [SECURITY.md](../SECURITY.md). For ordinary documentation or test feedback, use the repository's existing relevant issue when appropriate or contact the maintainer at **pusingcukdevprog@gmail.com**. Please avoid duplicate issues.

## Important limitations

- A passing test suite covers only the cases it exercises; it is not proof of full language correctness.
- A successful native build does not establish full parity with the Python interpreter.
- CI on Ubuntu does not establish physical Termux or Android runtime behavior.
- PVM and native execution are not safe sandboxes for untrusted programs.
- Database adapters, stable FFI/ABI, WebAssembly, and broader ecosystem integrations are roadmap items unless current code and tests demonstrate otherwise.

Please be direct and critical. Reproducible counterexamples are more valuable than broad claims of safety or completeness.
