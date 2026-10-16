"""Dependency-free Pusingcuk builtin registry backed by the shared contract."""
from __future__ import annotations

from dataclasses import dataclass
import math
import html
import json
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
    converted = float(value)
    if not math.isfinite(converted):
        raise ValueError("desimal() membutuhkan angka finite")
    return converted


def _to_bool(value: Any) -> bool:
    return bool(value)


def _to_text(value: Any) -> str:
    """Convert a value to Pusingcuk text, not host-language boolean spelling."""
    if value is True:
        return "okelah"
    if value is False:
        return "tidak"
    return str(value)


def _json_validate(value: Any, path: str = "$") -> Any:
    """Reject values that cannot be represented consistently across targets."""
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, int):
        if abs(value) > _MAX_SAFE_INTEGER:
            raise ValueError(f"JSON integer di luar rentang aman: {path}")
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"JSON angka non-finite: {path}")
        return value
    if isinstance(value, list):
        return [_json_validate(item, f"{path}[{index}]") for index, item in enumerate(value)]
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise TypeError(f"kunci objek JSON harus teks: {path}")
        return {key: _json_validate(item, f"{path}.{key}") for key, item in value.items()}
    raise TypeError(f"tipe tidak didukung JSON: {type(value).__name__} pada {path}")


def _json_text(value: Any) -> str:
    return json.dumps(_json_validate(value), ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _json_read(value: Any) -> Any:
    if not isinstance(value, str):
        raise TypeError("json_baca() membutuhkan teks JSON")
    try:
        decoded = json.loads(value, parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)))
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"teks JSON tidak valid: {exc}") from exc
    return _json_validate(decoded)


def _html_escape(value: Any) -> str:
    return html.escape(_to_text(value), quote=True)


def _csv_row(value: Any) -> str:
    if not isinstance(value, list):
        raise TypeError("csv_baris() membutuhkan daftar")
    fields = []
    for item in value:
        if item is None or isinstance(item, (str, bool)):
            field = _to_text(item)
        elif isinstance(item, (int, float)) and not isinstance(item, bool) and math.isfinite(item):
            if isinstance(item, int) and abs(item) > _MAX_SAFE_INTEGER:
                raise ValueError("csv_baris() integer di luar rentang aman")
            field = str(item)
        else:
            raise TypeError("csv_baris() hanya menerima nilai skalar")
        if any(char in field for char in (",", '"', chr(13), chr(10))):
            field = '"' + field.replace('"', '""') + '"'
        fields.append(field)
    return ",".join(fields)


def _numeric(name: str, value: Any) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(name + "() membutuhkan angka finite, bukan boolean atau tipe lain")
    if isinstance(value, float) and not math.isfinite(value):
        raise TypeError(name + "() membutuhkan angka finite")
    return value


def _math_result(name: str, value: float) -> float:
    if not math.isfinite(value):
        raise ValueError(name + "() menghasilkan angka non-finite")
    return value


_MAX_SAFE_INTEGER = 9007199254740991


def _canonical_math_result(name: str, value: float) -> int | float:
    """Normalize integral math results to a common safe integer representation."""
    value = _math_result(name, value)
    if value.is_integer() and abs(value) <= _MAX_SAFE_INTEGER:
        return int(value)
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


def _sqrt(value: Any) -> int | float:
    value = _numeric("akar", value)
    if value < 0:
        raise ValueError("akar() domain tidak valid: angka harus non-negatif")
    try:
        result = math.sqrt(value)
    except OverflowError as exc:
        raise ValueError("akar() menghasilkan angka non-finite") from exc
    return _canonical_math_result("akar", result)


def _floor(value: Any) -> int:
    return math.floor(_numeric("bawah", value))


def _ceil(value: Any) -> int:
    return math.ceil(_numeric("atas", value))


def _pow(a: Any, b: Any) -> int | float:
    base = _numeric("pangkat", a)
    exponent = _numeric("pangkat", b)
    if base < 0 and not isinstance(exponent, int) and not exponent.is_integer():
        raise ValueError("pangkat() domain tidak valid")
    if base == 0 and exponent < 0:
        raise ValueError("pangkat() domain tidak valid")
    try:
        result = math.pow(base, exponent)
    except ValueError as exc:
        raise ValueError("pangkat() domain tidak valid") from exc
    except OverflowError as exc:
        raise ValueError("pangkat() menghasilkan angka non-finite") from exc
    return _canonical_math_result("pangkat", result)


def _sin(value: Any) -> int | float:
    return _canonical_math_result("sinus", math.sin(_numeric("sinus", value)))


def _cos(value: Any) -> int | float:
    return _canonical_math_result("kosinus", math.cos(_numeric("kosinus", value)))


def _log(value: Any) -> int | float:
    value = _numeric("logaritma", value)
    if value <= 0:
        raise ValueError("logaritma() domain tidak valid: angka harus lebih besar dari nol")
    return _canonical_math_result("logaritma", math.log(value))


def _log10(value: Any) -> int | float:
    value = _numeric("log10", value)
    if value <= 0:
        raise ValueError("log10() domain tidak valid: angka harus lebih besar dari nol")
    return _canonical_math_result("log10", math.log10(value))


def _stat_values(name: str, value: Any) -> list[int | float]:
    if not isinstance(value, list) or not value:
        raise TypeError(name + "() membutuhkan daftar angka yang tidak kosong")
    values = [_numeric(name, item) for item in value]
    if any(
        (isinstance(item, int) and abs(item) > _MAX_SAFE_INTEGER)
        or (isinstance(item, float) and item.is_integer() and abs(item) > _MAX_SAFE_INTEGER)
        for item in values
    ):
        raise ValueError(name + "() menolak integer di luar rentang aman lintas target")
    return values


def _stat_result(name: str, value: float) -> int | float:
    return _canonical_math_result(name, value)


def _mean(value: Any) -> int | float:
    values = _stat_values("rata_rata", value)
    count = len(values)
    # Explicit ordered accumulation keeps behavior stable across Python releases
    # and matches the native C runtime instead of depending on host sum() policy.
    total = 0.0
    for item in values:
        total += item / count
    return _stat_result("rata_rata", total)


def _median(value: Any) -> int | float:
    values = sorted(_stat_values("median", value))
    middle = len(values) // 2
    if len(values) % 2:
        result = values[middle]
        if isinstance(result, int) and abs(result) <= 9007199254740991:
            return result
        return _stat_result("median", float(result))
    return _stat_result("median", values[middle - 1] / 2 + values[middle] / 2)



def _sum(value: Any) -> int | float:
    """Sum a list with shared finite-number and safe-integral-result rules."""
    if not isinstance(value, list):
        raise TypeError("jumlah() membutuhkan daftar angka finite")
    total = 0.0
    for item in value:
        item = _numeric("jumlah", item)
        if (
            (isinstance(item, int) and abs(item) > _MAX_SAFE_INTEGER)
            or (
                isinstance(item, float)
                and item.is_integer()
                and abs(item) > _MAX_SAFE_INTEGER
            )
        ):
            raise ValueError("jumlah() menolak angka di luar rentang aman lintas target")
        total += float(item)
        if not math.isfinite(total):
            raise ValueError("jumlah() menghasilkan angka non-finite")
        if total.is_integer() and abs(total) > _MAX_SAFE_INTEGER:
            raise ValueError("jumlah() menghasilkan integer di luar rentang aman lintas target")
    if total.is_integer():
        if abs(total) > _MAX_SAFE_INTEGER:
            raise ValueError("jumlah() menghasilkan integer di luar rentang aman lintas target")
        return int(total)
    return total

_IMPLEMENTATIONS: dict[str, Callable[..., Any]] = {
    "length": len,
    "text": _to_text,
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
    "log": _log,
    "log10": _log10,
    "sin": _sin,
    "cos": _cos,
    "mean": _mean,
    "median": _median,
    "sum": _sum,
    "json_text": _json_text,
    "json_read": _json_read,
    "html_escape": _html_escape,
    "csv_row": _csv_row,
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
