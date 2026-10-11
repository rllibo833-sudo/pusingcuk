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


@dataclass(frozen=True)
class Type:
    kind: TypeKind
    element: "Type | None" = None
    key: "Type | None" = None
    value: "Type | None" = None

    def __str__(self) -> str:
        if self.kind is TypeKind.LIST:
            return f"list[{self.element or ANY}]"
        if self.kind is TypeKind.MAP:
            return f"map[{self.key or ANY}, {self.value or ANY}]"
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
