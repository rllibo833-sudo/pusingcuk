# Contributing to Pusingcuk

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

- Learn the language: [`SPEC.md`](SPEC.md)
- Learn terms and features: [English dictionary](docs/DICTIONARY.md) and [Indonesian plain-language dictionary](docs/KAMUS_PUSINGCUK.md)
- Understand runtime differences: [compatibility matrix](docs/COMPATIBILITY.md)
- Learn the compiler architecture: [compiler interoperability](docs/COMPILER_INTEROP.md) and [IR v1](docs/IR_V1.md)
- Review native support: [native runtime matrix](docs/NATIVE_RUNTIME.md)
- Understand security limitations: [`SECURITY.md`](SECURITY.md)

## Branch naming

Use a descriptive branch name:

- `feat/<short-feature>` — a language capability or new feature.
- `fix/<short-problem>` — a bug fix.
- `test/<short-scope>` — tests only.
- `docs/<short-topic>` — documentation or tutorials.
- `audit/<short-topic>` — findings that do not intentionally change behavior.
- `refactor/<short-topic>` — restructuring without intended behavior changes.

Avoid vague names such as `update`, `new-feature`, or `final-fix`. Do not repurpose another contributor's experimental branch without checking its purpose.

## Before making changes

From a clean working directory:

```sh
git switch main
git pull --ff-only
git status --short
git switch -c docs/short-topic
```

If `git status --short` shows changes you do not understand, stop and inspect them before switching branches. Do not automatically delete or overwrite a user's local changes.

## Test gates

For changes to the modular language implementation:

```sh
python -m unittest discover -s tests -v
```

For changes to the native runtime:

```sh
make test-native
```

If a change affects both implementations, test both. Run the compiler and conformance checks when those paths are affected:

```sh
python tools/conformance.py
python -m compiler examples/halo.pusingcuk --target js --output /tmp/halo.js
```

CI must pass on the final revision before a change is considered verified. Physical Termux testing is still required for claims about actual Android devices; Ubuntu CI is not a substitute for Android testing.

## Contributor checklist

- [ ] The change has a clear purpose and stays within scope.
- [ ] Success cases and relevant failure cases have tests.
- [ ] `SPEC.md`, tests, and documentation agree with the implementation.
- [ ] Runtime parity is claimed only when the same conformance fixtures pass.
- [ ] Platform claims match the tested compatibility matrix.
- [ ] No secrets, personal data, caches, binaries, or backups are included.
- [ ] Error messages are useful and do not leak secrets.
- [ ] Test commands, results, and untested limitations are recorded accurately.
- [ ] New integrations are optional and do not introduce outbound network calls into core execution.

## Git history and review

Use clear commit messages, such as `feat(native): add module imports` or `docs: improve Termux quickstart`. Group related changes rather than creating a commit for every tiny edit. The repository owner reviews changes before merging. Squash-and-merge is suitable for an approved pull request when it preserves a readable history.

Do not rewrite shared history or delete old branches just because they look stale. Verify whether they contain unique work first. Historical code under `archive/legacy/` is retained for reference and is not the recommended starting point for new features.
