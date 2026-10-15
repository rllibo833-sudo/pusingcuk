# CukAccount integration contract

PusingCuk's integration branch for CukAccount is named `in-this-economy`. Keep this branch separate from `main` until reviewed and tested.

## Why this project exists
CukAccount is the first real application project used to strengthen `.cuk` as an independent programming language and to train/evaluate the currently local PusingCuk AI. The app is a practical testbed for compiler diagnostics, deterministic language rules, integration fixtures, and regression cases—not a claim that CukAccount is already compiled entirely from `.cuk`.

“Training” in the current stage means improving the local assistant's grounded project context, examples, registered rules, and measurable evaluations. Do not claim model-weight fine-tuning unless a reproducible fine-tuning pipeline and its evaluation evidence exist.

## Boundary
- PusingCuk supplies reviewed, deterministic .cuk rules and synthetic regression fixtures.
- CukAccount remains the source of truth for accounts, accounting periods, journals, posting, and reports.
- AI-generated output is advisory only. It must not post, mutate, delete, or commit financial records.
- The journal-balance rule checks supplied totals only. It does not validate individual journal lines, account status, period status, or posting permissions.
- Cross-repository CI should pin the exact PusingCuk commit SHA rather than depend on a moving branch ref.

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
