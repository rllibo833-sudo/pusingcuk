# Pusingcuk Security Policy

## Reporting a vulnerability

**Private vulnerability reporting is enabled for this repository.** Use **Report a vulnerability** in the repository's GitHub Security tab. Do not publish an unpatched vulnerability, an exploit, access tokens, passwords, personal data, or code that could put users at risk in a public issue.

Include the affected version or commit, platform, minimal reproduction steps, expected impact, and any temporary mitigation. Do not send active secrets; revoke or rotate credentials that may have been exposed.

## Security scope and limitations

**Pusingcuk is experimental. No component is claimed to be SSRF-proof, and PVM/native are not security sandboxes. Do not run untrusted code.** Runtimes generally execute with the permissions available to the current process; file operations may reach accessible files.

### SSRF protection scope

The current SSRF address filtering and fail-closed DNS-resolution behavior are implemented in `evaluator.py` for the **Python interpreter only**. Do not assume the same protection applies to PVM, the native runtime, compiler output, Studio/workbench, or other entry points. These paths have not been established as protected by this evaluator logic.

For the Python interpreter's URL/IP check, the documented behavior is:

| Destination / condition | Result |
| --- | --- |
| `127.0.0.0/8` (IPv4 loopback) | Blocked |
| `10.0.0.0/8` (private IPv4) | Blocked |
| `172.16.0.0/12` (private IPv4) | Blocked |
| `192.168.0.0/16` (private IPv4) | Blocked |
| `fc00::/7` (IPv6 unique-local) | Blocked |
| `fe80::/10` (IPv6 link-local) | Blocked |
| `::1` (IPv6 loopback) | Blocked |
| Public IP address | Allowed by this address filter |
| DNS resolution fails | Blocked (fail-closed) |

This table describes the Python interpreter's current filter, not a universal network policy or proof that all SSRF paths are eliminated. Public destinations may still be risky, and this behavior does not guarantee protection against every redirect, proxy, resolver, parsing, or time-of-check/time-of-use issue. Keep the runtime and dependencies updated and do not treat this as a sandbox.

### Other runtime limitations

The PVM JavaScript backend parses expressions with a restricted grammar instead of dynamically compiling expressions. PVM backends have other restrictions, but they do **not** inherit the Python interpreter's SSRF filtering simply by being PVM. The native runtime and PVM backends are not security sandboxes.

**Important remaining limitation:** PVM still includes file-operation opcodes. File paths are not confined by an operating-system sandbox, and resource limits are not a general security boundary. A program or bytecode file from an untrusted source may still read, modify, or delete accessible files. Do not treat PVM bytecode as a safe distribution format.

### Evidence and regression coverage

Commit [`8ab6a5c`](https://github.com/rllibo833-sudo/pusingcuk/commit/8ab6a5c2824fbafe7c30530173707cf54cc67a35) added DNS-rebinding/IPv6 ULA hardening in `evaluator.py` and the SSRF regression test file `tests/test_level6_ssrf.py`, with six regression tests. This is evidence for that implementation and test coverage only; it is not a claim of comprehensive SSRF protection across the project.

Existing tracking item: [#75](https://github.com/rllibo833-sudo/pusingcuk/issues/75). Do not create a duplicate public issue for the same finding.

Relevant reports include unintended code execution, unauthorized file access, path traversal or symlink escape, credential exposure, memory corruption, resource-limit bypasses, and CI workflows that expose tokens or run untrusted code with excessive permissions.

## Release security gates

- [ ] Clearly scope and test SSRF protections for every supported entry point; do not describe the project as SSRF-proof.
- [ ] Expression evaluation uses a restricted parser/evaluator; it does not use dynamic code compilation as a security boundary.
- [ ] Network behavior is explicitly documented and tested for each backend; Python interpreter filtering must not be assumed for PVM/native.
- [ ] File operations are removed, explicitly capability-gated, or confined by operating-system isolation before untrusted programs are supported.
- [ ] Negative tests cover host-global access, constructor/prototype escape, path traversal, symlink escape, and attempts to reach the network.
- [ ] Input size, payload size, execution time, and resource usage limits are tested.
- [ ] CI receives only the permissions and secrets it needs.

## Supported versions

The latest development version on `main` is the primary focus for fixes. No security support is promised for older releases or pre-release versions. Fix status and advisories will be published when mitigations are available.
