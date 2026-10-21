# PusingCuk

> **Warung-language feel. Serious machinery.**  
> PusingCuk is an experimental programming language with the `.cuk` extension, Indonesian-language keywords, and its own vocabulary and identity.

PusingCuk combines approachable Indonesian syntax with a reference interpreter, experimental compiler targets, a native runtime, and conformance tooling. It is an open learning and language-engineering project—not a claim that every target is equivalent or production-ready.

**[Try the browser playground →](https://rllibo833-sudo.github.io/pusingcuk/playground.html)** — experimental; it runs a bounded JavaScript AST interpreter in `site/runtime.js`, locally in the browser. It does not use Pyodide or a server-side code executor.

<!-- BEGIN GENERATED PYTHON-FREE SCORE BADGE -->
[![Python-free runtime · native C · 79/79 fixtures](docs/assets/python-free-score.svg)](docs/PYTHON_FREE_SCORE.md)
Python-free runtime, native C: **79 dari 79 fixture aktif lulus**. Ini cakupan fixture runtime native C, bukan klaim bahwa seluruh proyek atau proses build bebas Python.
<!-- END GENERATED PYTHON-FREE SCORE BADGE -->

**Status:** language contract `0.6-dev`; Python package `0.8.0.dev0`. Development software, not a stable release.

Metadata paket pada `main` adalah `0.8.0.dev0`. Backend support differs; check the compatibility matrix and fixtures.

## Run your first program

Requirements: Python 3.11 or 3.12.

Save as `hello.cuk`:

```cuk
jancuk
lah nama = "Dunia"
hedeh "Halo, " + nama
selesai jancuk
```

Run it and check its syntax:

```sh
python pusingcuk_new.py hello.cuk
python pusingcuk_new.py --check hello.cuk
```

<!-- BEGIN GENERATED SPEC ALIASES -->
## Keyword alias reference

This table is generated from SPEC.md. It documents accepted spellings; it does not add reserved words.

| Alias | Canonical keyword |
|---|---|
| adooh | kampret |
| bacot | hedeh |
| bacrit | hedeh |
| berak | hedeh |
| berisik | hedeh |
| bestie | lah |
| bongkar | baca |
| bongkar_json | baca_json |
| cetak | hedeh |
| crot | hedeh |
| gas | jancuk |
| gas_api | kepo_internet |
| gebber | hedeh |
| gembor | hedeh |
| gitu | selesai |
| impor | angkut |
| inthiseco | jancuk |
| janggal | bukan |
| jedor | hedeh |
| jir | hedeh |
| kelar | selesai |
| keluarin | hedeh |
| kepo | tanya |
| kirim_gosip | kirim_api |
| koar | hedeh |
| muncrat | hedeh |
| ngegas | hedeh |
| nyalak | hedeh |
| omong | hedeh |
| parse_json | jadi_json |
| print | hedeh |
| sembur | hedeh |
| semprot | hedeh |
| senggol | hedeh |
| simpen | tulis |
| simpen_json | tulis_json |
| skip | kampret |
| spill | hedeh |
| stalking | kepo_internet |
| suarakan | hedeh |
| tampilkan | hedeh |
| teriak | hedeh |
| valid | benar |
| waktu | jam |
| zonk | salah |
<!-- END GENERATED SPEC ALIASES -->

## The three parts of the ecosystem

- **The .cuk language:** specification, interpreter, compiler, and runtime. See [IDENTITY.md](IDENTITY.md).
- **PusingCuk AI:** an assistant grounded in language/project knowledge—not a foundation model trained from scratch.
- **Cuk Reality Engine:** conformance tooling for checking behavior across targets; compatibility claims require execution evidence.

## Runtime and app distribution

Keep these deliverables separate:

- **PusingCuk Studio APK** is the Android Studio application built by the Studio workflow. It is an editor/workbench for writing and trying `.cuk` programs; it is not a general-purpose APK generated from arbitrary `.cuk` source.
- **CukAccount** is a separate accounting application with its own UI and application/runtime integration. A passing PusingCuk fixture does not mean CukAccount has been rewritten or packaged from `.cuk`.
- **An arbitrary `.cuk` application** can currently be interpreted or compiled only to the targets and language subset documented in the compatibility matrix. There is no claim that any `.cuk` file can be packaged as a standalone Android APK.

For local AI development on Android, use Termux with Ollama running on the same device. The local development path must default to loopback-only access, explicit opt-in for writes, and review-only proposals. It must not require a cloud model, a hosted database, or an automatic Git push. Device-specific Termux behavior still requires the documented on-device test; an Ubuntu CI pass is not a substitute.
## Repository map

| Area | Purpose |
|---|---|
| Language core | Lexer, parser, AST, reference interpreter, specification, and semantic contract |
| Compiler | IR and experimental JavaScript, Python, Go (curated subset), HTML, JSON IR, and VM targets |
| Native runtime | C implementation for a tested subset of the language |
| Library and vocabulary | Built-ins, machine-readable contracts, keywords, and aliases |
| Conformance | Tests and fixtures for explicitly supported targets |
| AI tools | Helpers for the .cuk development loop; not proof of a self-trained model |
| Examples and docs | Learning programs, dictionaries, runtime guides, and compatibility limits |

## Reading paths

- [English documentation map](docs/README.md)
- [Language specification](SPEC.md) → [semantic contract](docs/SEMANTIC_CONTRACT.md)
- [Compatibility matrix](docs/COMPATIBILITY.md) and [conformance fixtures](docs/CONFORMANCE_FIXTURES.md)
- [Technical dictionary](docs/DICTIONARY.md) · [Indonesian Warung dictionary](docs/KAMUS_PUSINGCUK.md)
- [Project overview](docs/PROJECT_OVERVIEW.md) · [project vision](docs/VISION.md) · [ecosystem implementation roadmap](docs/ECOSYSTEM_ROADMAP.md)
- [Contributing](CONTRIBUTING.md) · [security policy](SECURITY.md)

## How to read feature claims

- **Present in the repository** means a file or implementation exists.
- **Works on a specific path** means a matching example or check has been run.
- **Verified** means relevant target fixtures passed on the same commit.
- **Production-ready** requires further evidence for security, compatibility, packaging, operations, and real target environments.

A file, example, workflow, or backend does not automatically prove production readiness.

## Security limits

The interpreter, compiler, and VM are **not an operating-system sandbox**. Do not execute untrusted .cuk code or bytecode in sensitive environments. A native executable that runs without Python after compilation does not mean its build process is Python-free or that it provides security isolation.

## License

PusingCuk is licensed under MIT. See [LICENSE](LICENSE) for terms.
