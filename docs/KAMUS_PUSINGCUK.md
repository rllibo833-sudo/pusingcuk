# PusingCuk Dictionary — Warung Language Edition

This guide helps new learners understand the language vocabulary, the repository layout, and the difference between implemented features and future goals. The slang gives .cuk its cultural identity; the compiler and runtime still follow explicit technical contracts.

## 1. Where to start

- `README.md`: project entry point and quick start.
- `SPEC.md`: formal language syntax and behavior.
- `docs/PEMULA.md`: step-by-step beginner tutorial.
- `docs/KOSAKATA_GENZ.md`: keywords and slang aliases.
- `docs/COMPATIBILITY.md`: which targets passed the measured fixture set.
- `docs/NATIVE_RUNTIME.md`: tested native C runtime scope.
- `docs/COMPILER_TARGETS.md`: experimental compiler targets.
- `CONTRIBUTING.md`: contribution guidelines.
- `SECURITY.md`: security policy and limitations.

## 2. Core vocabulary

| Keyword | Meaning | Example |
|---|---|---|
| `jancuk` | Start a program | `jancuk` |
| `selesai jancuk` | End a program | `selesai jancuk` |
| `lah` | Declare a variable | `lah umur = 17` |
| `hedeh` | Print a value | `hedeh umur` |
| `tanya` | Ask for terminal input | `tanya nama = "Name: "` |
| `njir` | Begin a conditional branch | `njir umur >= 17` |
| `kampret` | Alternative branch | `kampret` |
| `mumet` | Repeat while a condition holds | `mumet i < 3` |
| `untuk` | Iterate through a collection or range | `untuk angka dalam rentang(1, 4)` |
| `fungsi` | Define a function | `fungsi tambah(a, b)` |
| `balek` | Return a value from a function | `balek a + b` |
| `benar` / `salah` | Boolean true / false | `lah aktif = benar` |
| `dan` / `atau` / `bukan` | Logical AND / OR / NOT | `njir aktif dan bukan selesai` |

Exact syntax and target support are defined by the language specification and conformance fixtures. This dictionary is a learning aid, not a substitute for the formal contract.

## 3. How to read feature status

- **Implemented:** corresponding code exists.
- **Tested:** a named test ran against a named target.
- **Compatible:** the required shared fixtures passed on the compared targets.
- **Experimental:** behavior or support may still change.
- **Planned:** not yet implemented or not yet proven by the required evidence.

Do not infer that a feature works on every backend because its keyword or built-in appears in the dictionary.
