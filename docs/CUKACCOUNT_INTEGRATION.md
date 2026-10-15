# CukAccount integration contract

PusingCuk's integration branch for CukAccount is named in-this-economy. Keep this branch separate from main until reviewed and tested.

## Boundary
- PusingCuk supplies reviewed, deterministic .cuk rules and synthetic regression fixtures.
- CukAccount remains the source of truth for accounts, accounting periods, journals, posting, and reports.
- AI-generated output is advisory only. It must not post, mutate, delete, or commit financial records.
- The journal-balance rule checks supplied totals only. It does not validate individual journal lines, account status, period status, or posting permissions.
- Cross-repository CI should pin the exact PusingCuk commit SHA rather than depend on a moving branch ref.

## Accounting example
The file examples/accounting/report_equation.cuk is a synthetic educational fixture for profit calculation and the basic accounting equation. It is not a complete financial-report engine or a claim of compliance with SAK/PSAK or Islamic accounting standards.

## Safety
Do not put real customer names, account numbers, balances, credentials, or private company data in fixtures or the public knowledge index.
