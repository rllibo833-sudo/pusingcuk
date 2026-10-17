# CukAccount .cuk runtime slice

## Render the frontend

From the repository root:

```sh
python tools/cuk_ui_runtime.py apps/accounting/cukaccount_frontend.cuk --output apps/accounting/dist/index.html
```

With Node dependencies installed, launch the rendered screen in Electron:

```sh
cd apps/accounting
npm run start:cuk-ui
```

The frontend screen schema (navigation, labels, fields, actions, reports and theme) lives in `cukaccount_frontend.cuk`. The small Python renderer validates directives and emits responsive HTML; the HTML includes keyboard-focus styles, navigation, theme switching and required-field / basic debit-credit feedback. The regular `npm start` continues to launch the existing accounting MVP.

## Backend domain rules

`cukaccount_backend.cuk` contains deterministic rules for journal balance, normal account balances, open-period/date validation, report-category classification, basic tax arithmetic and preliminary sharia review flags. CI runs the reference interpreter and compares stdout with `cukaccount_backend.expected.txt`.

Tax output is arithmetic only, not tax advice or a statement of the applicable Indonesian tax rate. The sharia function only flags transaction attributes for human review; it does not issue a religious or compliance ruling.

## Platform bridge status

`platform_bridge.py` is a capability allowlist/dispatcher with injected handlers. It fails closed when an operation has no handler and rejects unknown operations and request shapes. The typed dispatcher now has an SQLite reference adapter (`sqlite_store.py`), atomic draft/post transactions, integer-Rupiah validation, idempotency keys, period locking, general-ledger running balances, and append-only audit events. `db.post_journal` invokes `validasi_jurnal` from `cukaccount_backend.cuk` through the reference interpreter before the SQLite commit; SQLite repeats critical invariant checks as defense in depth. Electron UI actions call a narrow preload IPC method which forwards bounded JSON to `platform_bridge_cli.py`. This is a desktop development vertical slice, **not yet an Android-native bridge**; secure-store, encrypted backup/restore, account/period setup UI, and device testing remain open.

## Known implementation boundaries

- `.cuk` remains the source of domain rules; the UI runtime does not move business rules to Dart.
- The rendered UI can load account choices, save a two-line journal draft, and request posting through the typed bridge. Posting is gated by live `.cuk` interpreter validation and an atomic SQLite transaction. UI report views and period close preview are not all wired to data yet; the basic ledger adapter exists, but the complete report UI is still open.
- Before production, add versioned migrations, chart-of-accounts and period setup, full report reconciliation, backup/restore and migration tests, and platform-native Android storage.
- Integrate bridge requests through a narrowly scoped host API, not arbitrary SQL or unrestricted filesystem access.
- Add cross-runtime conformance for these new backend rules before declaring them portable to JavaScript/native runtime.
- Use integer Rupiah for persisted amounts; do not use floating-point tax calculations for financial posting. Tax and sharia policies need separately reviewed, versioned rules.

## Regression tests

```sh
python -m unittest tests.test_cuk_ui_runtime tests.test_platform_bridge -v
python pusingcuk_new.py --check apps/accounting/cukaccount_frontend.cuk
python pusingcuk_new.py --check apps/accounting/cukaccount_backend.cuk
python pusingcuk_new.py apps/accounting/cukaccount_backend.cuk
```


## Typed bridge, storage and diagnostic repair loop (branch `warung-pusingcuk`)

- `platform_bridge.py` validates the contract version, request ID, operation allowlist, and per-operation field schemas; extra/missing fields fail closed.
- `sqlite_store.py` uses SQLite transactions for draft creation and posting. Posting uses `BEGIN IMMEDIATE`, verifies open period, active accounts, at least two lines, integer Rupiah and debit=credit, writes the posting audit event in the same transaction, and supports an idempotency key. A failed write rolls back both journal state and audit write.
- `cuk_domain.py` calls the real `.cuk` function through `pusingcuk_new.py`; `db.post_journal` denies posting if compilation/runtime fails or `.cuk` returns a rejection. Python storage validation is a second guard, not a replacement for `.cuk`.
- `cuk-ui-preload.cjs` exposes only a typed IPC request method; `cuk-ui-main.cjs` rejects non-local callers and oversized messages, invokes a fixed CLI without a shell, and stores the database under Electron's app-data directory. This host currently assumes a Python runtime is installed and is **not an Android APK integration**.
- `tools/diagnostic_repair_loop.py` runs syntax and runtime checks with a timeout, hashes source, compares locked output fixtures, emits stable diagnostic codes and manual-only repair suggestions. It never auto-edits source or merges. This is a testable diagnostic handoff for the AI repair workflow, not proof that a local AI model has been connected.
- Regression coverage: `tests.test_sqlite_store`, `tests.test_typed_bridge_integration`, and `tests.test_diagnostic_repair_loop`. CI evidence must be checked for the current branch head before treating this slice as green.
