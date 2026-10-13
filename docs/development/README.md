# Development and Test Gates

The maintained development baseline is the Python reference interpreter plus the native C runtime. The goal is predictable behavior and explicit support boundaries, not the largest number of active compiler targets.

## Core checks

From the repository root, run:

```sh
python -m unittest discover -s tests -v
make test-native
python tools/conformance.py
```

- The Python unit suite should pass on the supported Python versions (3.11 and 3.12 are tested in CI).
- `make test-native` builds and checks the native C runtime. CI uses GCC and Clang.
- `tools/conformance.py` runs common source fixtures on the Python reference and native C runtime. The manifest declares which result each runtime is required to support.

The package/CLI and PyInstaller smoke check runs in [`build-test.yml`](../../.github/workflows/build-test.yml). The primary language and parity checks run in [`tests.yml`](../../.github/workflows/tests.yml).

## The language-consistency rule

For a change that affects externally visible language behavior:

1. Update `SPEC.md` and [the semantic contract](../SEMANTIC_CONTRACT.md).
2. Keep Python tokenization, parsing, evaluation, and official alias mappings aligned.
3. Update native C behavior when the feature is claimed for native support.
4. Update the vocabulary/built-in registry where metadata changes.
5. Add a positive fixture and a failure/boundary fixture where applicable.
6. For Python/C parity, mark both runtimes `required` in the manifest and compare exit code, stdout, and error class.
7. Run the commands above and wait for CI to pass before claiming the feature is verified.

A fixture marked `unsupported` records a known limit; it is not a passing parity result. A feature tested only in Python is still useful, but it must be described as reference-only.

## Experimental work

Transpiler backends, PVM, and Android Studio APK generation are outside the required baseline for this phase. Their source is retained. Use the manual workflows only when changing or validating those experiments:

- [Experimental PVM workflow](../../.github/workflows/experimental-pvm.yml)
- [Android Studio APK workflow](../../.github/workflows/android-studio-apk.yml)
- [Android emulator smoke-test workflow](../../.github/workflows/android-emulator-smoke.yml)

Building the standalone C runtime for Termux is separate from building an Android application. Actual device claims still require testing on a physical Termux ARM64 device.

## Repository hygiene

Before submitting a change:

```sh
git diff --check
git status --short
```

Do not commit generated binaries, caches, coverage reports, package build output, credentials, or local backups. Keep changes focused, and never delete historical/experimental files solely because they are not part of the current priority.
