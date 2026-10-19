# PusingCuk from Zero — Beginner Guide

Start with a small program, then move gradually to functions and a mini project. New programs should use the canonical `.cuk` extension; legacy `.pusingcuk` files remain supported. The native runtime is still under development and supports only the features listed in [Native Runtime](NATIVE_RUNTIME.md).

The documentation style aims to be friendly and conversational without sacrificing technical accuracy.

## 1. Prepare the tools on Android / Termux

The current language contract is `0.6-dev`; the Python development package is `0.8.0.dev0`. The exact built-in count and native support must be read from the [built-in contract](../library/builtin_contract.json) and [compatibility evidence](COMPATIBILITY.md), rather than copied into this tutorial as a second source of truth.

Install the tools in Termux:

```sh
pkg update
pkg install git clang make
```

Clone the repository:

```sh
git clone https://github.com/rllibo833-sudo/pusingcuk.git
cd pusingcuk
```

Build and install the native executable:

```sh
bash scripts/install-termux.sh
```

After a successful build, the executable is installed as `pusingcuk-native`. The compiler is needed to rebuild the executable, not for each run of a successfully built native program.

## 2. Run a first example

```sh
pusingcuk-native examples/native/rekap_anggaran.pusingcuk
```

The example calculates a budget using dictionaries, loops, conditions, and functions. Expected output values are part of the checked-in example and its tests; consult those sources when changing the example.

To build and run the native test suite:

```sh
make test-native
```

## 3. Create a hello-world program

Create a new file named `halo.cuk` and add:

```cuk
jancuk
lah nama = "PusingCuk"
hedeh "Halo, " + nama
selesai jancuk
```

Run it with the reference interpreter:

```sh
python pusingcuk_new.py halo.cuk
```

Check syntax without treating that result as proof of runtime correctness:

```sh
python pusingcuk_new.py --check halo.cuk
```

The reference interpreter requires Python. The native executable has a different feature subset, so a program that works on one target must still be checked against the target's documented support.

## 4. Learn in this order

1. Variables and basic values.
2. Output and input.
3. Arithmetic and comparisons.
4. Conditions and loops.
5. Lists and dictionaries.
6. Functions and return values.
7. Built-ins and error handling.
8. Conformance fixtures and runtime differences.

Use the [language specification](../SPEC.md) for exact syntax, the [semantic contract](SEMANTIC_CONTRACT.md) for required behavior, and the [compatibility snapshot](COMPATIBILITY.md) for measured target support.

## Safety note

The interpreter, compiler, and VM are not operating-system sandboxes. Run only code you trust in a sensitive environment. A VM budget is not a hard OS-level security boundary.
