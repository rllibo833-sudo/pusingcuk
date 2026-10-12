"""Load and validate the canonical Pusingcuk builtin contract.

The JSON file is the metadata source of truth. Runtime implementations stay in
their respective backends; this module supplies names, arity, import allow-lists,
and target support metadata to every integration.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONTRACT_PATH = Path(__file__).with_name("builtin_contract.json")
_ALLOWED_STATES = {"supported", "unsupported", "not-claimed"}


class BuiltinContractError(ValueError):
    """The shared builtin contract is malformed or inconsistent."""


def _load() -> dict[str, Any]:
    try:
        data = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuiltinContractError(f"kontrak builtin tidak dapat dibaca: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise BuiltinContractError("schema_version kontrak builtin harus 1")
    builtins = data.get("builtins")
    if not isinstance(builtins, list) or not builtins:
        raise BuiltinContractError("builtins harus berupa daftar yang tidak kosong")

    seen: set[str] = set()
    for entry in builtins:
        if not isinstance(entry, dict):
            raise BuiltinContractError("setiap builtin harus berupa objek")
        name = entry.get("name")
        if not isinstance(name, str) or not name.isidentifier() or name in seen:
            raise BuiltinContractError(f"nama builtin kosong, tidak valid, atau duplikat: {name!r}")
        seen.add(name)
        parameters = entry.get("parameters")
        low, high = entry.get("min_args"), entry.get("max_args")
        if (not isinstance(parameters, list) or
                not all(isinstance(item, str) and item.isidentifier() for item in parameters) or
                not isinstance(low, int) or isinstance(low, bool) or
                not isinstance(high, int) or isinstance(high, bool) or
                low < 0 or high < low or high > len(parameters)):
            raise BuiltinContractError(f"metadata aritas tidak valid untuk {name}")
        if not isinstance(entry.get("description"), str) or not isinstance(entry.get("implementation"), str):
            raise BuiltinContractError(f"deskripsi/implementasi metadata tidak valid untuk {name}")
        backends = entry.get("backends")
        if not isinstance(backends, dict):
            raise BuiltinContractError(f"metadata backend hilang untuk {name}")
        for target, detail in backends.items():
            if not isinstance(detail, dict) or detail.get("status") not in _ALLOWED_STATES:
                raise BuiltinContractError(f"status backend tidak valid: {name}/{target}")
            helper = detail.get("helper")
            if detail["status"] == "supported" and target in {"js", "python"}:
                if not isinstance(helper, str) or not helper.isidentifier():
                    raise BuiltinContractError(f"helper backend hilang untuk {name}/{target}")

    by_name = {item["name"]: item for item in builtins}
    for mapping in data.get("python_builtins", []):
        if (not isinstance(mapping, dict) or
                not isinstance(mapping.get("source"), str) or
                mapping.get("target") not in by_name):
            raise BuiltinContractError("pemetaan builtin Python tidak valid")
    modules = data.get("python_modules")
    if not isinstance(modules, dict):
        raise BuiltinContractError("python_modules harus berupa objek")
    for module, spec in modules.items():
        if not isinstance(spec, dict):
            raise BuiltinContractError(f"metadata modul Python tidak valid: {module}")
        for section in ("functions", "constants"):
            values = spec.get(section, {})
            if not isinstance(values, dict):
                raise BuiltinContractError(f"{module}.{section} harus berupa objek")
            if section == "functions" and any(target not in by_name for target in values.values()):
                raise BuiltinContractError(f"pemetaan fungsi {module} menunjuk builtin yang tidak dikenal")
            if section == "constants" and any(not isinstance(value, str) for value in values.values()):
                raise BuiltinContractError(f"konstanta {module} harus berupa teks literal")
    return data


BUILTIN_CONTRACT = _load()
BUILTIN_BY_NAME = {item["name"]: item for item in BUILTIN_CONTRACT["builtins"]}
BUILTIN_NAMES = frozenset(BUILTIN_BY_NAME)
PYTHON_BUILTINS = {item["source"]: item["target"] for item in BUILTIN_CONTRACT["python_builtins"]}
PYTHON_MODULES = BUILTIN_CONTRACT["python_modules"]


def backend_builtins(target: str) -> dict[str, dict[str, Any]]:
    """Return only builtins the selected code backend explicitly implements."""
    if target not in {"js", "python"}:
        raise ValueError(f"backend builtin tidak dikenal: {target}")
    result = {}
    for name, entry in BUILTIN_BY_NAME.items():
        detail = entry["backends"].get(target, {})
        if detail.get("status") == "supported":
            result[name] = {
                "min_args": entry["min_args"],
                "max_args": entry["max_args"],
                "helper": detail["helper"],
            }
    return result


def imported_builtin(module: str, name: str) -> str | None:
    """Resolve one allow-listed function import without importing host modules."""
    return PYTHON_MODULES.get(module, {}).get("functions", {}).get(name)


def imported_constant(module: str, name: str) -> str | None:
    """Resolve one allow-listed numeric constant."""
    return PYTHON_MODULES.get(module, {}).get("constants", {}).get(name)
