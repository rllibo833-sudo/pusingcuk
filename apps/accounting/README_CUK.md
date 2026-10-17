# CukAccount rules written in .cuk

This directory is the first executable domain slice for CukAccount written in
PusingCuk syntax. It deliberately covers deterministic rules only; the existing
Flutter/Dart implementation remains authoritative for production posting and
money persistence until the full runtime, exact-money representation, database,
and integration tests are proven.

## Files
- `cukaccount_rules.cuk`: accounting equation, journal balance validation,
  and normal-balance calculation.
- `cukaccount_rules.expected.txt`: expected stdout for regression checks.

## Run
From the PusingCuk repository root, run the reference interpreter against
`apps/accounting/cukaccount_rules.cuk` using the same invocation documented
in the root README for a `.cuk` program.

## Scope and safety
- No imports/modules are assumed; current language spec says system modules are
  not available in the native runtime.
- This is a deterministic domain prototype, not a replacement for SQLite,
  audit trail, period closing, tax, sharia accounting review, or the production
  Dart posting path.
- Do not use binary floating point for production money. These rules accept
  numeric values and are for semantic/conformance learning until exact integer
  constraints are enforced end-to-end.
