# Pusingcuk Examples and Vocabulary Registry

This directory contains runnable examples and a machine-readable vocabulary registry. It is not yet a package manager or a general-purpose importable standard library.

- [`kosakata.json`](kosakata.json): keyword and alias glossary, meanings, and support-status metadata.
- [`conditional_logic.pusingcuk`](conditional_logic.pusingcuk): comparisons, booleans, short-circuit logic, and conditionals.
- [`loops_functions_genz.pusingcuk`](loops_functions_genz.pusingcuk): loops, recursive functions, and newer slang aliases. Run it with the modular interpreter because its text output is not supported by the experimental C source backend subset.
- [`stdlib.py`](stdlib.py): an internal builtin registry for conversions, shared numeric helpers, and math helpers (`akar`, `bawah`, `atas`, `pangkat`, `sinus`, `kosinus`), and statistics helpers (`rata_rata`, `median`). Registry presence alone does not imply every runtime supports a builtin: the six math helpers currently work in the JS/Python compiler backends, and HTML uses the JS backend; VM/native C support is not yet claimed.

## Run examples with the Python interpreter

From the repository root:

```sh
python pusingcuk_new.py library/conditional_logic.pusingcuk
python pusingcuk_new.py library/loops_functions_genz.pusingcuk
```

## Compile the conditional example to C11

With Python and a C11 compiler installed:

```sh
python -m compiler.c_backend library/conditional_logic.pusingcuk -o /tmp/conditional_logic.c
cc -std=c11 -Wall -Wextra -Werror /tmp/conditional_logic.c -o /tmp/conditional_logic
/tmp/conditional_logic
```

The compiled executable does not require Python at runtime. Python is only used by the compiler front end.

## How to update the vocabulary

When adding or changing a keyword or alias, update all relevant layers together:

1. The lexer/parser or runtime implementation that actually recognizes the word.
2. The language specification and slang guide.
3. `kosakata.json`, including the alias's canonical target and honest support-status fields.
4. Runnable examples and regression tests for the runtimes that claim support.

The JSON registry is a contributor-facing reference, not proof that a feature works. The automated tests should compare its alias mapping with the implementation so the two cannot silently drift.

## Understanding support status

- `native_runtime: tested` means a native-runtime fixture exercises the feature; it does not imply every compiler target supports it.
- `native_runtime: pending-native-support` means the standalone native runtime does not yet claim support for that alias/feature.
- `c_backend: supported` or a more specific subset label describes the experimental source-to-C backend only.
- `c_backend: unsupported` means the feature must not be used in C-backend examples; the compiler should reject it explicitly.

The glossary is a practical index, not a replacement for `SPEC.md`, the semantic contract, or the runtime compatibility matrix. If information differs, report the mismatch and use tests plus the relevant implementation to establish the actual behavior.


## Explicit Python statistics subset

The Python importer maps only `statistics.mean` to `rata_rata` and `statistics.median` to `median`. Both accept a non-empty list of finite numbers; this is a deliberately small Pusingcuk API, not full Python `statistics` compatibility. Other statistics functions, wildcard imports, VM, and native C support are not claimed.
