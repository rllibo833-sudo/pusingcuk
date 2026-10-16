# PusingCuk AI — CukAccount bridge

This branch adds a fixed, hash-pinned `.cuk` helper named
`journal_balance_check`. It accepts only two bounded integer totals and returns
a deterministic status. It cannot read files, access a database, post a journal,
or receive arbitrary source code from the model.

## Safety contract

- CukAccount's Dart domain and its future SQLite transaction layer remain the
  financial source of truth.
- The AI tool is a secondary arithmetic cross-check only. Equal totals alone do
  not establish that a journal is valid, complete, correctly classified, or
  compliant with an accounting standard.
- Inputs are schema-validated integers in the configured range; boolean, negative,
  oversized, missing, and extra arguments are rejected.
- The artifact is loaded from package-owned source and verified by SHA-256 before
  execution. The subprocess receives only a minimal environment and has a timeout.
- This is a fixed-artifact runner, not an OS sandbox. Never register model-generated
  source and never send real user financial records to a provider by default.

The CukAccount CI workflow separately runs synthetic `.cuk` fixtures using a
pinned PusingCuk reference-interpreter commit. This tool can be integrated there
only after its branch passes the PusingCuk test suite and the pin is deliberately
updated.
