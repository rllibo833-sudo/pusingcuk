# Historical Pusingcuk Archive

This directory contains historical experiments and backups from early development. Most old interpreters/programs were moved here, but a few legacy patch/backup artifacts remain at the repository root; `docs/REPO_STRUCTURE.md` lists them. Root-level leftovers are not supported entry points or the active test suite.

- `interpreters/`: old interpreter versions. They are unsupported, have not been audited as current runtimes, and must not be used with untrusted input.
- `programs/`: old examples and manual fixtures. Use `examples/` for supported examples and `tests/` for active automated tests.
- `scripts/`: historical patch scripts. They are not used by the current build or CI.

`loop_test.pusingcuk` contains a loop without a stopping condition. Do not run it without a time limit and resource restrictions. Do not use archived files as the source of truth for current language behavior.
