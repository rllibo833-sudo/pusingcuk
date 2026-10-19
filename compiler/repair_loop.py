"""Evidence-gated, model-agnostic repair loop for PusingCuk AI."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable, Protocol


class RepairAdapter(Protocol):
    """Provider-neutral interface: model output is only a source proposal."""
    def propose(self, request: str, current_source: str, diagnostics: str) -> str: ...


@dataclass
class AttemptResult:
    attempt: int
    request: str
    dry_run: bool
    source_changed: bool
    fixture_added: bool
    compile_ok: bool
    differential_ok: bool
    accepted: bool
    reason: str
    diagnostics: str = ""
    fixture_id: str | None = None
    timestamp: str = ""


class RepairLoop:
    """Runs a proposal through injected evidence gates and logs every attempt.

    Does not persist source itself. The trusted caller must persist only after
    receiving an accepted result.
    """
    def __init__(self, adapter: RepairAdapter, *, compiler: Callable[[str], Any],
                 fixture_runner: Callable[[str, str | None], dict],
                 differential_runner: Callable[[str], dict], log_path: str | Path):
        self.adapter = adapter
        self.compiler = compiler
        self.fixture_runner = fixture_runner
        self.differential_runner = differential_runner
        self.log_path = Path(log_path)
        self.attempt_count = 0

    def _log(self, result: AttemptResult) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(asdict(result), ensure_ascii=False, sort_keys=True) + "\n")

    def attempt(self, request: str, current_source: str, diagnostics: str = "",
                *, fixture_id: str | None = None, dry_run: bool = False) -> AttemptResult:
        self.attempt_count += 1
        proposed = ""
        changed = fixture_added = compile_ok = differential_ok = False
        reason = ""
        error = ""
        try:
            proposed = self.adapter.propose(request, current_source, diagnostics)
            if not isinstance(proposed, str):
                raise TypeError("adapter must return source text")
            changed = proposed != current_source
            if not changed:
                reason = "proposal unchanged"
            else:
                self.compiler(proposed)
                compile_ok = True
                fixture_result = self.fixture_runner(proposed, fixture_id)
                if not isinstance(fixture_result, dict):
                    raise TypeError("fixture runner must return a result mapping")
                fixture_added = fixture_result.get("added") is True
                fixture_id = fixture_result.get("fixture_id", fixture_id)
                if not fixture_added:
                    reason = "rejected: no new fixture was added"
                else:
                    matrix = self.differential_runner(proposed)
                    if not isinstance(matrix, dict):
                        raise TypeError("differential runner must return a result mapping")
                    differential_ok = (
                        matrix.get("ok") is True
                        and matrix.get("regressions") == []
                        and matrix.get("complete") is True
                    )
                    if not differential_ok:
                        reason = "rejected: full differential matrix incomplete, failed, or regressed"
                    elif dry_run:
                        reason = "dry-run: all gates passed; no source accepted or written"
                    else:
                        reason = "accepted by evidence gates; caller must persist explicitly"
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            reason = "rejected: validation or adapter exception"
        accepted = bool(
            changed and compile_ok and fixture_added and differential_ok
            and not dry_run and not error
        )
        result = AttemptResult(
            attempt=self.attempt_count, request=request, dry_run=dry_run,
            source_changed=changed, fixture_added=fixture_added, compile_ok=compile_ok,
            differential_ok=differential_ok, accepted=accepted, reason=reason,
            diagnostics=error, fixture_id=fixture_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._log(result)
        return result
