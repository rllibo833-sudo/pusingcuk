# CukAccount integration contract

CukAccount integration work is maintained against PusingCuk `main`; the previously documented `in-this-economy` branch is not present in the current repository branch list. Do not rely on that stale branch name or create another branch as part of this workflow.

## Why this project exists
CukAccount is the first real application project used to strengthen `.cuk` as an independent programming language and to train/evaluate the currently local PusingCuk AI. The app is a practical testbed for compiler diagnostics, deterministic language rules, integration fixtures, and regression cases—not a claim that CukAccount is already compiled entirely from `.cuk`.

“Training” in the current stage means improving the local assistant's grounded project context, examples, registered rules, and measurable evaluations. Do not claim model-weight fine-tuning unless a reproducible fine-tuning pipeline and its evaluation evidence exist.

## Boundary
- PusingCuk supplies reviewed, deterministic .cuk rules and synthetic regression fixtures.
- CukAccount remains the source of truth for accounts, accounting periods, journals, posting, and reports.
- AI-generated output is advisory only. It must not post, mutate, delete, or commit financial records.
- The journal-balance rule checks supplied totals only. It does not validate individual journal lines, account status, period status, or posting permissions.
- Cross-repository CI should pin the exact PusingCuk commit SHA rather than depend on a moving branch ref.

## Current Android build boundary

The workflow `.github/workflows/android-studio-apk.yml` builds the separate PusingCuk Studio APK and is manual-only. A successful Studio build is not evidence of a CukAccount APK or accounting functionality. The current generic Android compiler backend emits a small Activity for a limited .cuk subset; it does not by itself provide CukAccount navigation, persistent accounting storage, journal posting, audit records, or reconciled reports.

Do not mark the CukAccount Android target complete until a dedicated artifact has the expected CukAccount application identity and normal/professional modes, offline persistence, journal posting, and reports verified against the same synthetic domain cases used by the .cuk rules. Keep financial posting authority in the app's deterministic domain layer; PusingCuk AI remains advisory.

## Accounting example
The file examples/accounting/report_equation.cuk is a synthetic educational fixture for profit calculation and the basic accounting equation. It is not a complete financial-report engine or a claim of compliance with SAK/PSAK or Islamic accounting standards.

## Feedback loop and acceptance
1. Keep fixtures synthetic and specify expected outputs.
2. Let the local PusingCuk AI propose or explain `.cuk` source; treat its output as untrusted until checked.
3. Run compiler/check tooling and use the actual structured diagnostics, not model guesses.
4. Run deterministic fixtures and language conformance tests.
5. Convert reproducible failures into regression cases only after a maintainer reviews the expected behavior.
6. Synchronize accepted changes across the language contract, tests, CukAccount bridge pin, and docs.

Acceptance for stronger integration requires evidence that a `.cuk` rule's expected output maps to a corresponding domain case in CukAccount. Passing the current equation fixture alone does not establish full accounting semantics or backend parity.

## Safety
Do not put real customer names, account numbers, balances, credentials, or private company data in fixtures or the public knowledge index. Use synthetic examples only.

## Financial conformance fixture and expected output

`tests/conformance/cukaccount_financial_cases.cuk` is a shared, synthetic cross-runtime fixture. Its exact stdout contract is:

```text
CUKACCOUNT_VALID_BALANCED
CUKACCOUNT_INVALID_UNBALANCED
CUKACCOUNT_INVALID_ZERO
CUKACCOUNT_INVALID_NEGATIVE
CUKACCOUNT_BOUNDARY_MAX
```

Both the reference interpreter and native C runtime must match that output. The registered local-AI tool `journal_balance_check` has a separate schema-level contract: integer IDR totals from 0 through Rp1,000,000,000,000 are accepted as inputs; negatives, over-limit values, booleans, floats, strings, nulls, collections, missing fields, and extra fields are rejected without coercion. The .cuk fixture tests language semantics; the registered-tool tests check input validation and rule execution. Neither is a replacement for CukAccount's Dart/SQLite posting and report tests.

CukAccount CI should run this exact fixture from its pinned PusingCuk checkout, compare the complete stdout to the expected lines above, and run the registered-rule regression suite. The independent Dart/SQLite regression suite remains the source of truth for actual journal and report outcomes.
