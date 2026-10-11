"""Explicit, dependency-free registry for Pusingcuk standard-library builtins.

The registry is a foundation for interpreter/compiler integration. It never
evaluates source text and does not expose filesystem, network, or process APIs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any


@dataclass(frozen=True)
class Builtin:
    name: str
    parameters: tuple[str, ...]
    description: str
    function: Callable[..., Any]


def _to_int(value: Any) -> int:
    if isinstance(value, bool):
        raise TypeError("bool tidak dapat dikonversi menjadi int")
    return int(value)


def _to_float(value: Any) -> float:
    if isinstance(value, bool):
        raise TypeError("bool tidak dapat dikonversi menjadi float")
    return float(value)


def _to_bool(value: Any) -> bool:
    return bool(value)


BUILTINS: dict[str, Builtin] = {
    "panjang": Builtin("panjang", ("nilai",), "Jumlah item pada teks, daftar, atau peta.", len),
    "teks": Builtin("teks", ("nilai",), "Konversi nilai menjadi teks.", str),
    "bilangan": Builtin("bilangan", ("nilai",), "Konversi nilai menjadi bilangan bulat.", _to_int),
    "desimal": Builtin("desimal", ("nilai",), "Konversi nilai menjadi bilangan desimal.", _to_float),
    "logika": Builtin("logika", ("nilai",), "Konversi nilai menjadi benar/salah.", _to_bool),
    "mutlak": Builtin("mutlak", ("angka",), "Nilai absolut sebuah angka.", abs),
    "minimum": Builtin("minimum", ("angka1", "angka2"), "Nilai terkecil dari dua angka.", min),
    "maksimum": Builtin("maksimum", ("angka1", "angka2"), "Nilai terbesar dari dua angka.", max),
    "bulatkan": Builtin("bulatkan", ("angka",), "Pembulatan angka ke bilangan terdekat.", round),
}


def get_builtin(name: str) -> Builtin | None:
    """Return builtin metadata by exact name, or None when unknown."""
    return BUILTINS.get(name)


def call_builtin(name: str, *args: Any) -> Any:
    """Call a registered builtin with normal Python arity/type validation."""
    builtin = get_builtin(name)
    if builtin is None:
        raise NameError(f"fungsi bawaan tidak dikenal: {name}")
    return builtin.function(*args)
