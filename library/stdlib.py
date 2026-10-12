"""Explicit, dependency-free registry for Pusingcuk standard-library builtins.

The registry is a foundation for interpreter/compiler integration. It never
evaluates source text and does not expose filesystem, network, or process APIs.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
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


def _numeric(name: str, value: Any) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(name + "() membutuhkan angka, bukan boolean atau tipe lain")
    if isinstance(value, float) and not math.isfinite(value):
        raise TypeError(name + "() membutuhkan angka finite")
    return value


def _math_result(name: str, value: float) -> float:
    if not math.isfinite(value):
        raise ValueError(name + "() menghasilkan angka non-finite")
    return value


def _abs(value: Any) -> int | float:
    return abs(_numeric("mutlak", value))


def _min(a: Any, b: Any) -> int | float:
    return min(_numeric("minimum", a), _numeric("minimum", b))


def _max(a: Any, b: Any) -> int | float:
    return max(_numeric("maksimum", a), _numeric("maksimum", b))


def _round(value: Any) -> int:
    return round(_numeric("bulatkan", value))


def _sqrt(value: Any) -> float:
    value = _numeric("akar", value)
    if value < 0:
        raise ValueError("akar() membutuhkan angka non-negatif")
    return _math_result("akar", math.sqrt(value))


def _floor(value: Any) -> int:
    return math.floor(_numeric("bawah", value))


def _ceil(value: Any) -> int:
    return math.ceil(_numeric("atas", value))


def _pow(a: Any, b: Any) -> float:
    return _math_result("pangkat", math.pow(_numeric("pangkat", a), _numeric("pangkat", b)))


def _sin(value: Any) -> float:
    return _math_result("sinus", math.sin(_numeric("sinus", value)))


def _cos(value: Any) -> float:
    return _math_result("kosinus", math.cos(_numeric("kosinus", value)))


def _stat_values(name: str, value: Any) -> list[int | float]:
    if not isinstance(value, list) or not value:
        raise TypeError(name + "() membutuhkan daftar angka yang tidak kosong")
    values = [_numeric(name, item) for item in value]
    if any(
        (isinstance(item, int) and abs(item) > 9007199254740991)
        or (isinstance(item, float) and item.is_integer() and abs(item) > 9007199254740991)
        for item in values
    ):
        raise ValueError(name + "() menolak integer di luar rentang aman lintas target")
    return values


def _stat_result(name: str, value: float) -> int | float:
    value = _math_result(name, value)
    if value.is_integer() and abs(value) <= 9007199254740991:
        return int(value)
    return value


def _mean(value: Any) -> int | float:
    values = _stat_values("rata_rata", value)
    try:
        count = len(values)
        return _stat_result("rata_rata", sum(item / count for item in values))
    except OverflowError as exc:
        raise ValueError("rata_rata() menghasilkan angka di luar rentang finite") from exc


def _median(value: Any) -> int | float:
    values = sorted(_stat_values("median", value))
    middle = len(values) // 2
    if len(values) % 2:
        result = values[middle]
        if isinstance(result, int) and abs(result) <= 9007199254740991:
            return result
        return _stat_result("median", float(result))
    return _stat_result("median", values[middle - 1] / 2 + values[middle] / 2)


BUILTINS: dict[str, Builtin] = {
    "panjang": Builtin("panjang", ("nilai",), "Jumlah item pada teks, daftar, atau peta.", len),
    "teks": Builtin("teks", ("nilai",), "Konversi nilai menjadi teks.", str),
    "bilangan": Builtin("bilangan", ("nilai",), "Konversi nilai menjadi bilangan bulat.", _to_int),
    "desimal": Builtin("desimal", ("nilai",), "Konversi nilai menjadi bilangan desimal.", _to_float),
    "logika": Builtin("logika", ("nilai",), "Konversi nilai menjadi benar/salah.", _to_bool),
    "mutlak": Builtin("mutlak", ("angka",), "Nilai absolut sebuah angka.", _abs),
    "minimum": Builtin("minimum", ("angka1", "angka2"), "Nilai terkecil dari dua angka.", _min),
    "maksimum": Builtin("maksimum", ("angka1", "angka2"), "Nilai terbesar dari dua angka.", _max),
    "bulatkan": Builtin("bulatkan", ("angka",), "Pembulatan ties-to-even ke bilangan terdekat.", _round),
    "akar": Builtin("akar", ("angka",), "Akar kuadrat angka non-negatif.", _sqrt),
    "bawah": Builtin("bawah", ("angka",), "Pembulatan ke bawah menuju integer.", _floor),
    "atas": Builtin("atas", ("angka",), "Pembulatan ke atas menuju integer.", _ceil),
    "pangkat": Builtin("pangkat", ("basis", "eksponen"), "Pangkat numerik dengan hasil finite.", _pow),
    "sinus": Builtin("sinus", ("radian",), "Sinus sudut dalam radian.", _sin),
    "kosinus": Builtin("kosinus", ("radian",), "Kosinus sudut dalam radian.", _cos),
    "rata_rata": Builtin("rata_rata", ("daftar",), "Rata-rata aritmetika daftar angka finite yang tidak kosong.", _mean),
    "median": Builtin("median", ("daftar",), "Median daftar angka finite yang tidak kosong.", _median),
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
