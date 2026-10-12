# Pusingcuk Security Policy

## Reporting a vulnerability

Do not publish an unpatched vulnerability, an exploit, access tokens, passwords, personal data, or code that could put users at risk in a public issue.

If **Report a vulnerability** is available on this repository's GitHub Security tab, use that private reporting channel. If it is unavailable, contact the repository owner through their GitHub profile and ask for a private reporting channel before sending technical details.

Include the affected version or commit, platform, minimal reproduction steps, expected impact, and any temporary mitigation. Do not send active secrets; revoke or rotate credentials that may have been exposed.

## Security scope and limitations

Pusingcuk is experimental. The native runtime, Pusingcuk Studio, and PVM backends are **not security sandboxes**. Do not use them to run untrusted code on a device that contains sensitive data or accounts.

The PVM JavaScript backend now parses expressions with a restricted grammar instead of dynamically compiling expressions, and the PVM backend accepts only local `data:text/plain,` payloads while rejecting external network URLs. The PVM Python backend now uses a restricted AST evaluator and also rejects the network opcode. Neither backend requires an API key or makes an outbound network request as part of normal expression evaluation.

**Important remaining limitation:** PVM still includes file-operation opcodes. File paths are not confined by an operating-system sandbox, and resource limits are not a general security boundary. A program or bytecode file from an untrusted source may still read, modify, or delete accessible files. Do not treat PVM bytecode as a safe distribution format.

Existing tracking item: [#75](https://github.com/rllibo833-sudo/pusingcuk/issues/75). Do not create a duplicate public issue for the same finding.

Relevant reports include unintended code execution, unauthorized file access, path traversal or symlink escape, credential exposure, memory corruption, resource-limit bypasses, and CI workflows that expose tokens or run untrusted code with excessive permissions.

## Release security gates

- [ ] Expression evaluation uses a restricted parser/evaluator; it does not use dynamic code compilation as a security boundary.
- [ ] External network operations are disabled and tests confirm that network URLs are rejected; local `data:text/plain,` payloads remain supported.
- [ ] File operations are either removed, explicitly capability-gated, or confined by operating-system isolation before untrusted programs are supported.
- [ ] Negative tests cover host-global access, constructor/prototype escape, path traversal, symlink escape, and attempts to reach the network.
- [ ] Input size, payload size, execution time, and resource usage limits are tested.
- [ ] CI receives only the permissions and secrets it needs.

## Supported versions

The latest development version on `main` is the primary focus for fixes. No security support is promised for older releases or pre-release versions. Fix status and advisories will be published when mitigations are available.
