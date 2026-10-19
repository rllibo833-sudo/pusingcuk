"""Offline, deterministic source repair for the PusingCuk repair loop.

This adapter is deliberately not an AI model. It applies only explicitly
registered, exact source substitutions selected by a stable rule identifier.
Ambiguous or missing matches fail closed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class ExactRepairRule:
    """A maintainer-reviewed, single-occurrence source transformation."""
    rule_id: str
    before: str
    after: str

    def __post_init__(self) -> None:
        if not self.rule_id.strip():
            raise ValueError("rule_id must not be empty")
        if not self.before:
            raise ValueError("before must not be empty")
        if self.before == self.after:
            raise ValueError("repair rule must change source")


class OfflineRepairAdapter:
    """Implement RepairAdapter without network access, credentials, or a model.

    The request is an exact rule ID, not free-form natural language. This
    makes the behavior deterministic and auditable instead of pretending a
    rule engine understands arbitrary repair requests.
    """

    def __init__(self, rules: Mapping[str, ExactRepairRule]) -> None:
        self._rules = dict(rules)
        for key, rule in self._rules.items():
            if key != rule.rule_id:
                raise ValueError(f"rule key does not match rule_id: {key}")

    def propose(self, request: str, current_source: str, diagnostics: str) -> str:
        del diagnostics  # Diagnostics are retained by the outer repair-loop log.
        try:
            rule = self._rules[request]
        except KeyError as exc:
            raise ValueError(f"unknown offline repair rule: {request}") from exc

        matches = current_source.count(rule.before)
        if matches == 0:
            raise ValueError(f"rule {request} did not match source")
        if matches != 1:
            raise ValueError(
                f"rule {request} is ambiguous: expected one match, found {matches}"
            )
        proposed = current_source.replace(rule.before, rule.after, 1)
        if proposed == current_source:
            raise ValueError(f"rule {request} produced unchanged source")
        return proposed
