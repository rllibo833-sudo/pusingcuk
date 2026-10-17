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

`platform_bridge.py` is a capability allowlist/dispatcher with injected handlers. It fails closed when an operation has no handler and rejects unknown operations and request shapes. It is **not yet a live SQLite, secure-storage, Android backup or restore adapter**. Do not treat a successful dispatcher test as evidence that persistence is active.

## Known implementation boundaries

- `.cuk` remains the source of domain rules; the UI runtime does not move business rules to Dart.
- The rendered UI is an executable interaction prototype, not yet wired to the bridge's database operations. Save/post/report actions must not be considered persisted or production-ready.
- Before production, implement and test the SQLite adapter with atomic journal posting, idempotency, audit trail, period-lock enforcement and migration/restore tests.
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
