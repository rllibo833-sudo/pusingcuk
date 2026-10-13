# Contributing to Pusingcuk

**Canonical language version:** `0.4-dev`. New source examples use `.cuk`; legacy `.pusingcuk` files remain valid compatibility fixtures.

Start with the [project vision and community principles](docs/VISION.md). Pusingcuk welcomes code and non-code contributions; technical changes must still be tested and reviewed.

Thank you for helping develop Pusingcuk. The project aims to be easy for beginners, technically extensible by independent communities, and increasingly capable of running natively without Python at runtime.

## Community and extension principles

Pusingcuk is not tied to one company, school, or community. Contributors from Ecoslang.org and other programming-language, education, open-source, and developer communities are welcome to study the implementation, build compatible tooling, propose libraries, and develop new compiler targets.

1. **One change, one clear purpose.** Keep changes small enough to review and explain.
2. **The specification is the shared contract.** Do not silently change language semantics in one backend only.
3. **Offline-first by default.** Do not add `os.system`, Python `eval` or `exec`, `requests`, OpenAI SDK dependencies, API-key requirements, or automatic outbound network connections to the core runtime.
4. **No secrets in source.** Never commit API keys, tokens, passwords, private user data, local databases, build outputs, caches, or backups.
5. **State support honestly.** Do not claim native support based only on the Python interpreter. Do not claim cross-runtime or cross-platform compatibility without the relevant conformance tests.
6. **Keep the core open to extensions.** New backends and platform integrations should use the documented IR/semantic contracts where practical, declare their supported feature subset, and remain optional rather than making the core depend on a hosted service.
7. **Security boundaries must be real.** Generated code and a virtual machine are not automatically a sandbox. File, process, database, and network access must be explicit and tested.
8. **Respect repository history.** Do not force-push `main`, rewrite shared history, or delete a branch before checking whether it contains unique work.

## Where to start

- Learn how to use the language: [beginner guide](docs/PEMULA.md) and [Termux quick start](docs/termux/README.md)
- Find keywords, aliases, and built-ins: [language-reference map](docs/language/README.md)
- Understand the implementation boundary: [semantic contract](docs/SEMANTIC_CONTRACT.md) and [compatibility matrix](docs/COMPATIBILITY.md)
- Review the native subset: [native runtime guide](docs/NATIVE_RUNTIME.md)
- Understand security limits: [SECURITY.md](SECURITY.md) and [security review guide](docs/security/README.md)
- Find test commands and support rules: [development gates](docs/development/README.md)

## Test gates

For changes to the Python reference interpreter:

```sh
python -m unittest discover -s tests -v
```

For changes to the native C runtime or any behavior that claims Python/C parity:

```sh
make test-native
python tools/conformance.py
```

The maintained CI baseline tests Python 3.11/3.12 and native C with GCC/Clang. The main test workflow also checks the PVM file-capability boundary using `bash tests/test_all.sh`; generated Python PVM file operations require `--allow-file-io` for trusted bytecode, and JavaScript PVM file operations are disabled. For Android/Termux device claims, run `bash scripts/test-termux-device.sh` on real hardware and record the result. A cross-runtime feature must have a fixture that requires both `reference` and `native`; tests that mark a runtime unsupported do not prove parity. The contract for language-source errors is exit code `2` for syntax and `1` for runtime failures; the source-absent CLI case uses `3`.

Compiler/PVM prototypes and Android Studio APK development are intentionally outside the baseline. They remain available through manual workflows and should only be changed with explicit scope and relevant checks. Physical Termux testing is needed for claims about actual Android devices; Ubuntu CI alone is not sufficient.

## Contributor checklist

- [ ] The change has a clear purpose and stays within scope.
- [ ] Success cases and relevant failure cases have tests.
- [ ] `SPEC.md`, the semantic contract, built-in metadata, tests, and documentation agree with the implementation.
- [ ] Built-in changes update `library/builtin_contract.json`, `docs/language/BUILTINS.md`, runtime support states, and executable tests together.
- [ ] A new native built-in has parity fixtures for normal and fractional results, wrong arity, invalid types, domain failures, and overflow/non-finite results when applicable; assert Python/C stdout and source-line error parity.
- [ ] Trigonometric built-ins specify radians, finite/non-boolean arguments, canonical integral results, and representative fractional outputs.
- [ ] Statistical built-ins cover empty lists, booleans/non-numeric elements, singleton/cancellation cases, odd/even median, negative and duplicated values, fractional outputs, and inclusive/exclusive safe-integer boundaries in Python and C.
- [ ] Aggregate built-ins such as `jumlah` define empty-list behavior, ordered accumulation, input and result range rules, non-finite handling, arity/type failures, and exact Python/C stdout parity.
- [ ] Repository cleanup preserves useful compatibility examples and historical experiments; remove build/cache artifacts and relocate redundant root examples only when their intent remains discoverable.
- [ ] Numeric built-ins define accepted types, edge/domain rules, and canonical formatting of integral versus fractional results in both `SPEC.md` and `docs/SEMANTIC_CONTRACT.md`.
- [ ] Error fixtures compare syntax/runtime class, shared exit code, and source line; do not add per-runtime exit-code overrides to hide a mismatch.
- [ ] Runtime parity is claimed only when the same conformance fixtures pass.
- [ ] Platform claims match the tested compatibility matrix.
- [ ] No secrets, personal data, caches, binaries, or backups are included.
- [ ] Error messages are useful and do not leak secrets.
- [ ] Test commands, results, and untested limitations are recorded accurately.
- [ ] New integrations are optional and do not introduce outbound network calls into core execution.

## Git history and review

Use clear commit messages, such as `feat(native): add module imports` or `docs: improve Termux quickstart`. Group related changes rather than creating a commit for every tiny edit. The repository owner reviews changes before merging. Squash-and-merge is suitable for an approved pull request when it preserves a readable history.

Do not rewrite shared history or delete old branches just because they look stale. Verify whether they contain unique work first. Historical code under `archive/legacy/` is retained for reference and is not the recommended starting point for new features.
