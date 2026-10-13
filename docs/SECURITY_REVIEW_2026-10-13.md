# Security review — 2026-10-13

Scope: historical source and workflow review of the pre-hardening baseline (2026-10-13). The PVM findings below are the original issue statement; current mitigations and limits are documented in `SECURITY.md` and `docs/PVM_SPEC.md`. This is not a penetration test, account audit, or security certification.

**Required warning:** Eksekusi PusingCuk tidak ter-sandbox OS. Jangan jalankan kode tidak terpercaya. Compilation, bytecode validation, loopback binding, and timeouts do not provide operating-system isolation.

## Relevant controls in the reviewed main snapshot

- Added a static local module resolver with explicit exports, project-root path checks, cycle detection, and source/module/depth limits for compiler CLI targets.
- Added a SQLite adapter that confines its database file to a workspace and denies ATTACH/DETACH, PRAGMA, virtual-table operations, and selected file/extension functions.
- Added a JSON HTTP server that binds only to a loopback IP and caps request-body size.
- Added a deterministic blockchain mock and a JSON-RPC adapter restricted to literal loopback HTTP endpoints, with redirects and proxy environment variables disabled.
- Reduced GitHub Pages workflow permissions: build has read-only permissions, deploy receives pages write and OIDC permissions only, and pull requests do not deploy.

## Findings that remain

### High — PVM file access requires explicit controls

The original baseline did not gate PVM file operations or confine filesystem access reliably. The remediation now disables file opcodes in the JavaScript backend and requires the generated Python runtime to receive `--allow-file-io`; the enabled Python implementation uses a pinned root descriptor plus POSIX descriptor-relative no-follow operations. Negative tests cover default denial, absolute/traversal paths, symlink components, deletion, and current-working-directory changes.

This is a source-level mitigation, not independent proof that PVM is a safe sandbox. Do not run untrusted bytecode. Keep issue #75 open until a reviewer has examined the final changes and remaining OS-boundary requirements.

### High — native execution is not isolated

The native runtime and local workbench execute code with the permissions of the current user. The workbench uses loopback binding, input-size limits, a timeout, a temporary working directory, and an Origin check, but those controls do not turn a native process into a sandbox. Avoid exposing the workbench to a network and do not treat it as a safe public code runner.

Required before public multi-user execution: a dedicated low-privilege account/container or OS sandbox, read-only filesystem by default, restricted syscalls/network, resource limits, and independent testing.

### Supply-chain pinning — branch snapshot vs current main

The offline-adapter branch snapshot reviewed when this note was first written used version tags rather than immutable commit SHAs. During the current-main audit, all `uses:` entries in `.github/workflows/build-test.yml`, `pages.yml`, `release.yml`, and `tests.yml` were found pinned to full commit SHAs, with human-readable version comments. The older tag-pinning note is therefore not a current-main finding. Keep SHA pinning and periodically review Dependabot updates; this source review does not validate the contents of each action commit.

### Out of scope

This review cannot confirm GitHub account security settings, organization rulesets, installed Apps, secret rotation, branch protection, deployment environment approvals, or compromise history. Those require owner-side checks. Repository code alone cannot prevent an attacker who has control of the owner's GitHub account or device.

## Cleanup result

The reviewed tracked tree contained no obvious committed Python cache directories, compiled cache files, generated native binaries, build/dist output, or credential files. Existing ignore rules cover common caches, build artifacts, local environment files, and key files. Legacy material under archive/legacy is retained because it is explicitly archived history, not an active cache. No issue or pull request was created.

## Verification

The GitHub Actions test workflow completed successfully for the baseline snapshot documented by this report. Subsequent hardening requires its own CI result and independent review. CI success proves only the behavior covered by tests; it does not certify that Pusingcuk is immune to attacks.
