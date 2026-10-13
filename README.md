# Pusingcuk

Pusingcuk is an experimental programming language built around Indonesian-friendly keywords and readable examples. Its near-term goal is not to support every compiler target; it is to make one language behave predictably across its **Python reference interpreter** and **native C runtime**.

**Canonical language version:** `0.4-dev`. New programs use `.cuk`; `.pusingcuk` remains a compatibility extension.

### Runtime capability matrix

| Target | Contracted built-ins | Status |
|---|---:|---|
| Reference Python | 19 | Full contracted built-in set; additional reference-only intrinsics are separate |
| Native C | 15 | Subset; no file I/O, HTTP, or module system |
| JS transpiler | 14 | Subset |
| Python transpiler | 14 | Subset |
| VM | 6 | Experimental |


[![Core CI](https://github.com/rllibo833-sudo/pusingcuk/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/rllibo833-sudo/pusingcuk/actions/workflows/tests.yml)
[![Packaging](https://github.com/rllibo833-sudo/pusingcuk/actions/workflows/build-test.yml/badge.svg?branch=main)](https://github.com/rllibo833-sudo/pusingcuk/actions/workflows/build-test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Status:** experimental. Python defines the reference behavior; native C implements a tested subset. A feature is portable between them only when the same conformance fixture passes on both. Pusingcuk is not a security sandbox.
>
> **Security warning:** Eksekusi PusingCuk tidak ter-sandbox OS. Jangan jalankan kode tidak terpercaya. Execution runs with the current process's operating-system permissions; do not run untrusted code or bytecode.

## Try Pusingcuk on Termux

Install Python and Git, then run the example directly from the source tree:

```sh
pkg update
pkg install python git
git clone https://github.com/rllibo833-sudo/pusingcuk.git
cd pusingcuk
python pusingcuk_new.py halo.cuk
```

The same Python command works on Linux and other systems with Python 3.11 or 3.12 installed. The optional `pusingcuk` CLI can be installed with `python -m pip install .`; see the [Termux guide](docs/termux/README.md) for setup details.

## First program

```cuk
jancuk
lah angka = 40
hedeh angka + 2
selesai jancuk
```

Run it with:

```sh
python pusingcuk_new.py program.cuk
python pusingcuk_new.py --check program.cuk
```

The `.cuk` extension is Pusingcuk's canonical source-file identity for new programs. The distinctive identity comes from its Indonesian-readable syntax and tested language rules—not the suffix alone. Existing `.pusingcuk` files remain supported for compatibility.

The Python package/release version is `0.7.1` (`pyproject.toml`, `Makefile`); the language contract version is `0.4-dev` (`lexer.py`, `SPEC.md`). These identifiers have different purposes. Use `make version` and `make language-version` to inspect them.

After installing the CLI, run `pusingcuk script.cuk` directly. Executable scripts can start with `#!/usr/bin/env pusingcuk` and use `chmod +x script.cuk`; the CLI must be installed and on `PATH`.

For Linux desktop MIME registration, install `pusingcuk.xml` into `~/.local/share/mime/packages/` and run `update-mime-database ~/.local/share/mime`. MIME registration is a desktop/Linux facility; Termux shell execution uses the shebang and `PATH`.

## Two maintained execution paths

| Path | What it is | Important limit |
|---|---|---|
| Python reference | The modular interpreter launched by `pusingcuk_new.py`; reference for language behavior | Requires Python; host file/network capabilities are not a sandbox |
| Native C | A standalone C11 runtime built with GCC or Clang; no Python needed at runtime | Fifteen built-ins are verified, including trigonometry, summation, and statistics, alongside arithmetic, collection, scope, numeric-domain, and error fixtures; the native module system is not available |

For the native C runtime on Termux:

```sh
pkg install git clang make
bash scripts/install-termux.sh
pusingcuk-native examples/rekap_anggaran.cuk
```

The native runtime and its limits are documented in the [native runtime guide](docs/NATIVE_RUNTIME.md). The existing Linux `pusingcuk` release asset is not a Termux ARM64 binary. Choose an explicitly named Android ARM64 native asset when available, or build from source; physical Termux device compatibility must not be inferred from Ubuntu CI alone.

## Documentation map

- **Start and learn:** [Beginner guide](docs/PEMULA.md) · [Termux quick start](docs/termux/README.md)
- **Language reference and dictionary:** [Language reference index](docs/language/README.md) · [Built-in catalogue](docs/language/BUILTINS.md) · [Syntax specification](SPEC.md) · [English dictionary](docs/DICTIONARY.md) · [Kamus Indonesia](docs/KAMUS_PUSINGCUK.md)
- **Consistency and runtime support:** [Semantic contract](docs/SEMANTIC_CONTRACT.md) · [Compatibility matrix](docs/COMPATIBILITY.md) · [Conformance fixtures](docs/CONFORMANCE_FIXTURES.md)
- **Development:** [Contributor guide](CONTRIBUTING.md) · [Development and test gates](docs/development/README.md) · [Repository map](docs/REPO_STRUCTURE.md)
- **Security:** [Security policy](SECURITY.md) · [Security review guide](docs/security/README.md)
- **Complete documentation index:** [docs/README.md](docs/README.md)

## Quality gates

Run the same checks used by the maintained Python/C baseline:

```sh
python -m unittest discover -s tests -v
make test-native
python tools/conformance.py
python tests/conformance/runner.py
```

CI tests the reference interpreter on Python 3.11 and 3.12 and builds the native runtime with GCC and Clang. The manifest distinguishes required, optional, and unsupported runtime behavior; unsupported features are not counted as parity.

## What is deliberately deferred

Transpiler backends, PVM extensions, and Android Studio APK development are experimental and are not the current compatibility baseline. Existing code and design notes are retained for future work, but their presence does not mean production support. The current priority is to align the specification, vocabulary registry, Python interpreter, native C runtime, and executable conformance tests.

## Security

Do not run code or bytecode from an untrusted source with access to important files, credentials, or accounts. Runtime limits and restricted expression parsers are not operating-system isolation. Read [SECURITY.md](SECURITY.md) before using Pusingcuk in a security-sensitive context.

## License

MIT. See [LICENSE](LICENSE).
