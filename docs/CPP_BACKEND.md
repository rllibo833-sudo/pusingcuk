# C++17 backend PusingCuk

**Status:** experimental source backend. It emits a standalone C++17 program with a small PusingCuk value runtime embedded; the generated executable does not need Python at runtime.

## Build and run

From the repository root:

~~~sh
python -m compiler program.cuk --target cpp --output program.cpp
g++ -std=c++17 -O2 program.cpp -o program
./program
~~~

The compiler itself still runs under Python. The output is C++ source, not a binary; compiling and linking the generated file is a separate step.

## Current conformance boundary

The initial target is tracked in tests/conformance/cpp_manifest.json. It deliberately reuses the 55 fixture IDs from the first Go backend manifest so that the two generated-language targets start from the same measured core. The automated test compiles and executes every selected fixture, then compares exit code, stdout, error class, and source line against the shared fixture contract.

Implemented in this subset:

- Scalar numbers, strings, booleans, and None.
- Variables, assignment, output, arithmetic, comparisons, unary operators, and short-circuit dan / atau.
- njir, mumet, untuk, rentang, top-level fungsi and balek.
- Lists, ordered dictionaries, mutation, indexing, and the tested equality rules.
- Numeric, range, conversion, trigonometry, statistics, and rounding built-ins used by the selected fixtures.
- Runtime diagnostics with source-line reporting and limits on steps, ranges, and collection size.

Not claimed yet: interactive tanya, coba / ketangkep / akhirnya, JSON/HTML/CSV built-ins, filesystem or network APIs, module imports, closures/nested functions, complete diagnostic wording parity, or full language compatibility outside the manifest. Unsupported AST nodes fail during compilation instead of being translated to an approximate behavior.

## Verification

Run the target suite:

~~~sh
python -m unittest tests.test_cpp_backend -v
python -m compiler tests/conformance/output_arithmetic.pusingcuk --target cpp --output /tmp/halo.cpp
g++ -std=c++17 /tmp/halo.cpp -o /tmp/halo
/tmp/halo
~~~

The suite requires a C++17 compiler (g++ or c++). A successful result proves only the selected fixtures and toolchain, not compatibility with every C++ compiler or platform.
