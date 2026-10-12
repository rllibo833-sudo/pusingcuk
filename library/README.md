# Pusingcuk Standard Examples

This directory contains reusable keyword references and example Pusingcuk programs.

- [`kosakata.json`](kosakata.json): machine-readable glossary of keywords, aliases, operators, meanings, and runtime support status.
- [`conditional_logic.pusingcuk`](conditional_logic.pusingcuk): examples of comparisons, booleans, short-circuit logic, and conditionals supported by the C backend subset.
- [`loops_functions_genz.pusingcuk`](loops_functions_genz.pusingcuk): examples of loops, recursive functions, and slang aliases. Run this example with the modular interpreter because it prints text not yet supported by the C backend.

## Run examples with the Python interpreter

From the repository root:

```sh
python pusingcuk_new.py library/conditional_logic.pusingcuk
python pusingcuk_new.py library/loops_functions_genz.pusingcuk
```

## Compile an example to C11

With Python and a C11 compiler installed:

```sh
python -m compiler.c_backend library/conditional_logic.pusingcuk -o /tmp/conditional_logic.c
cc -std=c11 -Wall -Wextra -Werror /tmp/conditional_logic.c -o /tmp/conditional_logic
/tmp/conditional_logic
```

The compiled executable does not require Python at runtime. Python is only used by the compiler front end.

## Understanding support status

- `native_runtime: tested` means the feature has tests for the standalone C runtime; check the runtime matrix for detailed limits.
- `c_backend: supported` means the feature is included in the tested source-to-C subset.
- `c_backend: unsupported` means the feature must not be used in C-backend examples; the compiler should reject it explicitly.

The glossary is a practical index, not a replacement for the language specification. If information differs, refer to `SPEC.md` and the semantic documentation.
