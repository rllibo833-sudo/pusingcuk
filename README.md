# Pusingcuk

Pusingcuk is an experimental programming language with Indonesian-friendly keywords and local slang aliases. The project aims to make programming approachable while building a testable interpreter, a native C runtime, and experimental compiler backends.

> **Project status:** experimental, version 0.4-dev. Runtime and compiler support varies by feature. Pusingcuk is not a security sandbox and must not run untrusted programs on systems containing sensitive data.

## Project vision and community

Pusingcuk is intended as a shared learning and engineering space for beginners, experienced developers, educators, testers, translators, and language communities. Its Gen Z/Gen Alpha-inspired slang is an optional style layer, not a requirement for participation or a claim that one slang vocabulary represents every region or generation.

The project welcomes technical criticism and non-code contributions such as documentation, examples, translations, reproducible bug reports, and test cases. Read the [project vision](docs/VISION.md) for the principles behind this approach.

## Quick start on Android

### Option A: Termux (Python interpreter)

Install the tools once:

```sh
pkg update
pkg install python git
git clone https://github.com/rllibo833-sudo/pusingcuk.git
cd pusingcuk
python pusingcuk_new.py examples/halo.pusingcuk
```

Run your own program:

```sh
python pusingcuk_new.py program.pusingcuk
```

### Option B: Pydroid 3

1. Download or copy the repository into a folder on your phone.
2. Open the folder in Pydroid 3.
3. Open `pusingcuk_new.py` and run it with a source-file argument, or use the Pydroid terminal if available:

```sh
python pusingcuk_new.py examples/halo.pusingcuk
```

The Python interpreter uses the standard library; no API key or third-party Python package is required.

### Option C: Native runtime in Termux

The native runtime needs a C compiler and Make for building. After building, running the native executable does not require Python.

```sh
pkg update
pkg install git clang make
git clone https://github.com/rllibo833-sudo/pusingcuk.git
cd pusingcuk
bash scripts/install-termux.sh
pusingcuk-native examples/native/rekap_anggaran.pusingcuk
```

## Hello, world

```pusingcuk
jancuk
hedeh "Hello, world!"
selesai jancuk
```

Run it with:

```sh
python pusingcuk_new.py program.pusingcuk
```

## Language basics

| Keyword | Meaning |
|---|---|
| `jancuk` | Start a program |
| `lah` | Declare a variable |
| `hedeh` | Print a value |
| `njir` | Start a conditional |
| `kampret` | Alternative branch |
| `mumet` | Start a while loop |
| `tanya` | Read text input |
| `fungsi` | Define a function |
| `balek` | Return a value |
| `selesai jancuk` | End a program |

Example:

```pusingcuk
jancuk
lah name = "Budi"
lah age = 20
hedeh "Hello, " + name
njir age >= 18
    hedeh "Adult"
kampret
    hedeh "Under 18"
selesai njir
selesai jancuk
```

See [the language specification](SPEC.md), [the beginner guide](docs/PEMULA.md), and [the slang keyword guide](docs/KOSAKATA_GENZ.md) for more examples and exact syntax.

## Development and tests

Run the Python test suite offline from the repository root:

```sh
python -m unittest discover -s tests -v
```

Run native-runtime tests (requires a C compiler and Make):

```sh
make test-native
```

Run cross-runtime conformance checks:

```sh
python tools/conformance.py
```

The Python interpreter is the reference development path. The native C runtime and compiler targets support documented subsets and are not yet fully equivalent. See the [runtime compatibility matrix](docs/COMPATIBILITY.md), [native runtime notes](docs/NATIVE_RUNTIME.md), and [compiler targets](docs/COMPILER_TARGETS.md).

## Offline-first policy

The core language interpreter, native runtime, compiler, and tests are designed to run locally without outbound network access, API keys, hosted services, or third-party Python packages. The first-time commands `git clone` and `pkg install` shown above download source/tools and therefore require a connection during setup. For a strictly offline setup, transfer the repository and ensure Python (and, if building native code, a C compiler and Make) are already installed. After setup, running Pusingcuk does not need internet. Tests should use local files only. The optional browser workbench binds to loopback (`127.0.0.1`) for this device only and must not contact external services.

Do not add `os.system`, Python `eval` or `exec`, `requests`, OpenAI SDK dependencies, API-key requirements, or automatic outbound network calls to the core runtime. Keep external integrations out of the default execution path and add offline tests for new features.

**Security note:** the PVM JavaScript and Python backends use restricted expression parsing. External network URLs are rejected; only local `data:text/plain,` payloads are supported. PVM file operations are still not confined by an operating-system sandbox, so do not run bytecode from untrusted sources. Check [SECURITY.md](SECURITY.md) for current limitations.

## Documentation and repository guide

The full, categorized documentation catalog is in [docs/README.md](docs/README.md). Independent technical reviewers can start with [docs/INDEPENDENT_REVIEW.md](docs/INDEPENDENT_REVIEW.md).

- [Project vision and community principles](docs/VISION.md)
- [Repository structure and feature status](docs/REPO_STRUCTURE.md)
- [Beginner guide](docs/PEMULA.md)
- [Language and technical dictionary (English)](docs/DICTIONARY.md)
- [Plain-language dictionary (Indonesian)](docs/KAMUS_PUSINGCUK.md)
- [Slang and alias design](docs/KOSAKATA_GENZ.md)
- [Vocabulary registry and examples](library/README.md)
- [Language specification](SPEC.md)
- [Runtime compatibility](docs/COMPATIBILITY.md)
- [Native runtime](docs/NATIVE_RUNTIME.md)
- [Compiler targets](docs/COMPILER_TARGETS.md)
- [Python importer and standard-library subset](docs/IMPORT_PYTHON.md)
- [Native runtime and ecosystem roadmap](docs/NATIVE_SECURE_ECOSYSTEM_ROADMAP.md)
- [Contributing guide](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Community code of conduct](CODE_OF_CONDUCT.md)

## Contributing and project contact

Pusingcuk is open to contributions from beginners and experienced developers. You do not need to be a programmer to contribute: documentation, translations, examples, reproducible bug reports, and thoughtful design feedback are useful too. Read [CONTRIBUTING.md](CONTRIBUTING.md), describe the problem clearly, include a small reproducible example where possible, and add tests for behavior changes. Contributions should preserve offline operation and document Android support honestly.

For ordinary project contact and review feedback, email **pusingcukdevprog@gmail.com**. Please do not send passwords, access tokens, private user data, or unpatched vulnerability details by ordinary email; follow [SECURITY.md](SECURITY.md) for security reports.

## Community extensibility

Pusingcuk is intended to be developed by people and communities beyond its founder, including Ecoslang.org and other language, education, and open-source communities. The shared language specification, conformance fixtures, and intermediate representation are the foundation for compatible runtimes, libraries, compiler targets, and future integrations. Database adapters, server/API tooling, frontend bindings, WebAssembly, stable FFI/ABI, configurable regional vocabulary, and blockchain support are development goals, not claims of production-ready support. See the [English dictionary](docs/DICTIONARY.md), [Indonesian dictionary](docs/KAMUS_PUSINGCUK.md), and [ecosystem roadmap](docs/NATIVE_SECURE_ECOSYSTEM_ROADMAP.md).

## License

Pusingcuk is distributed under the MIT License. See [LICENSE](LICENSE).
