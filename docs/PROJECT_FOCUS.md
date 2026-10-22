# Project Focus: From Bootstrap to Useful Tools

## Current direction

PusingCuk keeps its language core, native runtime, compiler IR, bootstrap implementation, and reproducibility evidence. The bootstrap is a milestone to preserve—not a reason to keep expanding self-hosting infrastructure indefinitely.

The next development effort should optimize for useful outcomes:

1. **Compiler interoperability:** define clear source/target boundaries and reuse the existing IR and tested runtime paths instead of creating parallel compiler infrastructure.
2. **Terminal applications:** make it straightforward to build practical command-line tools with `.cuk`, with documented input/output, errors, packaging, and platform limits.
3. **Jeklyn exploration:** investigate whether a Jeklyn source frontend could target `.cuk` or a shared IR for terminal applications. This is a proposal only; no Jeklyn compiler or compatibility claim is implied by this document.
4. **Repository maintenance:** keep generated build outputs and local caches out of version control, but preserve source files, canonical fixtures, and bootstrap evidence required to reproduce results.

## Repository hygiene rules

- `.gitignore` prevents new untracked local files from being added accidentally; it does not untrack files already committed.
- Do not delete root-level `ir_*.json` files or move them until their consumers, workflows, and regeneration commands have been verified. A large generated-looking JSON file may still be a required fixture or bootstrap input.
- Keep canonical conformance manifests and intentional baseline data versioned. Treat ephemeral reports and local caches as regenerable only when CI can recreate them.
- Keep the bootstrap source, native seed, scripts, tests, and status documentation. Retire redundant notes only after their unique information is consolidated.
- Keep `main` as the stable integration branch. Retain the bootstrap PR branch until its changes are merged or otherwise preserved; do not delete a branch solely because its name contains `selfhost` or `bootstrap`.

## Acceptance for the next compiler project

Before implementing Jeklyn interop, record a minimal source example, expected terminal behavior, compilation target, IR boundary (if any), and unsupported cases. Then prove the smallest end-to-end path with a reproducible command and tests. Avoid adding a new runtime, manifest, or framework unless the chosen design needs it.
