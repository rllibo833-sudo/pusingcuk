# Security review — 2026-10-13

Scope: repository source and workflow review at the offline-adapter work branch. This is a source-level engineering review, not a penetration test, account audit, or security certification.

## Changes in this branch

- Added a static local module resolver with explicit exports, project-root path checks, cycle detection, and source/module/depth limits for compiler CLI targets.
- Added a SQLite adapter that confines its database file to a workspace and denies ATTACH/DETACH, PRAGMA, virtual-table operations, and selected file/extension functions.
- Added a JSON HTTP server that binds only to a loopback IP and caps request-body size.
- Added a deterministic blockchain mock and a JSON-RPC adapter restricted to literal loopback HTTP endpoints, with redirects and proxy environment variables disabled.
- Reduced GitHub Pages workflow permissions: build has read-only permissions, deploy receives pages write and OIDC permissions only, and pull requests do not deploy.

## Findings that remain

### High — PVM file access is not a sandbox

PVM v1 includes file open/read/delete opcodes. The current design does not reliably confine those paths to a project directory or use an OS sandbox. A malicious PVM program can potentially read or delete files that the current operating-system user can access. Do not run bytecode or programs from untrusted sources on a device with valuable files or credentials. This was already documented in SECURITY.md and associated with existing issue #75; this review does not create a duplicate issue.

Required before claiming support for untrusted programs: remove file opcodes from untrusted execution, or enforce explicit capabilities and OS-level filesystem isolation, including symlink/traversal tests.

### High — native execution is not isolated

The native runtime and local workbench execute code with the permissions of the current user. The workbench uses loopback binding, input-size limits, a timeout, a temporary working directory, and an Origin check, but those controls do not turn a native process into a sandbox. Avoid exposing the workbench to a network and do not treat it as a safe public code runner.

Required before public multi-user execution: a dedicated low-privilege account/container or OS sandbox, read-only filesystem by default, restricted syscalls/network, resource limits, and independent testing.

### Medium — supply-chain pinning

Workflow permissions are limited and the test workflow does not use privileged pull-request triggers. However, third-party GitHub Actions are referenced by version tags rather than immutable commit SHAs. Pin actions to reviewed full commit SHAs and automate update review for stronger supply-chain reproducibility.

### Out of scope

This review cannot confirm GitHub account security settings, organization rulesets, installed Apps, secret rotation, branch protection, deployment environment approvals, or compromise history. Those require owner-side checks. Repository code alone cannot prevent an attacker who has control of the owner's GitHub account or device.

## Cleanup result

The reviewed tracked tree contained no obvious committed Python cache directories, compiled cache files, generated native binaries, build/dist output, or credential files. Existing ignore rules cover common caches, build artifacts, local environment files, and key files. Legacy material under archive/legacy is retained because it is explicitly archived history, not an active cache. No issue or pull request was created.

## Verification

The GitHub Actions test workflow completed successfully for the branch commit listed in the execution report. CI success proves only the behavior covered by the tests; it does not close the findings above or guarantee that Pusingcuk is immune to attacks.
