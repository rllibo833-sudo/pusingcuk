"""Dependency-free Pusingcuk builtin registry backed by the shared contract."""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Any

from library.builtin_contract import BUILTIN_BY_NAME


@dataclass(frozen=True)
class Builtin:
    name: str
    parameters: tuple[str, ...]
    description: str
    function: Callable[..., Any]
    min_args: int
    max_args: int


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


def _range(*args: Any) -> list[int]:
    if not 1 <= len(args) <= 3 or any(not isinstance(x, int) or isinstance(x, bool) for x in args):
        raise TypeError("rentang() membutuhkan 1-3 bilangan bulat")
    if len(args) == 3 and args[2] == 0:
        raise ValueError("langkah rentang tidak boleh nol")
    result = range(*args)
    if len(result) > 10000:
        raise ValueError("rentang melewati batas 10000 item")
    return list(result)


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


_IMPLEMENTATIONS: dict[str, Callable[..., Any]] = {
    "length": len,
    "text": str,
    "integer": _to_int,
    "float": _to_float,
    "boolean": _to_bool,
    "range": _range,
    "abs": _abs,
    "min": _min,
    "max": _max,
    "round": _round,
    "sqrt": _sqrt,
    "floor": _floor,
    "ceil": _ceil,
    "pow": _pow,
    "sin": _sin,
    "cos": _cos,
    "mean": _mean,
    "median": _median,
}

_missing = {entry["implementation"] for entry in BUILTIN_BY_NAME.values()} - set(_IMPLEMENTATIONS)
if _missing:
    raise RuntimeError("implementasi builtin hilang: " + ", ".join(sorted(_missing)))

BUILTINS: dict[str, Builtin] = {
    name: Builtin(
        name=name,
        parameters=tuple(entry["parameters"]),
        description=entry["description"],
        function=_IMPLEMENTATIONS[entry["implementation"]],
        min_args=entry["min_args"],
        max_args=entry["max_args"],
    )
    for name, entry in BUILTIN_BY_NAME.items()
}


def get_builtin(name: str) -> Builtin | None:
    """Return builtin metadata by exact name, or None when unknown."""
    return BUILTINS.get(name)


def call_builtin(name: str, *args: Any) -> Any:
    """Call a registered builtin with contract-defined arity and type validation."""
    builtin = get_builtin(name)
    if builtin is None:
        raise NameError(f"fungsi bawaan tidak dikenal: {name}")
    if not builtin.min_args <= len(args) <= builtin.max_args:
        if builtin.min_args == builtin.max_args:
            expected = str(builtin.min_args)
        else:
            expected = f"{builtin.min_args}-{builtin.max_args}"
        raise TypeError(f"{name}() membutuhkan {expected} argumen")
    return builtin.function(*args)
