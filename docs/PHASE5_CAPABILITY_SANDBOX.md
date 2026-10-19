# Phase 5 — Capability Sandbox (VM-level, honest scope)

**Status: foundation only; not yet an end-to-end sandbox.**

## Security boundary

This phase adds a default-deny capability policy and VM resource-budget primitives. These are guardrails inside the language runtime, **not an operating-system sandbox** and not a security guarantee for hostile code. The Python process, imported modules, host libraries, and interpreter remain outside a hard isolation boundary.

For untrusted programs, run the VM inside a separately configured container or equivalent isolation boundary; consider seccomp and/or a WASM runtime with an explicit capability model. Do not run hostile code with valuable host credentials or broad filesystem access.

## Capabilities

The policy recognizes explicit grants:

- `baca:./data` — read access rooted under the selected directory.
- `tulis:./output` — write access rooted under the selected directory.
- `jaringan:api.example` — a named network target.
- `proses:tool-name` — a named process target.
- `env:LANG` — one named environment variable.

No grants are present by default. Grants are exact for network, process, and environment targets. File targets are resolved before checking containment so a path that escapes the granted root (including through a symlink) is rejected. A permission string does not itself perform I/O: an operation must explicitly call the policy before opening a file, connecting to a host, spawning a process, or reading environment data. The current bytecode VM does not expose these host operations as language built-ins, so Phase 5 must not imply they are already integrated.

## Resource budgets

The resource primitive supports:
- fuel: maximum VM instruction ticks;
- elapsed-time deadline checked at VM ticks;
- approximate accounting for VM-visible Python objects.

The memory estimate is not a hard RSS limit: it does not include all interpreter/native allocations and cannot reliably stop a single expensive host call. A hard time or memory ceiling requires an external supervisor/OS boundary. Integration into each VM execution loop and negative integration tests are still required.

## Completion gates

- [ ] Wire the policy into every host-capability entry point in each claimed VM target.
- [ ] Add CLI flags for per-run grants and fuel/memory/time limits.
- [ ] Enforce path containment and document permission syntax.
- [ ] Negative tests: denied file/network/process/env operations, path traversal, symlink escape, malformed permission, fuel exhaustion, time exhaustion, and memory-budget exhaustion.
- [ ] Run the negative tests in CI and publish the exact supported target(s).
- [ ] Keep the OS-sandbox warning visible in user-facing security documentation.

Until these gates pass, label Phase 5 **in progress** and do not claim the VM safely executes arbitrary untrusted code.
