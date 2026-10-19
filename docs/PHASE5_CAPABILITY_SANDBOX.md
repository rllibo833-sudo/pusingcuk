# Phase 5 — Capability Policy and VM Resource Budgets

**Status: partially implemented.** The current work provides a default-deny capability policy and VM-level resource-budget hooks. It does not provide an operating-system sandbox or safe execution of hostile programs.

## Security boundary

The Python process, native libraries, imported modules, and host operations remain outside a hard isolation boundary. Do not run untrusted programs with valuable credentials or broad host access. Use a separately configured OS/container boundary for hostile code.

## Capability policy

The policy recognizes explicit grants:

- `baca:./data` — read access rooted under the selected directory.
- `tulis:./output` — write access rooted under the selected directory.
- `jaringan:api.example` — a named network target.
- `proses:tool-name` — a named process target.
- `env:LANG` — one named environment variable.

No grants are present by default. Network, process, and environment grants use exact targets. File paths are resolved before containment checks, including checks against path traversal and symlink escapes.

**Important limitation:** a grant string is policy data, not an I/O operation. The current bytecode VM does not expose file, network, process, or environment access as language built-ins, so these grants do not enable or mediate those operations. Any future host-capability entry point must call the policy before performing the operation.

## VM resource budgets

The bytecode VM accepts per-run controls:

- `--fuel 100000` — maximum VM instruction ticks.
- `--memori-byte 16777216` — approximate accounting for VM-visible Python objects.
- `--waktu-detik 2` — elapsed-time deadline checked at VM instruction ticks.
- Repeatable `--izin=baca:./data` or another supported grant string.

Example:

```sh
python -m compiler.vm --fuel 50000 --memori-byte 8388608 --waktu-detik 1.5 --izin=baca:./data program.bytecode.json
```

These are runtime guardrails, not hard OS-level limits. Memory accounting does not include every interpreter/native allocation, and a time check cannot interrupt an expensive host call between VM ticks.

## Evidence and remaining gates

Implemented and covered by the current Phase 5 test suite: policy decisions, exact targets, path containment checks, symlink-escape rejection, and VM-level fuel/memory budget behavior.

Still incomplete: capability mediation for actual host operations, hard resource isolation, and a security guarantee for arbitrary untrusted code. Do not describe the VM as a secure sandbox.

The CI workflow on `cuk-reality-engine` runs the sandbox tests. The result proves only the tested contracts on that commit; it does not change the security boundary above.
