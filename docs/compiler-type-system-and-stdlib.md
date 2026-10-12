# Compiler type system and standard library

## Status

This change adds an isolated type-model module and an explicit standard-library
registry. It does **not** yet change source-language syntax or wire static type
checking into the interpreter, IR, or C backend. Treat it as a foundation, not
as a claim that Pusingcuk has a complete static type system.

## Type model

The initial type vocabulary is `any`, `void`, `null`, `bool`, `int`,
`float`, `string`, `list[T]`, and `map[K, V]`. Literal inference keeps
booleans distinct from integers. Integer values can flow to float targets;
float-to-integer assignment is not implicit. Unknown or mixed collection
elements use `any`.

## Standard library registry

The registry provides metadata and callable implementations for
`panjang`, `teks`, `bilangan`, `desimal`, `logika`, `mutlak`,
`minimum`, `maksimum`, and `bulatkan`. The JavaScript and Python compiler
backends and the bytecode VM execute the shared numeric subset `mutlak`,
`minimum`, `maksimum`, and `bulatkan`. These functions validate numeric
inputs, reject booleans, and use ties-to-even rounding for `bulatkan` across
those targets. The conversion functions remain registry-only until their
conversion semantics are aligned across every runtime. The registry
intentionally excludes file, network, shell, and process access. Numeric casts
reject booleans explicitly.

The Python importer additionally maps the allow-listed `math` APIs to
`akar`, `bawah`, `atas`, `pangkat`, `sinus`, and `kosinus`. Those six
helpers are implemented in the JavaScript and Python compiler backends; HTML
uses the same JavaScript runtime. They are **not yet available in the VM or
native C backend**, so Python programs using those math functions should
currently target `js`, `html`, or `python`.

## Required next integration steps

1. Agree on source syntax for declarations and annotations before enforcing
   static types; keep existing untyped programs compatible.
2. Add type annotations to IR nodes and validate operands, calls, returns,
   and collection operations in a dedicated semantic-analysis pass.
3. Make interpreter and C backend share the same builtin signatures and
   conformance fixtures so their observable behavior cannot drift.
4. Test overflow, division/modulo, invalid casts, nested collections, Unicode,
   error locations, and resource limits on both runtimes.
5. Only enable type errors by default after legacy examples and the full test
   suite pass consistently. Until then, type checking should be opt-in.

## Proposed repository layout

- `compiler/`: IR, semantic analysis, type model, code generation.
- `library/`: source-level modules and standard-library registry.
- `tests/`: interpreter, compiler, native, and shared conformance tests.
- `docs/`: language specification, architecture, compatibility, and roadmap.
- `native/`: C runtime/backend implementation.
- `android-studio/`: Android app and build integration.
- `archive/`: historical experiments, never imported by production code.


## Cross-target numeric builtins

The following program is supported by the JS, Python, and VM targets:

```pusingcuk
jancuk
hedeh mutlak(-8)
hedeh minimum(4, 9)
hedeh maksimum(4, 9)
hedeh bulatkan(2.5)
hedeh bulatkan(3.5)
selesai jancuk
```

Expected output:

```text
8
4
9
2
4
```

These names are reserved for builtins; user-defined functions cannot shadow them.
