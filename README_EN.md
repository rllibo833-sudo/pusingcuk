# PusingCuk

PusingCuk is an experimental programming language with Indonesian-readable keywords. Its compatibility baseline is the **Python reference interpreter** plus a tested **native C runtime** subset.

- **Language contract:** `0.5-dev`
- **Development package version:** `0.8.0.dev0` (PEP 440 spelling for the `0.8.0-dev` line)
- **Canonical source extension:** `.cuk`; legacy `.pusingcuk` files remain supported.

PusingCuk is experimental and is **not** an operating-system sandbox. Do not run untrusted programs or bytecode with access to important files, credentials, or accounts.

## Quick start

On Linux, macOS, or Termux with Python 3.11 or 3.12:

```sh
pkg install python git  # Termux; use your platform package manager elsewhere
git clone https://github.com/rllibo833-sudo/pusingcuk.git
cd pusingcuk
python pusingcuk_new.py examples/halo_dunia.cuk
```

Running the CLI without a source-file argument opens the interactive terminal REPL:

```sh
python pusingcuk_new.py
# or after installation
pusingcuk
```

## First program

```cuk
jancuk
lah answer = 40
hedeh answer + 2
selesai jancuk
```

Run it with `python pusingcuk_new.py program.cuk`. Use `python pusingcuk_new.py --check program.cuk` to parse without executing the program.

## Built-ins and runtime parity

The 21-item built-in contract is recorded in `library/builtin_contract.json`. The Python reference supports all 21 contracted built-ins. Native C has verified support for 17, including rounding, trigonometry, logarithms (`logaritma`, `log10`), and statistics. Other compiler targets have independent capability subsets. A feature is portable to a runtime only when the conformance manifest requires it and its fixture passes on that runtime.

The `logaritma(x)` intrinsic returns the natural logarithm and `log10(x)` returns base-10 logarithm. Both require a finite number greater than zero. Invalid domains are runtime errors on Python reference and native C.

## Run tests

```sh
python -m unittest discover -s tests -v
python tools/conformance.py
make test-native
```

See [SPEC.md](SPEC.md), the [built-in catalogue](docs/language/BUILTINS.md), [conformance fixtures](docs/CONFORMANCE_FIXTURES.md), [Termux instructions](docs/termux/README.md), and [editor support](docs/EDITOR_SUPPORT.md).

## Contributing

Language-contract changes should update the specification, semantic contract, built-in metadata and positive/negative conformance fixtures together. Avoid adding keyword aliases without explicit approval. Native support must never be marked as available before it has working implementations and tests.
