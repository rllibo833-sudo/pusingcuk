# Historical Pusingcuk Archive

This directory contains experiments and backups from early development. They were moved out of the repository root so they are not mistaken for supported entry points or the active test suite.

- `interpreters/`: old interpreter versions. They are unsupported, have not been audited as current runtimes, and must not be used with untrusted input.
- `programs/`: old examples and manual fixtures. Use `examples/` for supported examples and `tests/` for active automated tests.
- `scripts/`: historical patch scripts. They are not used by the current build or CI.

`loop_test.pusingcuk` contains a loop without a stopping condition. Do not run it without a time limit and resource restrictions. Do not use archived files as the source of truth for current language behavior.
