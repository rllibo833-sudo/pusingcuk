# Python-Free Score

The Python-Free Score measures the checked-in native C runtime's fixture coverage, not whether the build or test toolchain itself uses Python and not whether the entire language is implemented without Python.

**Formula:** native C fixtures that pass ÷ all fixtures in the active manifest × 100. Fixtures marked unsupported remain in the denominator and do not count as passed. The value is a coverage score, not a security certification or a claim of full backend parity.

## History

<!-- BEGIN GENERATED PYTHON-FREE SCORE HISTORY -->
| Date | Python-Free Score (native C) | Commit | CI evidence |
|---|---:|---|---|
| 2026-10-18 | 96.10% (74/77) | [`31a39d4`](https://github.com/rllibo833-sudo/pusingcuk/commit/31a39d416245a1c500c0945e0cdd66e00ae6b322) | [fixture matrix](https://github.com/rllibo833-sudo/pusingcuk/actions/runs/39137355887) |
<!-- END GENERATED PYTHON-FREE SCORE HISTORY -->

This is the first tracked snapshot in this history. Earlier scores are not backfilled unless a dated, reproducible source summary and CI evidence can be identified. Each new baseline score must add a dated record to `tests/conformance/python_free_score_history.json`; CI checks that the newest record matches the checked-in baseline summary.

## Evidence and limitations

- Canonical fixture list: [`tests/conformance/manifest.json`](../tests/conformance/manifest.json)
- Baseline counts: [`tests/conformance/baseline_summary.json`](../tests/conformance/baseline_summary.json)
- Current history records link to the corresponding commit and fixture-matrix workflow run.
- Native C can run after compilation without Python, but this score does not claim that the compiler, build, CI, or every PusingCuk backend is Python-free.
