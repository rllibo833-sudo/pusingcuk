"""Capability policy and resource accounting for the PusingCuk VM.

This module is a VM-level guardrail, NOT an operating-system security boundary.
No file/network/process/environment operation is exposed by this module itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time
from typing import Iterable


class CapabilityDenied(PermissionError):
    """Raised when a VM operation has not been explicitly granted."""


class ResourceLimitExceeded(RuntimeError):
    """Raised when a VM resource budget is exhausted."""


@dataclass(frozen=True)
class Permission:
    capability: str
    target: str | None = None


_ALLOWED_CAPABILITIES = {"baca", "tulis", "jaringan", "proses", "env"}


def parse_permission(spec: str) -> Permission:
    """Parse e.g. 'baca:./data', 'jaringan:api.example', or 'env:HOME'."""
    if not isinstance(spec, str) or not spec:
        raise ValueError("izin kosong")
    capability, separator, target = spec.partition(":")
    if capability not in _ALLOWED_CAPABILITIES:
        raise ValueError(f"kapabilitas tidak dikenal: {capability}")
    if capability == "env" and (not separator or not target):
        raise ValueError("izin env harus menyebut nama variabel")
    if capability in {"baca", "tulis", "jaringan", "proses"} and (not separator or not target):
        raise ValueError(f"izin {capability} harus menyebut target")
    if target and "\x00" in target:
        raise ValueError("target izin mengandung NUL")
    return Permission(capability, target if separator else None)


class CapabilityPolicy:
    """Default-deny policy. Grants are exact; file paths are confined to a granted root."""

    def __init__(self, permissions: Iterable[str | Permission] = (), *, cwd: str | Path | None = None):
        self.cwd = Path(cwd or Path.cwd()).resolve()
        parsed = [p if isinstance(p, Permission) else parse_permission(p) for p in permissions]
        self.permissions = tuple(parsed)

    def require(self, capability: str, target: str | None = None) -> None:
        if capability not in _ALLOWED_CAPABILITIES:
            raise CapabilityDenied(f"kapabilitas tidak dikenal/ditolak: {capability}")
        for permission in self.permissions:
            if permission.capability != capability:
                continue
            if capability in {"baca", "tulis"}:
                if target is None:
                    continue
                root = (self.cwd / permission.target).resolve()
                requested = (self.cwd / target).resolve()
                try:
                    requested.relative_to(root)
                except ValueError:
                    continue
                return
            if permission.target == target:
                return
        suffix = f":{target}" if target is not None else ""
        raise CapabilityDenied(f"akses ditolak (default-deny): {capability}{suffix}")

    def resolve_file(self, capability: str, target: str) -> Path:
        if capability not in {"baca", "tulis"}:
            raise CapabilityDenied(f"bukan kapabilitas file: {capability}")
        self.require(capability, target)
        return (self.cwd / target).resolve()


def estimate_size(value, seen=None) -> int:
    """Conservative-ish accounting estimate; not a hard process RSS limit."""
    import sys

    if seen is None:
        seen = set()
    ident = id(value)
    if ident in seen:
        return 0
    seen.add(ident)
    size = sys.getsizeof(value)
    if isinstance(value, dict):
        size += sum(estimate_size(k, seen) + estimate_size(v, seen) for k, v in value.items())
    elif isinstance(value, (list, tuple, set, frozenset)):
        size += sum(estimate_size(item, seen) for item in value)
    elif isinstance(value, (str, bytes, bytearray)):
        pass
    return size


class ResourceBudget:
    """Fuel, elapsed-time, and VM-visible object budget checks."""

    def __init__(self, *, fuel: int = 100_000, memory_bytes: int = 16 * 1024 * 1024,
                 time_seconds: float = 2.0):
        if isinstance(fuel, bool) or not isinstance(fuel, int) or fuel < 1:
            raise ValueError("fuel harus integer positif")
        if isinstance(memory_bytes, bool) or not isinstance(memory_bytes, int) or memory_bytes < 1:
            raise ValueError("batas memori harus integer positif")
        if isinstance(time_seconds, bool) or not isinstance(time_seconds, (int, float)) or time_seconds <= 0:
            raise ValueError("batas waktu harus positif")
        self.fuel_limit = fuel
        self.memory_limit = memory_bytes
        self.deadline = time.monotonic() + float(time_seconds)
        self.steps = 0

    def tick(self, *live_values) -> None:
        self.steps += 1
        if self.steps > self.fuel_limit:
            raise ResourceLimitExceeded("batas fuel VM tercapai")
        if time.monotonic() > self.deadline:
            raise ResourceLimitExceeded("batas waktu VM tercapai")
        estimated = sum(estimate_size(value) for value in live_values)
        if estimated > self.memory_limit:
            raise ResourceLimitExceeded(
                f"batas memori objek VM tercapai ({estimated} > {self.memory_limit} byte)"
            )
