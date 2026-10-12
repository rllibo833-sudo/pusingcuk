# Pusingcuk

Pusingcuk is an experimental programming language with Indonesian-friendly keywords and local slang aliases. The project aims to make programming approachable while building a testable interpreter, a native C runtime, and experimental compiler backends.

> **Project status:** experimental, version 0.4-dev. Runtime and compiler support varies by feature. Pusingcuk is not a security sandbox and must not run untrusted programs on systems containing sensitive data.

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

The core language interpreter is designed to run locally and does not require a network connection, API key, hosted service, or third-party Python package. Tests should be runnable from local files. Any optional tool that serves a local browser page must bind to loopback only; it must not silently contact external services.

Do not add `os.system`, Python `eval` or `exec`, `requests`, OpenAI SDK dependencies, API-key requirements, or automatic outbound network calls to the core runtime. Keep external integrations out of the default execution path and add offline tests for new features.

**Security note:** the PVM JavaScript and Python backends now use restricted expression parsing. External network URLs are rejected; only local `data:text/plain,` payloads are supported. PVM file operations are still not confined by an operating-system sandbox, so do not run bytecode from untrusted sources. Check [SECURITY.md](SECURITY.md) for current limitations.

## Repository guide

- [Repository structure and feature status](docs/REPO_STRUCTURE.md)
- [Beginner guide](docs/PEMULA.md)
- [Language and technical dictionary (English)](docs/DICTIONARY.md)
- [Plain-language dictionary (Indonesian)](docs/KAMUS_PUSINGCUK.md)
- [Language specification](SPEC.md)
- [Runtime compatibility](docs/COMPATIBILITY.md)
- [Native runtime](docs/NATIVE_RUNTIME.md)
- [Compiler targets](docs/COMPILER_TARGETS.md)
- [Native runtime and ecosystem roadmap](docs/NATIVE_SECURE_ECOSYSTEM_ROADMAP.md)
- [Contributing guide](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Community code of conduct](CODE_OF_CONDUCT.md)

## Contributing

Pusingcuk is open to contributions from beginners and experienced developers. Read [CONTRIBUTING.md](CONTRIBUTING.md), describe the problem clearly, include a small reproducible example, add tests, and document any behavior change. Contributions should preserve offline operation and Android compatibility.

## License

Pusingcuk is distributed under the MIT License. See [LICENSE](LICENSE).
