# Security Review Guide

This page organizes security review topics. The official policy and vulnerability-reporting instructions remain in the repository-root [`SECURITY.md`](../../SECURITY.md). Use GitHub's private vulnerability-reporting feature for an unpatched vulnerability; do not publish secrets or a weaponizable report in a public issue.

## Security boundary at a glance

Pusingcuk is experimental and does not provide a general-purpose operating-system sandbox.

| Component | What must not be assumed |
|---|---|
| Python reference interpreter | A URL/address filter in the evaluator is not proof that every network path, redirect, or host interaction is safe. |
| Native C runtime | Resource/loop limits do not isolate file access, memory, or host permissions. |
| PVM and experimental backends | Restricted expression parsing does not make file operations safe or confine them to an OS sandbox. |
| Compiler output and Android Studio prototype | Generated code and an editor are not security boundaries. |

Always verify the exact entry point and target being reviewed. Security behavior in the Python evaluator must not be credited to the native runtime, PVM, or generated code unless those paths have their own implementation and regression tests.

## What a review should cover

1. **Execution boundary:** Does the change invoke a shell, dynamic code execution, a subprocess, or a hidden network connection?
2. **Filesystem:** Can untrusted input escape a project root through absolute paths, traversal, symbolic links, or race conditions?
3. **Network:** Are schemes, DNS results, redirects, payload sizes, timeouts, and failure cases handled explicitly?
4. **Parser and runtime:** Are malformed input, recursion, allocation limits, overflow, and invalid types rejected without corrupting state?
5. **Data and credentials:** Are tokens, personal information, local databases, and build outputs excluded from source control and logs?
6. **CI workflow:** Are permissions minimal, third-party Actions pinned to reviewed revisions, untrusted PR code handled safely, and release artifacts checked before publication?
7. **Claims:** Does the documentation describe precisely which runtime was tested, rather than implying a universal sandbox or SSRF guarantee?

## Regression commands

Run the broad tests first, then focus on the affected boundary:

```sh
python -m unittest discover -s tests -v
make test-native
python tools/conformance.py
python -m unittest discover -s tests -p 'test_level6_ssrf.py' -v
```

Only the relevant command may be needed for a narrow change, but a security-sensitive patch must include a repeatable regression test. Do not claim a finding is fixed until the test reproduces the old behavior and passes against the patched implementation.

## Security notes and audits

- [Official security policy](../../SECURITY.md) is authoritative for reporting and current limitations.
- [Native runtime scope](../NATIVE_RUNTIME.md) describes C-specific limits.
- [Semantic contract](../SEMANTIC_CONTRACT.md) defines language/runtime behavior.
- [Dated native audit](../NATIVE_AUDIT_2026-10-11.md) is a point-in-time engineering note, not a certification and not a substitute for checking current source.

## Keep the repository clean

Do not commit `__pycache__`, test caches, coverage output, build directories, wheel metadata, compiled binaries, Gradle output, local credentials, or backup snapshots. These are ignored by `.gitignore`; review `git status --short` before committing. Workflow caches and artifacts are GitHub-side resources, not files that should be added to the repository.


PVM file operations reject absolute paths, parent traversal, and symlink components outside the execution working directory. These checks are defense in depth, not an OS sandbox; untrusted bytecode still requires OS-level isolation.
