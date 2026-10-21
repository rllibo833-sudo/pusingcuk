# Browser Playground Runtime

The GitHub Pages playground is an in-browser execution target implemented in `site/runtime.js`. It tokenizes and parses `.cuk` source into an AST and interprets that AST directly; it does not generate JavaScript from user source, call `eval`, load Pyodide, or send code to a server.

## Supported core

- Program boundaries, declarations, assignments, output, arithmetic, comparisons, boolean short-circuit operators, and unary operators.
- `njir` conditionals, `mumet` loops, `untuk` iteration, `fungsi`/`balek`, and `coba`/`ketangkep`/`akhirnya`.
- Lists, dictionaries, indexing, and deterministic pure built-ins, including JSON, HTML escaping, and CSV row formatting.
- Diagnostics for syntax errors, unknown names, invalid types, invalid JSON, and runtime limits.

## Explicit limitations

The browser runtime is intentionally a separate, capability-limited target, not a claim of full parity with the Python reference interpreter. Interactive `tanya` input, filesystem access, imports, shell commands, and network built-ins are unavailable. Execution is bounded by source size (64 KiB), interpreter steps (50,000), recursion depth (100), collection/iteration size (10,000 items), and output size (64 KiB). Some limits apply to specific operations: for example, loops and generated collections have their own item caps. Unsupported behavior raises a visible error rather than executing host JavaScript.

## Verification

Run these commands from the repository root:

- `node tests/test_browser_runtime.js` — executes every curated gallery program against its expected output and covers arithmetic edge cases, short-circuiting, nested JSON, HTML/CSV escaping, functions, mutable indexes, iteration, exception handling, malformed syntax, invalid JSON, host-code isolation, and resource limits.
- `node tests/test_browser_playground.js` — exercises the actual inline playground controller with a small DOM harness: initial execution, Run button, runtime diagnostics, Ctrl+Enter, clear output, successful example loading, and preservation of editor contents after a failed example fetch.

The Pages workflow runs both suites, in addition to checking the reference interpreter and compiled examples, before publishing. The compiler fixture workflow also runs `node tests/test_browser_differential.js`, which compares a curated browser-supported subset against the Python reference for exit code, stdout, error class, and source line. The selected subset is explicit in `tests/conformance/browser_manifest.json`; omission means browser parity is not claimed. These tests do not establish full language parity or replace a real-device/browser compatibility matrix.
