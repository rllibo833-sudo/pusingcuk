# Pusingcuk Language and Technical Dictionary

This is the plain-language map for learners and contributors. It describes the `0.4-dev` language-spec contract; the implementation release line is versioned separately. It is not a promise that every feature works on every backend.

## 1. Start here

- **Language syntax:** [`SPEC.md`](../SPEC.md)
- **Beginner tutorial:** [`PEMULA.md`](PEMULA.md) (Indonesian)
- **Keyword aliases:** [`KOSAKATA_GENZ.md`](KOSAKATA_GENZ.md) (Indonesian)
- **Runtime feature matrix:** [`COMPATIBILITY.md`](COMPATIBILITY.md)
- **Native C runtime:** [`NATIVE_RUNTIME.md`](NATIVE_RUNTIME.md)
- **Compiler targets:** [`COMPILER_TARGETS.md`](COMPILER_TARGETS.md)
- **Contributor rules:** [`CONTRIBUTING.md`](../CONTRIBUTING.md)
- **Security policy:** [`SECURITY.md`](../SECURITY.md)

## 2. Basic language keywords

| Keyword | Meaning | Example |
|---|---|---|
| `jancuk` | Starts a program | `jancuk` |
| `selesai jancuk` | Ends the program | `selesai jancuk` |
| `lah` | Declares a new variable | `lah umur = 17` |
| `hedeh` | Prints a value | `hedeh umur` |
| `tanya` | Displays a prompt and reads one line of text | `tanya nama = "Nama: "` |
| `njir` | Starts a condition | `njir umur >= 17` |
| `kampret` | Starts the alternative branch | `kampret` |
| `mumet` | Starts a while loop | `mumet i < 3` |
| `untuk` / `dalam` | Iterates over a supported collection or range | `untuk item dalam daftar` |
| `fungsi` | Defines a function | `fungsi tambah(a, b)` |
| `balek` | Returns a value from a function | `balek a + b` |
| `selesai njir` | Ends a conditional block | `selesai njir` |
| `selesai mumet` | Ends a while loop | `selesai mumet` |
| `selesai untuk` | Ends a for loop | `selesai untuk` |
| `selesai fungsi` | Ends a function | `selesai fungsi` |

The lexer also recognizes documented slang aliases. Check [`KOSAKATA_GENZ.md`](KOSAKATA_GENZ.md) and [`library/kosakata.json`](../library/kosakata.json) before adding or changing an alias. Prefer canonical keywords in teaching material so examples remain easy to compare across implementations.

## 3. Values and operators

- **Number:** `10`, `-3`, `2.5`
- **Text/string:** `"Halo"`
- **Boolean:** `benar` and `salah`
- **List:** `[10, 20, 30]`
- **Dictionary/map:** `{"nama": "Budi", "umur": 20}`
- **Index:** list and text indexes start at zero, for example `angka[0]`.
- **Assignment:** `umur = umur + 1` changes an existing variable.
- **Comment:** a line whose first non-space character is `#`.

Arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`.

Comparison operators: `==`, `!=`, `<`, `<=`, `>`, `>=`.

Logical operators: `dan` (AND), `atau` (OR), and `bukan` (NOT).

A declaration creates a new variable; assignment updates an existing one. Redeclaring a variable in the same scope is an error. Exact collection, numeric, and Unicode behavior can differ by backend; check the compatibility matrix.

## 4. Built-in functions

The complete and test-checked list of 18 built-ins, argument counts, and per-target support is in the [built-in catalogue](language/BUILTINS.md). The examples below are a learner-friendly subset; an entry in a registry does not mean every target supports it.

| Function | Purpose | Example |
|---|---|---|
| `panjang(value)` | Counts supported text/list/dictionary items | `hedeh panjang("halo")` |
| `rentang(end)` | Creates integers from zero up to, but not including, `end` | `rentang(4)` |
| `rentang(start, end)` | Creates a range with an exclusive end | `rentang(1, 5)` |
| `rentang(start, end, step)` | Creates a stepped range; step cannot be zero | `rentang(0, 10, 2)` |
| `mutlak(number)` | Absolute value | `mutlak(-8)` |
| `minimum(a, b)` | Smaller of two numbers | `minimum(3, 9)` |
| `maksimum(a, b)` | Larger of two numbers | `maksimum(3, 9)` |
| `bulatkan(number)` | Rounds a finite number using the documented ties-to-even rule | `bulatkan(2.5)` |
| `rata_rata(list)` | Arithmetic mean of a non-empty list of finite numbers | `rata_rata([1, 2, 6])` |
| `median(list)` | Median of a non-empty list of finite numbers | `median([1, 4, 8])` |
| `teks(value)` | Converts a value to text in the standard-library registry | Check target support first |
| `bilangan(value)` | Converts a value to an integer in the standard-library registry | Check target support first |
| `desimal(value)` | Converts a value to a decimal number in the standard-library registry | Check target support first |
| `logika(value)` | Converts a value to a boolean in the standard-library registry | Check target support first |

The reference interpreter and experimental JavaScript, Python, and HTML targets currently implement `rata_rata` and `median`; VM/native C support is not claimed. This is a small Pusingcuk API, not full Python `statistics` compatibility. For exact implementation status, see [`IMPORT_PYTHON.md`](IMPORT_PYTHON.md), [`compiler-type-system-and-stdlib.md`](compiler-type-system-and-stdlib.md), [`COMPILER_TARGETS.md`](COMPILER_TARGETS.md), and [`NATIVE_RUNTIME.md`](NATIVE_RUNTIME.md).

## 5. A complete small program

```pusingcuk
jancuk
lah nama = "Pusingcuk"
lah angka = 2

fungsi tambah(a, b)
    balek a + b
selesai fungsi

hedeh "Halo, " + nama
hedeh tambah(20, 22)

njir angka < 3
    hedeh "Masih kecil"
kampret
    hedeh "Tiga atau lebih"
selesai njir
selesai jancuk
```

Run it with the reference interpreter from the repository root:

```sh
python pusingcuk_new.py halo.cuk
```

Or use the compiler CLI to generate a documented experimental target:

```sh
python -m compiler halo.cuk --target python --output /tmp/halo.py
python /tmp/halo.py
```

The generated target supports a subset of the language. If compilation rejects a feature, that is preferable to silently generating code with different meaning.

## 6. Repository and compiler terms

| Term | Plain-language meaning |
|---|---|
| **Lexer** | Splits source text into meaningful tokens, such as keywords, names, and operators. |
| **Parser** | Checks token order against the language grammar and builds a syntax tree. |
| **AST** | Abstract Syntax Tree: a structured representation of what the source code says. |
| **Evaluator / interpreter** | Runs the program directly instead of first producing a standalone executable. |
| **Runtime** | The code and services that make a program execute, including values, built-ins, and error handling. |
| **Native runtime** | A runtime compiled to a platform executable. Pusingcuk's C runtime is a tested subset, not full parity. |
| **Compiler** | Translates a program to another representation or language. |
| **Backend** | The part of a compiler that emits a particular target, such as JavaScript or Python. |
| **IR** | Intermediate Representation: a structured format between source parsing and a compiler target. |
| **Bytecode / VM** | Compact instructions executed by a virtual machine. PVM is a draft; the JSON VM target is a separate implementation. |
| **Conformance test** | Runs the same language behavior against implementations to check whether they agree. |
| **ABI / FFI** | Rules for calling functions and passing values across compiled languages or native libraries. Not a stable Pusingcuk feature yet. |
| **Standard library** | Built-in functions and reusable modules maintained with the language. The registry is not fully enabled on every target. |
| **Dependency** | External software a project needs to build or run. The core Python interpreter aims to use the Python standard library only. |
| **Sandbox** | An enforced isolation boundary limiting what a program can access. Pusingcuk does not currently guarantee one. |
| **Capability** | An explicit permission to use a resource such as a file, database, or network. This is a design goal for future integrations. |
| **CI** | Continuous Integration: automated checks run when repository changes are pushed. A green CI run proves only the checks that ran. |
| **WASM / WebAssembly** | A portable compiled target. A Pusingcuk WASM backend is not currently available. |
| **Frontend / backend** | In web apps, frontend is the user-facing browser part; backend is the server-side logic. The compiler's “backend” has a different meaning. |
| **API** | A defined interface that one program uses to communicate with another program or service. A general production API framework is not currently available. |
| **Database adapter** | Code that connects the language/runtime to a specific database through a documented interface. A complete standard database adapter is not currently available. |
| **Blockchain SDK** | A library for interacting with a blockchain network. Production blockchain support is not currently available. |

## 7. Current support versus future goals

**Current development paths**
- Reference interpreter: `pusingcuk_new.py` and the modular Python implementation.
- Native C runtime: works for the features documented in `NATIVE_RUNTIME.md`; it is not fully equivalent to the reference interpreter.
- Compiler CLI: experimental `js`, `python`, `html`, `json`, and `vm` targets with different supported subsets.
- PVM v1: draft bytecode format; do not treat it as a stable public ABI.

**Not yet a verified production feature**
- Full module/package system across runtimes.
- Stable ABI/FFI.
- WebAssembly backend.
- Complete database connectors and migrations.
- Production-ready HTTP server/API framework.
- Full frontend/browser API bindings.
- Production blockchain integration.
- General-purpose OS-enforced sandbox.

These are valid community development directions, not features to advertise as already implemented. Each new feature should start with a written contract, a minimal working example, tests, a security review appropriate to its risk, and explicit support status.

## 8. Rules for contributors

1. Preserve the language's offline-first core. Do not add `os.system`, Python `eval`/`exec`, `requests`, OpenAI SDK dependencies, API-key requirements, or automatic outbound connections.
2. Keep parsing and execution separate. Never treat generated host-language code as a security sandbox.
3. Change the specification, implementation, fixtures, and compatibility notes together when language behavior changes.
4. Test supported behavior and rejection cases, including malformed input.
5. Mark each feature as planned, prototype, experimental, tested, or stable. Do not use “supported” without naming the runtime/target.
6. Prefer small, documented changes that are easy for first-time contributors to understand.
7. Never commit secrets, private data, build outputs, or personal files.
8. Do not run untrusted programs or PVM bytecode on a device containing sensitive files. File operations are not currently confined by an OS sandbox.
