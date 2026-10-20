# Browser Playground Runtime

The GitHub Pages playground is an in-browser execution target implemented in `site/runtime.js`. It tokenizes and parses `.cuk` source into an AST and interprets that AST directly; it does not generate JavaScript from user source, call `eval`, load Pyodide, or send code to a server.

## Supported core

- Program boundaries, declarations, assignments, output, arithmetic, comparisons, boolean short-circuit operators, and unary operators.
- `njir` conditionals, `mumet` loops, `untuk` iteration, `fungsi`/`balek`, and `coba`/`ketangkep`/`akhirnya`.
- Lists, dictionaries, indexing, and deterministic pure built-ins, including JSON, HTML escaping, and CSV row formatting.
- Diagnostics for syntax errors, unknown names, invalid types, invalid JSON, and runtime limits.

## Explicit limitations

The browser runtime is intentionally a separate, capability-limited target, not a claim of full parity with the Python reference interpreter. Interactive `tanya` input, filesystem access, imports, shell commands, and network built-ins are unavailable. Execution is bounded by source size, interpreter steps, recursion depth, collection size, and output size. Unsupported behavior raises a visible error rather than executing host JavaScript.

## Verification

`node tests/test_browser_runtime.js` runs every curated gallery program and compares output with the checked-in expected output, then exercises arithmetic, short-circuiting, nested JSON, escaping, invalid input, loop limits, and the no-host-eval boundary. The Pages workflow runs this suite before publishing.
