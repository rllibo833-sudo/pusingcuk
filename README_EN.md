# PusingCuk

> **Warung-language feel. Serious machinery.**  
> PusingCuk is an experimental programming language with the `.cuk` extension, Indonesian-language keywords, and a distinct vocabulary and syntax identity.

The project combines approachable Indonesian syntax with a reference interpreter, experimental compiler targets, a native runtime, and conformance tooling. It is intended for learning, language experiments, and open development—not as a claim that every target is equivalent or production-ready.

**Status:** language contract `0.6-dev`; Python package `0.8.0.dev0`. This is development software, not a stable release. Backend support differs and must be checked against the compatibility matrix and fixtures.

## Run your first program

Requirements: Python 3.11 or 3.12.

Save as `hello.cuk`:

```cuk
jancuk
lah nama = "Dunia"
hedeh "Halo, " + nama
selesai jancuk
```

Run it and check syntax:

```sh
python pusingcuk_new.py hello.cuk
python pusingcuk_new.py --check hello.cuk
```

## What is in the repository?

| Area | Purpose |
|---|---|
| Language core | Lexer, parser, AST, reference interpreter, specification, and semantic contract |
| Compiler | IR and experimental JavaScript, Python, HTML, JSON IR, and VM targets |
| Native runtime | C implementation for a tested subset of the language |
| Library and vocabulary | Built-ins, machine-readable contracts, keywords, and slang aliases |
| PusingCuk AI | Assistant and tools for the .cuk development loop; not evidence of a self-trained foundation model |
| Conformance | Automated tests and fixtures for explicitly supported targets |
| Examples and docs | Learning programs, dictionaries, runtime guides, compatibility limits, and development notes |

## Reading paths

- **New to PusingCuk:** [Beginner guide](docs/PEMULA.md) (Indonesian)
- **Language rules:** [Specification](SPEC.md) → [Semantic contract](docs/SEMANTIC_CONTRACT.md)
- **Verified target support:** [Compatibility matrix](docs/COMPATIBILITY.md) and [conformance fixtures](docs/CONFORMANCE_FIXTURES.md)
- **Dictionary:** [English dictionary](docs/DICTIONARY.md) · [Kamus Bahasa Warung](docs/KAMUS_PUSINGCUK.md)
- **Documentation map:** [docs/README.md](docs/README.md)
- **Project overview and limitations:** [Project overview (English)](docs/PROJECT_OVERVIEW_EN.md) · [Ikhtisar proyek](docs/PROJECT_OVERVIEW.md)
- **Contributing and security:** [CONTRIBUTING.md](CONTRIBUTING.md) · [SECURITY.md](SECURITY.md)

## Feature-status language

- **Available** means an implementation exists in the repository.
- **Tested** means specific checks ran for a named target and commit.
- **Experimental** means behavior, coverage, or interfaces may still change.
- **Production-ready** requires additional evidence for security, compatibility, packaging, operations, and target-environment testing.

A file, example, workflow, or backend does not automatically prove production readiness. Language changes should keep the specification, implementation, fixtures, and compatibility matrix aligned.

## Security limits

The PusingCuk interpreter, compiler, and VM are **not an operating-system sandbox**. Do not execute untrusted .cuk code or bytecode in sensitive environments. A native executable that can run without Python after compilation does not mean its build process is Python-free or that it provides security isolation.

## License

PusingCuk is licensed under MIT. See [LICENSE](LICENSE) for terms.
