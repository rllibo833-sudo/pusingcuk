"""Small, dependency-free type model for the Pusingcuk compiler.

This module intentionally does not alter interpreter semantics yet. Frontends can
use it for static checks before type information is wired into the IR.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class TypeKind(str, Enum):
    ANY = "any"
    VOID = "void"
    NULL = "null"
    BOOL = "bool"
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    LIST = "list"
    MAP = "map"
    OPTIONAL = "optional"
    RESULT = "result"
    STRUCT = "struct"
    ENUM = "enum"


@dataclass(frozen=True)
class Type:
    kind: TypeKind
    element: "Type | None" = None
    key: "Type | None" = None
    value: "Type | None" = None
    success: "Type | None" = None
    error: "Type | None" = None
    name: str | None = None
    fields: tuple[tuple[str, "Type"], ...] = ()
    variants: tuple[str, ...] = ()

    def __str__(self) -> str:
        if self.kind is TypeKind.LIST:
            return f"list[{self.element or ANY}]"
        if self.kind is TypeKind.MAP:
            return f"map[{self.key or ANY}, {self.value or ANY}]"
        if self.kind is TypeKind.OPTIONAL:
            return f"{self.element or ANY}?"
        if self.kind is TypeKind.RESULT:
            return f"Hasil[{self.success or ANY}, {self.error or ANY}]"
        if self.kind is TypeKind.STRUCT:
            return self.name or "struct"
        if self.kind is TypeKind.ENUM:
            return self.name or "enum"
        return self.kind.value


ANY = Type(TypeKind.ANY)
VOID = Type(TypeKind.VOID)
NULL = Type(TypeKind.NULL)
BOOL = Type(TypeKind.BOOL)
INT = Type(TypeKind.INT)
FLOAT = Type(TypeKind.FLOAT)
STRING = Type(TypeKind.STRING)


def list_of(element: Type = ANY) -> Type:
    return Type(TypeKind.LIST, element=element)


def map_of(key: Type = ANY, value: Type = ANY) -> Type:
    return Type(TypeKind.MAP, key=key, value=value)


def optional_of(inner: Type = ANY) -> Type:
    """Describe a value that may be absent; this is type-model support only."""
    return Type(TypeKind.OPTIONAL, element=inner)


def result_of(success: Type = ANY, error: Type = ANY) -> Type:
    """Describe an explicit success/error result type."""
    return Type(TypeKind.RESULT, success=success, error=error)


def struct_of(name: str, fields: dict[str, Type] | tuple[tuple[str, Type], ...]) -> Type:
    """Create a nominal named-record type with deterministic field order."""
    if not isinstance(name, str) or not name.isidentifier():
        raise ValueError("nama tipe struktur harus berupa identifier")
    entries = tuple(fields.items()) if isinstance(fields, dict) else tuple(fields)
    names = [field_name for field_name, _ in entries]
    if any(not isinstance(field_name, str) or not field_name.isidentifier() for field_name in names):
        raise ValueError("nama field struktur harus berupa identifier")
    if len(names) != len(set(names)):
        raise ValueError("nama field struktur tidak boleh duplikat")
    if any(not isinstance(field_type, Type) for _, field_type in entries):
        raise TypeError("tipe setiap field struktur harus berupa Type")
    return Type(TypeKind.STRUCT, name=name, fields=entries)


def enum_of(name: str, variants: tuple[str, ...] | list[str]) -> Type:
    """Create a nominal enum type and validate its variant names."""
    if not isinstance(name, str) or not name.isidentifier():
        raise ValueError("nama enum harus berupa identifier")
    values = tuple(variants)
    if not values or any(not isinstance(item, str) or not item.isidentifier() for item in values):
        raise ValueError("enum membutuhkan nama varian yang valid")
    if len(values) != len(set(values)):
        raise ValueError("varian enum tidak boleh duplikat")
    return Type(TypeKind.ENUM, name=name, variants=values)


def infer_type(value: Any) -> Type:
    """Infer the narrowest supported type for a runtime literal."""
    if value is None:
        return NULL
    if isinstance(value, bool):
        return BOOL
    if isinstance(value, int):
        return INT
    if isinstance(value, float):
        return FLOAT
    if isinstance(value, str):
        return STRING
    if isinstance(value, list):
        item_types = [infer_type(item) for item in value]
        element = item_types[0] if item_types and all(t == item_types[0] for t in item_types) else ANY
        return list_of(element)
    if isinstance(value, dict):
        key_types = [infer_type(item) for item in value]
        value_types = [infer_type(item) for item in value.values()]
        key_type = key_types[0] if key_types and all(t == key_types[0] for t in key_types) else ANY
        value_type = value_types[0] if value_types and all(t == value_types[0] for t in value_types) else ANY
        return map_of(key_type, value_type)
    return ANY


def is_assignable(target: Type, source: Type) -> bool:
    """Return whether a source value can be assigned to a target type."""
    if target.kind is TypeKind.ANY or source.kind is TypeKind.ANY:
        return True
    if target == source:
        return True
    if target.kind is TypeKind.OPTIONAL:
        inner = target.element or ANY
        if source.kind is TypeKind.NULL:
            return True
        if source.kind is TypeKind.OPTIONAL:
            return is_assignable(inner, source.element or ANY)
        return is_assignable(inner, source)
    if source.kind is TypeKind.OPTIONAL:
        return False
    if target.kind is TypeKind.RESULT and source.kind is TypeKind.RESULT:
        return is_assignable(target.success or ANY, source.success or ANY) and is_assignable(
            target.error or ANY, source.error or ANY
        )
    if target.kind in (TypeKind.STRUCT, TypeKind.ENUM):
        return target == source
    if target.kind is TypeKind.FLOAT and source.kind is TypeKind.INT:
        return True
    if target.kind is TypeKind.LIST and source.kind is TypeKind.LIST:
        return is_assignable(target.element or ANY, source.element or ANY)
    if target.kind is TypeKind.MAP and source.kind is TypeKind.MAP:
        return (
            is_assignable(target.key or ANY, source.key or ANY)
            and is_assignable(target.value or ANY, source.value or ANY)
        )
    return False


def common_type(left: Type, right: Type) -> Type:
    """Find a safe common type for expressions such as conditional branches."""
    if left == right:
        return left
    if left.kind is TypeKind.ANY or right.kind is TypeKind.ANY:
        return ANY
    if left.kind is TypeKind.NULL and right.kind is TypeKind.OPTIONAL:
        return right
    if right.kind is TypeKind.NULL and left.kind is TypeKind.OPTIONAL:
        return left
    if left.kind is TypeKind.OPTIONAL or right.kind is TypeKind.OPTIONAL:
        left_inner = left.element if left.kind is TypeKind.OPTIONAL else left
        right_inner = right.element if right.kind is TypeKind.OPTIONAL else right
        return optional_of(common_type(left_inner or ANY, right_inner or ANY))
    if left.kind is TypeKind.RESULT and right.kind is TypeKind.RESULT and left.name == right.name:
        return result_of(
            common_type(left.success or ANY, right.success or ANY),
            common_type(left.error or ANY, right.error or ANY),
        )
    if left.kind in (TypeKind.STRUCT, TypeKind.ENUM) or right.kind in (TypeKind.STRUCT, TypeKind.ENUM):
        return ANY
    if {left.kind, right.kind} == {TypeKind.INT, TypeKind.FLOAT}:
        return FLOAT
    if left.kind is TypeKind.LIST and right.kind is TypeKind.LIST:
        return list_of(common_type(left.element or ANY, right.element or ANY))
    if left.kind is TypeKind.MAP and right.kind is TypeKind.MAP:
        return map_of(
            common_type(left.key or ANY, right.key or ANY),
            common_type(left.value or ANY, right.value or ANY),
        )
    return ANY
